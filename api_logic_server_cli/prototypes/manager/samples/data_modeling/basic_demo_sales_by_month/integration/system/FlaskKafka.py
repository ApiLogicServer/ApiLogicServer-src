import signal
import threading, time
import logging
import sys
import signal
try:
    from confluent_kafka import Producer, KafkaException, Consumer
except ImportError:
    Producer = None
    KafkaException = None
    Consumer = None
    # Kafka support not available on this platform

####
# adapted from and thanks to: https://pypi.org/project/flask-kafka
####

logger = logging.getLogger('integration.kafka')
__version__ = "1.01"

class FlaskKafka():
    def __init__(self, interrupt_event: object, conf: dict, safrs_api: object, **kw):
        self.consumer = None  # create consumer KafkaConsumer(**kw)
        self.handlers={}
        self.interrupt_event = interrupt_event
        self.conf = conf
        self.safrs_api = safrs_api


    def _add_handler(self, topic, handler):
        if self.handlers.get(topic) is None:
            self.handlers[topic] = []
        logger.debug(f"FlaskKafka._add_handler - topic: {topic}, handler: {handler}")
        self.handlers[topic].append(handler)

    def handle(self, topic):
        """Annotation to identify handler for topic

        Args:
            topic (str): name of topic
        """
        def decorator(f):
            self._add_handler(topic, f)
            return f
        return decorator

    def _run_handlers(self, msg):
        try:
            handlers = self.handlers[msg.topic()]
            for handler in handlers:
                handler(msg = msg, safrs_api = self.safrs_api)
            # self.consumer.commit(asynchronous=False)
            # DEV/DEMO: commit is intentionally disabled (enable.auto.commit=false in config).
            # Effect: offsets are never committed, so server restart replays all messages from earliest.
            # The is_processed guard on Consumer 2 makes replays a safe no-op (skips already-processed blobs).
            # PRODUCTION: uncomment the commit line above for at-least-once delivery with no replays.
        except Exception as e:
            logger.critical(str(e), exc_info=1)
            # self.consumer.close()
            sys.exit("Exited due to exception")

    def signal_term_handler(self, signal, frame):
        logger.info("closing consumer")
        self.consumer.close()
        sys.exit(0)


    def _start(self):
        """ thread target (from _run) """

        # thanks: https://www.reddit.com/r/learnpython/comments/gfg97m/how_do_i_run_a_function_every_5_seconds_inside_a/

        topics = self.handlers.keys()
        logger.info(f" - FlaskKafka._start: begin polling (v {__version__}), with \n -- conf: {self.conf} \n -- topics: {topics}")
        try:
            consumer = Consumer(self.conf)
            consumer.subscribe(topics=list(topics))
        except Exception as e:
            logger.critical(f"FlaskKafka._start: Consumer init/subscribe failed: {e}", exc_info=True)
            return
        while True and len(topics) > 0:
            if self.interrupt_event.is_set():
                logger.info("Kafka thread interrupted")
                break
    
            msg = consumer.poll(1.0)
            logger.debug(f' - KafkaConnect._start - consuming consumer.poll(1.0): {msg}') if msg else None
            if msg is None:
                continue
            if msg.error():
                logger.warning(f" - FlaskKafka: msg.error() on topic {msg.topic()}: {msg.error()}")
            else:
                self._run_handlers(msg)  # accrued per annotations


    def listen_kill_server(self):
        signal.signal(signal.SIGTERM, self.interrupted_process)
        signal.signal(signal.SIGINT, self.interrupted_process)
        signal.signal(signal.SIGQUIT, self.interrupted_process)
        signal.signal(signal.SIGHUP, self.interrupted_process)
            
    def interrupted_process(self, *args):
        logger.info("closing consumer")
        self.consumer.close()
        sys.exit(0)

    
    def _run(self):
        logger.info(" * The flask Kafka thread started")
        t = threading.Thread(target=self._start)
        t.start()


    # run the consumer application
    def run(self):
        """
        Kafka consumption, threading, handler annotations
        """
        self._run()
