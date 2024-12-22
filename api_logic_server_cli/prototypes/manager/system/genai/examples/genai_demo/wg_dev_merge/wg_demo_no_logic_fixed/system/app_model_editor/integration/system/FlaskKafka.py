import signal
import threading, time
import logging
import sys
import signal
from confluent_kafka import Producer, KafkaException, Consumer

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
            # self.consumer.commit()
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
        consumer = Consumer(self.conf)
        consumer.subscribe(topics=list(topics))
        while True:
            msg = consumer.poll(1.0)
            logger.debug(f' - KafkaConnect._start - consuming consumer.poll(1.0): {msg}')
            if msg is None:
                continue
            if msg.error():
                pass  # Handle errors as needed
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
