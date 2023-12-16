"""
Invoked at server start (api_logic_server_run.py)

Listen/consume Kafka topis, if KAFKA_CONSUMER specified in Config.py

Add handlers for consuming kafka topics
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
    logger.debug(f'\nKafka producer configured')

    if "client.id" not in conf:
        conf["client.id"] = socket.gethostname()

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

"""
create annotated handlers to consume kafka topics        

    @bus.handle('order_shipping')
    def test_topic_handler(msg):
        print("consumed {} from order_shipping topic consumer".format(msg))
        pass  # save message content as desired
"""