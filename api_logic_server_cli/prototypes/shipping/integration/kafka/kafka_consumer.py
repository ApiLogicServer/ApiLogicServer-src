"""

Invoked at server start (api_logic_server_run.py)

Connect to Kafka, if KAFKA_CONNECT specified in Config.py

"""
from config import Args
from confluent_kafka import Producer, KafkaException, Consumer
import signal
import logging
import json
import socket
from flask import Flask, redirect, send_from_directory, send_file
from threading import Event
from integration.system.FlaskKafka import FlaskKafka


conf = None

logger = logging.getLogger('integration.kafka')
logger.debug("kafka_producer imported")
pass


def kafka_consumer(flask_app: Flask):
    """
    Called by api_logic_server_run to listen on kafka

    Enabled by config.KAFKA_LISTEN

    Args:
        app (Flask): flask_app
    """

    if not Args.instance.kafka_consumer:
        logger.debug(f'Kafka Consumer not activated')
        return

    conf = Args.instance.kafka_consumer
    # conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
    logger.debug(f'\nKafka producer configured')

    
    if "client.id" not in conf:
        conf["client.id"] = socket.gethostname()
    # conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
    logger.debug(f'\nKafka producer starting')


    INTERRUPT_EVENT = Event()

    bus = FlaskKafka(INTERRUPT_EVENT, conf)
    
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
    from_article = False  # this blocks server from starting
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


