import datetime
from decimal import Decimal
import integration.kafka.kafka_producer as kafka_producer
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import logging

app_logger = logging.getLogger(__name__)


def declare_logic():
    """
    App Integration Use Case Logic
    
    Natural Language Requirements:
    1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.
    """
    
    # 1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None
    Rule.after_flush_row_event(on_class=models.Order, calling=kafka_producer.send_row_to_kafka, 
                               if_condition=lambda row: row.date_shipped is not None, with_args={'topic': 'order_shipping'})
