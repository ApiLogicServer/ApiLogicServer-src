import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database.models import *
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging
import requests
import traceback
from flask import jsonify
import json
from integration.row_dict_maps.Customer_Orders import Customer_Orders
from confluent_kafka import Producer, KafkaException
import integration.kafka.kafka_producer as kafka_producer
import integration.n8n.n8n_producer as n8n_producer
from config.config import Config


""" Examples for integrating Kafka, n8n Webhooks, etc. """

app_logger = logging.getLogger(__name__)

# Configuration for Webhook
wh_server = "localhost"
wh_port = 5678
wh_endpoint = "webhook-test"
wh_key = "1c83eb31-18b7-4505-9cd2-b6722cb8bb86"

def declare_logic():
    
    def fn_workflow(row: Customer, old_row: Customer, logic_row: LogicRow):
        """
        Workflow:  When Customer is inserted = post to external system
        """
        n8n_producer.send_n8n_message(logic_row=logic_row,
                                            kafka_topic="customer",
                                            n8n_key=str(row.Id),
                                            msg="1. /integration.py: n8n, sending logic_row")        

    Rule.after_flush_row_event(on_class=Customer, calling=fn_workflow)


    def send_kafka_customer_orders(row: Customer, old_row: Customer, logic_row: LogicRow):
        """ #als: Send Kafka message formatted by OrderShipping RowDictMapper

        See also:  send_kafka_message() in declare_logic.py.

        Args:
            row (Customer): inserted / changed Customer
            old_row (Customer): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
        """
        

        kafka_producer.send_kafka_message(logic_row=logic_row,
                                            kafka_topic="customer",
                                            kafka_key=str(row.Id),
                                            msg="1. /integration.py: Kafka, sending logic_row=logic_row")

        kafka_producer.send_kafka_message(payload={"customer_id": row.Id, "balance": row.Balance},
                                            kafka_topic="customer",
                                            kafka_key=str(row.Id),
                                            msg="2. logic_discovery/integration.py: Kafka, sending payload=<dict>")

        kafka_producer.send_kafka_message(logic_row=logic_row,
                                            row_dict_mapper=Customer_Orders,
                                            kafka_topic="customer",
                                            kafka_key=str(row.Id),
                                            msg="3. logic_discovery/integration.py: Kafka, sending with declarative mapping (row_dict_mapper=Customer_Orders)")
            
    Rule.after_flush_row_event(on_class=Customer, calling=send_kafka_customer_orders)  # see above
