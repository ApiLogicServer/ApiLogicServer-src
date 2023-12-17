import signal
import threading, time
import traceback
import json
import logging
import sys
import signal
from confluent_kafka import Producer, KafkaException, Consumer

####
# adapted from and thanks to: https://pypi.org/project/flask-kafka
####

logger = logging.getLogger('integration.kafka')

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
        logger.info("starting consumer...registered signterm")

        logger.info(" - KafkaConnect._start: begin polling")
        consumer = Consumer(self.conf)
        use_decorator = True  # working 9.06.06
        if use_decorator:
            topics = self.handlers.keys()
            consumer.subscribe(topics=list(topics))  # restart often corrects "Failed to set subscription"
        else:
            consumer.subscribe(["order_shipping"])
        while True:
            msg = consumer.poll(1.0)
            logger.debug(f'consumer.poll gets: {msg}')
            if msg is None:
                continue
            if msg.error():
                pass  # Handle errors as needed pass
            else:
                if use_decorator:
                    self._run_handlers(msg)
                else:
                    message_data = msg.value() .decode("utf-8")
                    # Assuming the JSON message has a 'message_id' and 'message data' f
                    json_message = json.loads(message_data)
                    message_id = json_message.get('message_id')
                    message_data = json_message.get( 'message_data' )
                    # Create a new KafkaMessage instance and persist it to the database
                    print(f'Received and persisted message with ID: (message_data)')



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
        logger.info(" * The flask Kafka application is consuming")
        t = threading.Thread(target=self._start)
        t.start()


    # run the consumer application
    def run(self):
        self._run()
