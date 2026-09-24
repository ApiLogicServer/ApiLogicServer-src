"""
Kafka Subscribe — order_b2b (Req §3)
=====================================
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity

Basic Design (2-message pattern — mandatory, see docs/training/eai_subscribe.md):
  1. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b
       reads message, inserts raw payload into OrderB2bMessage blob (Tx 1)
  2. logic/logic_discovery/order_b2b_consume.py
       insert → publishes payload to topic: order_b2b_processed
  3. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b_processed
       parses payload → domain rows (lookups + LogicBank rules) (Tx 2)
  4. api/api_discovery/order_b2b_consume_debug.py
       /consume_debug/order_b2b bypasses Kafka, calls same parse function directly

Quick Test (no Kafka needed):
  curl 'http://localhost:5656/consume_debug/order_b2b?file=integration/kafka/message_formats/order_b2b.json'
"""
import json
import logging
import safrs
from database import models
from integration.system.EaiSubscribeMapper import resolve_lookups

logger = logging.getLogger('integration.kafka')

ORDER_B2B_PARENT_LOOKUPS = [
    (models.Customer, models.Customer.name, 'Account', 'customer_id'),
]
ORDER_B2B_CHILD_LOOKUPS = [
    (models.Product, models.Product.name, 'Name', 'product_id'),
]
ORDER_B2B_CHILD_KEY = 'Items'


def _record_error_text(blob_id: int, error_text: str):
    """Persist a Tx 2 failure reason onto its blob row, in its own clean transaction.

    Called from the except block of a Kafka consumer — never call session.rollback()
    there; use a fresh session scope so this write can't be poisoned by the failed Tx 2
    it's reporting on.
    """
    fresh_session = safrs.DB.session
    blob = fresh_session.get(models.OrderB2bMessage, blob_id)
    if blob:
        blob.error_text = error_text
        fresh_session.commit()


def process_order_b2b_payload(payload: str, session, blob_id: int = None):
    """
    Parse payload, resolve lookups, persist domain rows, mark blob processed.

    Called by both Consumer 2 (Kafka path) and /consume_debug/order_b2b (no-Kafka path).
    blob_id=None (debug path): blob created inside this function with is_processed=True.
    blob_id set  (Kafka path): existing blob fetched and is_processed set to True.
    """
    from integration.OrderB2bMapper import parse
    raw = json.loads(payload)
    order_row, item_rows = parse(payload)
    resolve_lookups(order_row, raw, ORDER_B2B_PARENT_LOOKUPS, session)
    for item_row, item_src in zip(item_rows, raw.get(ORDER_B2B_CHILD_KEY, [])):
        resolve_lookups(item_row, item_src, ORDER_B2B_CHILD_LOOKUPS, session)
        order_row.ItemList.append(item_row)   # attach via relationship — NOT session.add(item_row)

    session.add(order_row)

    if blob_id is not None:
        blob = session.get(models.OrderB2bMessage, blob_id)
        if blob:
            blob.is_processed = True
    else:
        # Debug path: create the blob inline with is_processed=True
        blob = models.OrderB2bMessage(payload=payload, is_processed=True)
        session.add(blob)

    session.commit()
    return order_row, blob


# ─── Kafka consumer registration ─────────────────────────────────────────────

def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('order_b2b')
    def order_b2b(msg, safrs_api):
        """Consumer 1: save raw blob, commit. row_event publishes to order_b2b_processed."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.OrderB2bMessage(payload=msg.value().decode('utf-8'), is_processed=False)
            session.add(blob)
            session.commit()   # blob.id assigned; row_event bridge publishes to order_b2b_processed

    @bus.handle('order_b2b_processed')
    def order_b2b_processed(msg, safrs_api):
        """Consumer 2: parse + persist domain rows, mark blob processed (atomic Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_order_b2b_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception as e:
                logger.exception(f"order_b2b_processed parse error (blob_id={blob_id})")
                if blob_id:
                    _record_error_text(blob_id, str(e))
