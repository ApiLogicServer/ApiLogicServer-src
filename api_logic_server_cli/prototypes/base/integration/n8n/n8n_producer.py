"""

Version 1.0

Invoked at server start (api_logic_server_run.py -> config/setup.py)

Connect to n8n, if N8N_CONNECT specified in Config.py

You do not normally need to alter this file

"""
import traceback
import requests
from config.config import Args

import socket
import logging
from logic_bank.exec_row_logic.logic_row import LogicRow
from integration.system.RowDictMapper import RowDictMapper
from flask import jsonify
import api.system.api_utils as api_utils

producer = None
""" connected producer (or null if N8N not enabled in Config.py) """

conf = None
""" filled from config (N8N_CONNECT) """

logger = logging.getLogger('integration.n8n')
logger.debug("n8n_connect imported")

def n8n_producer():
    """
    Called by api_logic_server_run>server_setup to listen on kafka using confluent_kafka

    Enabled by config.KAFKA_CONNECT (dict, of bootstrap.servers, client.id)

    Args:
        none
    """

    global conf
    if Args.instance.n8n_producer:
        conf = Args.instance.n8n_producer
        producer = conf
        # good place to do defaults, get api keys, etc
        logger.debug(f'N8N producer initialized')


def send_n8n_message(kafka_topic: str, n8n_key: str, msg: str="", json_root_name: str = "", 
                       logic_row: LogicRow = None, row_dict_mapper: RowDictMapper = None, payload: dict = None):
    """ Send N8N message regarding logic_row, mapped by row_dict_mapper

    * Typically called from declare_logic event

    Args:
        logic_row (LogicRow): root data to be sent
        row_dict_mapper (RowDictMapper): typically subclass of RowDictMapper, transforms row to dict
        kafka_topic (str): the kafka topic
        kafka_key (str): the kafka key
        msg (str, optional): string to log
        json_root_name (str, optional): json name for json payload root; default is logic_row.name
    """

    global conf

    if isinstance(payload, dict):
        row_obj_dict = payload
    elif row_dict_mapper is not None:
        row_obj_dict = row_dict_mapper().row_to_dict(row = logic_row.row)
    elif row_dict_mapper is None:
        row_obj_dict = RowDictMapper(model_class=logic_row.row.__class__).row_to_dict(row = logic_row.row)
    else:
        raise ValueError(f"send_n8n_message payload type not supported: {type(payload)}") 

    root_name = json_root_name
    if root_name == "":
        if logic_row is None:
            root_name = 'Payload'
        else:
            root_name = logic_row.name

    json_payload = jsonify({f'{root_name}': row_obj_dict}).data.decode('utf-8')
    log_msg = msg + ' sends:'

    if logic_row:
        logic_row.log(msg)
    logger.debug(f'\n\n{log_msg}\n{json_payload}')

    token = "YWRtaW46cA=="  # admin:p base64 encoded
    headers = {
        "Authorization": conf['authorization'],
        "Content-Type": "application/json",
        "wh_state": logic_row.ins_upd_dlt
    }
    try:
        endpoint = 'fixme'
        status = requests.post(f'http://{conf["server"]}:{conf["port"]}/{endpoint}/{n8n_key}/:{n8n_key}', 
                                json=json_payload, headers=headers)
        if status.status_code != 200:
            raise(f"n8n_producer: status_code: {status.status_code}")
    except Exception as e:
        logger.error(f"\nn8n_producer fails with: {e}")
        long_message = traceback.format_exc()

