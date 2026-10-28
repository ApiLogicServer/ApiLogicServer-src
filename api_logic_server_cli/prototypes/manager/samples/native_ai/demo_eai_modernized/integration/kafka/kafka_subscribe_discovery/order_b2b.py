"""
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b
       reads message, inserts raw payload into OrderB2bMessage blob (Tx 1)
  2. logic/logic_discovery/order_b2b_consume.py
       insert -> publishes payload to topic: order_b2b_processed
  3. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b_processed
       parses payload -> domain rows (lookups + LogicBank rules) (Tx 2)
  4. api/api_discovery/order_b2b_kafka_consume_debug.py
       /consume_debug/order_b2b bypasses Kafka, calls same parse function directly

Debug test (no Kafka required):
  curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json&mode=simulated"

Enable live Kafka in config/default.env:
  KAFKA_SERVER = localhost:9092
  KAFKA_CONSUMER_GROUP = demo_eai_modernized-group1
  Reset topics before starting server: bash integration/kafka/order_b2b_reset.sh
"""

import json
import logging
import safrs
from database import models
from integration.system.EaiSubscribeMapper import resolve_lookups, record_error_text

logger = logging.getLogger('integration.kafka')

ORDER_B2B_PARENT_LOOKUPS = [
    (models.Customer, models.Customer.name, 'Account', 'customer_id'),
]

ORDER_B2B_CHILD_LOOKUPS = [
    (models.Product, models.Product.name, 'Name', 'product_id'),
]

ORDER_B2B_CHILD_KEY = 'Items'


def process_order_b2b_payload(payload: str, session, blob_id: int = None):
    """Kafka subscribe order_b2b: parses payload, resolves Customer and Product lookups, persists Order and Items, and marks OrderB2bMessage processed."""
    from integration.OrderB2bMapper import parse
    raw = json.loads(payload)
    parent_row, detail_rows = parse(payload)
    if detail_rows and not hasattr(detail_rows[0], '__tablename__'):
        raise TypeError(f"parse() must return list[model_instance]; got {type(detail_rows[0]).__name__} — check OrderB2bMapper.parse() return value")
    resolve_lookups(parent_row, raw, ORDER_B2B_PARENT_LOOKUPS, session)
    for child_row, child_src in zip(detail_rows, raw.get(ORDER_B2B_CHILD_KEY, [])):
        resolve_lookups(child_row, child_src, ORDER_B2B_CHILD_LOOKUPS, session)
        parent_row.ItemList.append(child_row)
    session.add(parent_row)
    if blob_id:
        blob = session.get(models.OrderB2bMessage, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.OrderB2bMessage(payload=payload, is_processed=True)
        session.add(blob)
    session.commit()
    return parent_row, blob


def register(bus):
    """Kafka subscribe order_b2b: registers Consumer 1 (order_b2b) and Consumer 2 (order_b2b_processed) on the Kafka bus."""

    @bus.handle('order_b2b')
    def order_b2b(msg, safrs_api):
        """Kafka subscribe order_b2b: Consumer 1 saves the raw payload into OrderB2bMessage (Tx 1) so the row_event bridge publishes to order_b2b_processed."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.OrderB2bMessage(payload=msg.value().decode('utf-8'), is_processed=False)
            session.add(blob)
            session.commit()

    @bus.handle('order_b2b_processed')
    def order_b2b_processed(msg, safrs_api):
        """Kafka subscribe order_b2b: Consumer 2 parses the payload, persists Order and Item rows, and marks OrderB2bMessage processed (Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_order_b2b_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception as e:
                logger.exception(f"order_b2b_processed parse error (blob_id={blob_id})")
                if blob_id:
                    try:
                        record_error_text(models.OrderB2bMessage, blob_id, str(e))
                    except Exception:
                        logger.exception(f"could not record error_text for blob_id={blob_id}")

