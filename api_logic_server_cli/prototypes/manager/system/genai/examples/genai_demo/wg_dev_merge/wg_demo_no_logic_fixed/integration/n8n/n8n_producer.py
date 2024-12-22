"""

Version 1.1

Invoked at server start (api_logic_server_run.py -> config/setup.py)

Connect to n8n, if N8N_CONNECT specified in Config.py

You do not normally need to alter this file

"""
import traceback
import requests
from config.config import Args
import json
import logging
from logic_bank.exec_row_logic.logic_row import LogicRow
from integration.system.RowDictMapper import RowDictMapper
from flask import jsonify
import api.system.api_utils as api_utils
from config.config import Args

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
        logger.debug('N8N producer initialized')


def send_n8n_message(http_method: str = "POST", ins_upd_dlt: str = "ins", msg: str = "",
        wh_entity: str = "unknown",
        logic_row: LogicRow = None, 
        row_dict_mapper: RowDictMapper = None, 
        payload: dict = None) -> any:
    """ Send N8N webhook message regarding [logic_row, mapped by row_dict_mapper or by  payload]

    * Typically called from declare_logic event

    Args:
        http_method (str):  [GET, POST,PUT,PATCH, DELETE] default is POST
        ins_upd_dlt (str): "ins, upd, dlt" (logic row state) logic_row.ins_upd_dlt or manual (wh_state pass in header)
        logic_row (LogicRow):(Optional) logic row contains row, old_row, ins_upd_dlt and more
        msg: this is used for debugging
        row_dict_mapper (RowDictMapper): (Optional) typically subclass of RowDictMapper, transforms row to dict
        payload (str): (Optional) JSON data to be sent as string (json.dumps(row.to_dict()))    
        wh_entity (str): the webhook entity name pass in header
    """

    global conf
    if conf is None:
        conf = Args.instance.n8n_producer #FIXME not sure why this fails - conf is None
        #return "N8N not enabled in Config.py"
        
    if row_dict_mapper is None and payload is None and logic_row is None:
        return "send_n8n_message: payload, logic_row, row_dict_mapper are all None - must provide one"
    row_obj_dict = None
    if isinstance(payload, dict):
        row_obj_dict = json.dumps(payload)
    elif logic_row is not None:
        row_obj_dict = json.dumps(logic_row.row.to_dict())
    elif row_dict_mapper is not None:
        row_obj_dict = row_dict_mapper().row_to_dict(row = logic_row.row)
    elif row_dict_mapper is None:
        row_obj_dict = RowDictMapper(model_class=logic_row.row.__class__).row_to_dict(row = logic_row.row)
    elif payload is None and http_method.lower() == "post":
        raise ValueError(f"send_n8n_message payload type not supported: {type(payload)}") 

    wh_state =  ins_upd_dlt if logic_row is None else logic_row.ins_upd_dlt
    wh_entity = logic_row.row.__class__.__name__ if logic_row else wh_entity
    try:
        if row_obj_dict is not None:
            json_payload = jsonify(f'{row_obj_dict}').data.decode('utf-8')
            msg = f"Webhook send_n8n_message: http_method: {http_method} wh_state: {wh_state} wh_entity: {wh_entity}"
            logger.debug(f'\n\n{msg}\n{json_payload}')
        
        status = {"status_code": 500}

        if conf is None:
            logger.debug(f"n8n_producer: not configured in config/Config.py")
        else:
            headers = {
                "Authorization": conf['authorization'],
                "Content-Type": "application/json",
                "wh_state": wh_state,
                "wh_entity": wh_entity
            }
            endpoint = f'{conf["n8n_url"]}'
            status = {"status_code": 500}
            if http_method in {"post", "POST"}:
                #Only passing payload in this example
                status = requests.post(endpoint, json=row_obj_dict, headers=headers)
            elif http_method.lower() == "get":
                status = requests.get(endpoint, headers=headers)
            elif http_method.lower() in {"put", "patch", "delete"}:
                logger.error(f"n8n_producer: http_method: {http_method} not implemented")

            if status and status.status_code != 200:
                logger.error(f"n8n_producer: status_code: {status.status_code}")
        return status
    except Exception as e:
        logger.error(f"\nn8n_producer fails with: {e}")
        long_message = traceback.format_exc()
        logger.error(long_message)
        return long_message

