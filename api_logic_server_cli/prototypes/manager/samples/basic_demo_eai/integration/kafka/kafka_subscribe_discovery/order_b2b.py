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
       reads the message, inserts the raw payload into OrderB2bMessage (Tx 1)
  2. logic/logic_discovery/order_b2b_consume.py
       blob insert -> publishes the payload to topic order_b2b_processed
  3. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b_processed
       parses the payload -> Order + Items (lookups + LogicBank rules) (Tx 2)
  4. api/api_discovery/order_b2b_kafka_consume_debug.py
       /consume_debug/order_b2b: live through the broker when one answers, else calls process_order_b2b_payload directly

Creating prompt: docs/requirements/demo_eai/requirements.md, section 3 (Kafka Subscribe).

Test: see the docstring of api/api_discovery/order_b2b_kafka_consume_debug.py for the curl commands, and
  python test/send_order_b2b.py   (standalone publisher, live Kafka)

Enable Kafka: set KAFKA_SERVER and a project-unique KAFKA_CONSUMER_GROUP in config/default.env, start the broker
  (docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d), run
  bash integration/kafka/order_b2b_reset.sh to create/reset the topics, then (re)start the server.
"""
import logging

import safrs

from database import models
from integration.system.EaiSubscribeMapper import resolve_lookups, record_error_text

logger = logging.getLogger('integration.kafka')

# name -> FK lookups, co-located with the consumer that owns them
ORDER_B2B_PARENT_LOOKUPS = [(models.Customer, models.Customer.name, 'Account', 'customer_id')]
ORDER_B2B_CHILD_LOOKUPS = [(models.Product, models.Product.name, 'Name', 'product_id')]
ORDER_B2B_CHILD_KEY = 'Items'


def process_order_b2b_payload(payload: str, session, blob_id: int = None):
    """Order_b2b consumer 2: parses the payload, resolves lookups, persists Order + Items, marks the blob processed.
    Called by Consumer 2 (Kafka) and by /consume_debug (simulated).  blob_id=None: the blob is created here."""
    import json
    from integration.OrderB2bMapper import parse
    raw = json.loads(payload)
    order_row, item_rows = parse(payload)
    if item_rows and not hasattr(item_rows[0], '__tablename__'):
        raise TypeError(f"parse() must return list[model_instance]; got {type(item_rows[0]).__name__}")
    resolve_lookups(order_row, raw, ORDER_B2B_PARENT_LOOKUPS, session)
    for item_row, item_src in zip(item_rows, raw.get(ORDER_B2B_CHILD_KEY, [])):
        resolve_lookups(item_row, item_src, ORDER_B2B_CHILD_LOOKUPS, session)
        order_row.ItemList.append(item_row)
    session.add(order_row)
    if blob_id:
        blob = session.get(models.OrderB2bMessage, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.OrderB2bMessage(payload=payload, is_processed=True)
        session.add(blob)
    session.commit()
    return order_row, blob


def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('order_b2b')
    def order_b2b(msg, safrs_api):
        """Kafka subscribe order_b2b, consumer 1: saves the raw message as a blob row and commits (Tx 1)."""
        with safrs_api.app.app_context():
            from datetime import datetime
            session = safrs.DB.session
            blob = models.OrderB2bMessage(payload=msg.value().decode('utf-8'), is_processed=False,
                                          received_at=datetime.utcnow())
            session.add(blob)
            session.commit()   # blob.id assigned; the row event publishes to order_b2b_processed

    @bus.handle('order_b2b_processed')
    def order_b2b_processed(msg, safrs_api):
        """Kafka subscribe order_b2b_processed, consumer 2: parses and persists the Order (Tx 2); failures go to error_text."""
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
