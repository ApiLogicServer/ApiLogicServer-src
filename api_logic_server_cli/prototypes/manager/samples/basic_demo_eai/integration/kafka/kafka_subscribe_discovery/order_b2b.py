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
       parses payload -> Order + Items (lookups + LogicBank rules) (Tx 2)
  4. api/api_discovery/order_b2b_kafka_consume_debug.py
       /consume_debug/order_b2b sends the sample live, or calls the same parse function directly (simulated)

Creating prompt: docs/requirements/demo_eai/requirements.md, section 3 (Kafka Subscribe).

Test without Kafka (simulated):
    curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json&mode=simulated"
Tests: test/api_logic_server_behave/features/ (Feature: Kafka Subscribe Order Integration)

Enable Kafka: in config/default.env set
    KAFKA_SERVER = localhost:9092
    KAFKA_CONSUMER_GROUP = demo_eai-group1
then, before the first live start:  bash integration/kafka/order_b2b_reset.sh   (resets topics + log)
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
    """
    Kafka subscribe order_b2b: parse the message, resolve lookups, persist Order + Items, mark the blob processed.
    Single function called by both consumer 2 (Kafka) and /consume_debug (simulated).

    blob_id=None (debug path): blob created here, in the same Tx, already processed.
    blob_id set  (Kafka path): existing blob fetched and is_processed set to True.
    """
    from integration.OrderB2bKafkaMapper import parse
    raw = json.loads(payload)
    order, items = parse(payload)
    if items and not hasattr(items[0], '__tablename__'):
        raise TypeError(f"parse() must return list[model_instance]; got {type(items[0]).__name__}")
    resolve_lookups(order, raw, ORDER_B2B_PARENT_LOOKUPS, session)
    for item, item_src in zip(items, raw.get(ORDER_B2B_CHILD_KEY, [])):
        resolve_lookups(item, item_src, ORDER_B2B_CHILD_LOOKUPS, session)
        order.ItemList.append(item)
    session.add(order)
    if blob_id:
        blob = session.get(models.OrderB2bMessage, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.OrderB2bMessage(payload=payload, is_processed=True)
        session.add(blob)
    session.commit()
    return order, blob


def register(bus):
    """Kafka subscribe order_b2b: registers consumer 1 (order_b2b) and consumer 2 (order_b2b_processed)."""

    @bus.handle('order_b2b')
    def order_b2b(msg, safrs_api):
        """Kafka subscribe order_b2b: consumer 1 saves the raw message as an OrderB2bMessage blob (Tx 1)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.OrderB2bMessage(payload=msg.value().decode('utf-8'), is_processed=False)
            session.add(blob)
            session.commit()   # blob.id assigned; the bridge publishes it to order_b2b_processed

    @bus.handle('order_b2b_processed')
    def order_b2b_processed(msg, safrs_api):
        """Kafka subscribe order_b2b_processed: consumer 2 parses the blob into Order + Items (Tx 2)."""
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
                    except Exception:   # never let error-recording end the consumer
                        logger.exception(f"could not record error_text for blob_id={blob_id}")
