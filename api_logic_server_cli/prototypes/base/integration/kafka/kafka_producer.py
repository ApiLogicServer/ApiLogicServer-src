"""

Invoked at server start (api_logic_server_run.py)

Connect to Kafka, if KAFKA_CONNECT specified in Config.py

You do not normally need to alter this file

"""
from config.config import Args
from confluent_kafka import Producer
import socket
import logging


producer = None
""" connected producer (or null if Kafka not enabled in Config.py) """

conf = None
""" filled from config (KAFKA_CONNECT) """

logger = logging.getLogger('integration.kafka')
logger.debug("kafka_connect imported")

def kafka_producer():
    """
    Called by api_logic_server_run to listen on kafka using confluent_kafka

    Enabled by config.KAFKA_CONNECT (dict, of bootstrap.servers, client.id)

    Args:
        none
    """

    global producer, conf
    if Args.instance.kafka_producer:
        conf = Args.instance.kafka_producer
        if "client.id" not in conf:
            conf["client.id"] = socket.gethostname()
        # conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
        producer = Producer(conf)
        logger.debug(f'\nKafka producer connected')

