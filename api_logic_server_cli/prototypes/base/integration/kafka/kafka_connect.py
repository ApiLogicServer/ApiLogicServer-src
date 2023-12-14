"""

Invoked at server start (api_logic_server_run.py)

Connect to Kafka, if KAFKA_CONNECT specified in Config.py

"""
from config import Args
from confluent_kafka import Producer, KafkaException
import socket

producer = None
""" connected producer (or null if Kafka not enabled in Config.py) """

def kafka_connect():
    global producer
    if Args.instance.kafka_connect:
        conf = Args.instance.kafka_connect
        if "client.id" not in conf:
            conf["client.id"] = socket.gethostname()
        # conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
        producer = Producer(conf)

