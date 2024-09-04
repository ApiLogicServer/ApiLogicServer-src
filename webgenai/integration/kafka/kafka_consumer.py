"""
Invoked at server start (api_logic_server_run.py)

Listen/consume Kafka topis, if KAFKA_CONSUMER specified in Config.py

Alter this file to add handlers for consuming kafka topics
"""

from config.config import Args
from confluent_kafka import Producer, KafkaException, Consumer
import signal
import logging
import json
import socket
import safrs
from threading import Event
from integration.system.FlaskKafka import FlaskKafka


conf = None

logger = logging.getLogger('integration.kafka')
logger.debug("kafka_consumer imported")


def kafka_consumer(safrs_api: safrs.SAFRSAPI = None):
    """
    Called by api_logic_server_run to listen on kafka

    Enabled by config.KAFKA_CONSUMER

    Args:
        app (safrs.SAFRSAPI): safrs_api
    """

    if not Args.instance.kafka_consumer:
        logger.debug(f'Kafka Consumer not activated')
        return

    conf = Args.instance.kafka_consumer
    #  eg, KAFKA_CONSUMER = '{"bootstrap.servers": "localhost:9092", "group.id": "als-default-group1"}'
    logger.debug(f'\nKafka Consumer configured, starting')

    INTERRUPT_EVENT = Event()

    bus = FlaskKafka(interrupt_event=INTERRUPT_EVENT, conf=conf, safrs_api=safrs_api)
    
    bus.run()  # Kafka consumption, threading, handler annotations

    logger.debug(f'Kafka Listener thread activated {bus}')

    '''   Your Code Goes Here
    
    Define topic handlers here, e.g.

    @bus.handle('order_shipping')
    def order_shipping(msg: object, safrs_api: safrs.SAFRSAPI):

    '''

