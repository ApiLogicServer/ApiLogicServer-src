"""

Invoked at server start (api_logic_server_run.py)

Connect to Kafka, if KAFKA_CONNECT specified in Config.py

"""
from config import Args
from confluent_kafka import Producer, KafkaException, Consumer
import socket
import logging
import json
from flask import Flask, redirect, send_from_directory, send_file
from threading import Event
import signal
import threading, time
import traceback
import logging
import sys
import signal
# from integration.system.FlaskKafka import FlaskKafka

producer = None
""" connected producer (or null if Kafka not enabled in Config.py) """

conf = None

logger = logging.getLogger(__name__)
logger.debug("kafka_connect imported")
pass

class FlaskKafka():
    def __init__(self, interrupt_event, **kw):
        self.consumer = None  # create consumer KafkaConsumer(**kw)
        self.handlers={}
        self.interrupt_event = interrupt_event
        '''
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.setLevel(logging.INFO)
        logger = logger
        '''


    def _add_handler(self, topic, handler):
        if self.handlers.get(topic) is None:
            self.handlers[topic] = []
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
            handlers = self.handlers[msg.topic]
            for handler in handlers:
                handler(msg)
            self.consumer.commit()
        except Exception as e:
            logger.critical(str(e), exc_info=1)
            self.consumer.close()
            sys.exit("Exited due to exception")

    def signal_term_handler(self, signal, frame):
        logger.info("closing consumer")
        self.consumer.close()
        sys.exit(0)


    def _start(self):
        """ thread target (from _run) """

        # thanks: https://www.reddit.com/r/learnpython/comments/gfg97m/how_do_i_run_a_function_every_5_seconds_inside_a/
        logger.info("starting consumer...registered signterm")
        while True:
            logger.info("wakeup")
            time.sleep(5)

        do_consume = False
        if do_consume:
            self.consumer.subscribe(topics=tuple(self.handlers.keys()))

            for msg in self.consumer:
                logger.debug("TOPIC: {}, PAYLOAD: {}".format(msg.topic, msg.value))
                self._run_handlers(msg)
                # stop the consumer
                if self.interrupt_event.is_set():
                    self.interrupted_process()
                    self.interrupt_event.clear()

            
    def interrupted_process(self, *args):
        logger.info("closing consumer")
        self.consumer.close()
        sys.exit(0)

    
    def _run(self):
        logger.info(" * The flask Kafka application is consuming")
        t = threading.Thread(target=self._start)
        t.start()


    # run the consumer application
    def run(self):
        self._run()



def kafka_connect():
    """
    Called by api_logic_server_run to listen on kafka using confluent_kafka

    Enabled by config.KAFKA_CONNECT (dict, of bootstrap.servers, client.id)

    Args:
        app (Flask): flask_app
    """

    global producer, conf
    if Args.instance.kafka_connect:
        conf = Args.instance.kafka_connect
        if "client.id" not in conf:
            conf["client.id"] = socket.gethostname()
        if "group.id" not in conf:
            conf["group.id"] = 'als-default-group'
        # conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
        producer = Producer(conf)
        logger.debug(f'\nKafka producer connected')


def kafka_listen(app: Flask):
    """
    Called by api_logic_server_run to listen on kafka

    Enabled by config.KAFKA_LISTEN

    Args:
        app (Flask): flask_app
    """

    if not Args.instance.kafka_listen:
        logger.debug(f'Kafka Listener not activated')
        return
    
    global conf
    
    # consumer : Consumer = Consumer()

    # thanks: https://pypi.org/project/flask-kafka

    INTERRUPT_EVENT = Event()

    bus = FlaskKafka(INTERRUPT_EVENT,
                    bootstrap_servers=None,  # bootstrap_servers=",".join(["localhost:9092"]),
                    group_id=None                        # group_id="consumer-grp-id"
                    )
    
    bus.run()

    logger.debug(f'Kafka Listener activated {bus}')

    def listen_kill_server():
        signal.signal(signal.SIGTERM, bus.interrupted_process)
        signal.signal(signal.SIGINT, bus.interrupted_process)
        signal.signal(signal.SIGQUIT, bus.interrupted_process)
        signal.signal(signal.SIGHUP, bus.interrupted_process)


    @bus.handle('order_shipping')
    def test_topic_handler(msg):
        print("consumed {} from order_shipping topic consumer".format(msg))
        pass

    # thanks:  https://dzone.com/articles/event-streaming-ai-amp-automation
    from_article = False   # blocks server start
    if from_article:
        consumer = Consumer(conf)
        while True:
            msg = consumer.poll(1.0)
            logger.debug(f'consumer.poll gets: {msg}')
            if msg is None:
                continue
            if msg.error():
                pass  # Handle errors as needed pass
            else:
                message_data = msg.value() .decode("utf-8")
                # Assuming the JSON message has a 'message_id' and 'message data' f
                json_message = json.loads(message_data)
                message_id = json_message.get('message_id')
                message_data = json_message.get( 'message_data' )
                # Create a new KafkaMessage instance and persist it to the database
                print(f'Received and persisted message with ID: (message_id)')


