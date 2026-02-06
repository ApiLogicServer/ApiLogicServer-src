"""
App Integration Use Case - Business Logic Rules

Natural Language Requirements:
1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.

version: 1.0
date: February 5, 2026
source: docs/training/logic_bank_api.md
"""

from logic_bank.logic_bank import Rule
from database import models
from integration.kafka import kafka_producer


def declare_logic():
    """Business logic rules for App Integration use case."""
    
    # Rule 1: Send Order to Kafka when shipped
    Rule.after_flush_row_event(
        on_class=models.Order,
        calling=kafka_producer.send_row_to_kafka,
        if_condition=lambda row: row.date_shipped is not None,
        with_args={"topic": "order_shipping"}
    )
