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
__version__ = "1.02"   # 1.02 (Nov 2026): commits offsets after each message (APILOGICPROJECT_KAFKA_COMMIT_OFFSETS, default true)


def commit_offsets_enabled() -> bool:
    """ APILOGICPROJECT_KAFKA_COMMIT_OFFSETS: true / 1 / yes / on (the default), else false.  Not `if os.getenv(...)`:
    the string "false" is truthy. """
    import os
    return os.getenv("APILOGICPROJECT_KAFKA_COMMIT_OFFSETS", "true").strip().lower() in ("true", "1", "yes", "on")

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
        except Exception as e:
            # Log and carry on with the next message.  (This used to sys.exit, which ended the consumer thread:
            # one failed message silently stopped all later processing.)  Handlers record their own failures
            # (e.g. error_text on the blob row), so a failed message is not retried by replaying it.
            logger.critical(f"FlaskKafka: a handler failed on topic {msg.topic()}; the message is skipped: {e}", exc_info=1)
        finally:
            self._commit(msg)

    def _commit(self, msg):
        """ Commit the message's offset, so a server restart resumes AFTER it (no replay).

        APILOGICPROJECT_KAFKA_COMMIT_OFFSETS (default true).  Set it to false only to replay every message on each
        start, e.g. to re-run a pipeline by hand: replays re-insert every message (Consumer 1 saves a new blob row
        each time), so they create duplicate rows - never use false in production.
        """
        if not commit_offsets_enabled():
            return
        try:
            self.consumer.commit(message=msg, asynchronous=False)
        except Exception as e:
            logger.error(f"FlaskKafka: could not commit offset for topic {msg.topic()}: {e}")

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
            self.consumer = consumer   # used by _commit (and close on shutdown)
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
