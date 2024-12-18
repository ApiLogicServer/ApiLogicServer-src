"""

Version 1.1

Invoked at server start (api_logic_server_run.py -> config/setup.py)

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
import api.system.api_utils as api_utils

producer = None
""" connected producer (or null if Kafka not enabled in Config.py) """

conf = None
""" filled from config (KAFKA_CONNECT) """

logger = logging.getLogger('integration.n8n')
logger.debug("kafka_connect imported")

def kafka_producer():
    """
    Called by api_logic_server_run>server_setup to listen on kafka using confluent_kafka

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


def send_kafka_message(kafka_topic: str, kafka_key: str, msg: str="", json_root_name: str = "", 
                       logic_row: LogicRow = None, row_dict_mapper: RowDictMapper = None, payload: dict = None):
    """ Send Kafka message regarding logic_row, mapped by row_dict_mapper

    * Typically called from declare_logic event

    Args:
        logic_row (LogicRow): root data to be sent
        row_dict_mapper (RowDictMapper): typically subclass of RowDictMapper, transforms row to dict
        kafka_topic (str): the kafka topic
        kafka_key (str): the kafka key
        msg (str, optional): string to log
        json_root_name (str, optional): json name for json payload root; default is logic_row.name
    """


    if isinstance(payload, dict):
        row_obj_dict = payload
    elif row_dict_mapper is not None:
        row_obj_dict = row_dict_mapper().row_to_dict(row = logic_row.row)
    elif row_dict_mapper is None:
        row_obj_dict = RowDictMapper(model_class=logic_row.row.__class__).row_to_dict(row = logic_row.row)
    else:
        raise ValueError(f"send_kafka_message payload type not supported: {type(payload)}") 

    root_name = json_root_name
    if root_name == "":
        if logic_row is None:
            root_name = 'Payload'
        else:
            root_name = logic_row.name

    json_string = jsonify({f'{root_name}': row_obj_dict}).data.decode('utf-8')
    log_msg = msg + ' sends:'
    if producer:  # enabled in config/config.py?
        try:
            producer.produce(value=json_string, topic="order_shipping", key=kafka_key)
            if logic_row:
                logic_row.log(msg)
        except KafkaException as ke:
            logger.error("kafka_producer#send_kafka_message error: {ke}") 
    else:
        log_msg += "    [Note: **Kafka not enabled** ]"
    if logic_row is not None:
        logic_row.log(f'\n\n{log_msg}\n{json_string}')
    else:
        logger.debug(f'\n\n{log_msg}\n{json_string}')
