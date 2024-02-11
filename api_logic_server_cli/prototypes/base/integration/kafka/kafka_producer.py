"""

Invoked at server start (api_logic_server_run.py)

Connect to Kafka, if KAFKA_CONNECT specified in Config.py

You do not normally need to alter this file

"""
from config.config import Args
from confluent_kafka import Producer
import socket
import logging
from logic_bank.exec_row_logic.logic_row import LogicRow
from integration.system.RowDictMapper import RowDictMapper
from flask import jsonify
from confluent_kafka import Producer, KafkaException

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


def send_kafka_message(logic_row: LogicRow, row_dict_mapper: RowDictMapper, 
                       kafka_topic: str, kafka_key: str, msg: str=""):
    """ Send Kafka message regarding logic_row, mapped by row_dict_mapper

    * Typically called from declare_logic event

    Args:
        logic_row (LogicRow): root data to be sent
        row_dict_mapper (RowDictMapper): typically subclass of RowDictMapper, transforms row to dict
        kafka_topic (str): the kafka topic
        kafka_key (str): the kafka key
        msg (str, optional): string to log
    """
    row_obj_dict = row_dict_mapper().row_to_dict(row = logic_row.row)
    json_string = jsonify({f'{logic_row.name}': row_obj_dict}).data.decode('utf-8')
    if producer:  # enabled in config/config.py?
        try:
            producer.produce(value=json_string, topic="order_shipping", key=kafka_key)
            logic_row.log(msg)
        except KafkaException as ke:
            logic_row.log("kafka_producer#send_kafka_message error: {ke}") 
    logger.info(f'\n\n{msg} sends:\n{json_string}')
