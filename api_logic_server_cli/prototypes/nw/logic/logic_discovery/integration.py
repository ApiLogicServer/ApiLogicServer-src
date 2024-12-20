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
from integration.n8n.n8n_producer import send_n8n_message
from config.config import Config


""" Examples for integrating Kafka, n8n Webhooks, etc. """

app_logger = logging.getLogger(__name__)


# ###############################################################################
# important - only one after_flush_row_event per class
# ###############################################################################

def declare_logic():

    def fn_customer_workflow(row: Customer, old_row: Customer, logic_row: LogicRow):
        """ #als: Send N8N message 
        Webhook Workflow:  When Customer is inserted/updated - post n8n Webhook and call sendgrid email system

        Args:
            row (Customer): inserted / changed Customer
            old_row (Customer): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
         """
        
        if logic_row.is_inserted():
            send_n8n_message(logic_row=logic_row)



        """ #als: Send Kafka message - illustrate 3 alerting methods 
        See also:  send_kafka_message() in declare_logic.py.
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


    def fn_employee_workflow(row: Employee, old_row: Employee, logic_row: LogicRow):
        """
        Workflow:  When Employee is inserted = post n8n Webhook and call sendgrid email system
        """
        send_n8n_message(logic_row=logic_row,
                msg="1. /Webhook integration.py: n8n, sending Employee logic_row")        


    def fn_order_workflow(row: Order, old_row: Order, logic_row: LogicRow):
        """
        Workflow:  When Order is inserted = post n8n Webhook and call sendgrid email system
        """
        if logic_row.is_updated() and row.Ready == True and old_row.Ready == False:
            send_n8n_message(payload={
                                    "Order Id": row.Id, 
                                    "Customer Name": row.Customer.CompanyName, 
                                    "Order Total": str(row.AmountTotal),
                                    "Order Date": row.OrderDate,
                                    #"items": [row.OrderDetailList]
                                },
                ins_upd_dlt="upd", wh_entity="Order",
                msg="1. /Webhook integration.py: n8n, sending ready Order payload")        


    Rule.after_flush_row_event(on_class=Customer, calling=fn_customer_workflow)
    Rule.after_flush_row_event(on_class=Employee, calling=fn_employee_workflow)


