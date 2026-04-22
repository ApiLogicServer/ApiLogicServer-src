"""
Kafka Subscribe — order_b2b topic
===================================
Req §3: 2-message pattern for inbound orders from the sales channel.

Pipeline:
  Consumer 1  ('order_b2b')          → save raw blob to OrderB2bMessage, commit (Tx 1)
  after_flush_row_event               → publish blob to 'order_b2b_processed' topic
  Consumer 2  ('order_b2b_processed') → parse + persist Order+Items, mark blob (Tx 2)

Debug (no Kafka):
  curl 'http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json'
"""
import json
import logging
import safrs
from database import models
from integration.system.EaiSubscribeMapper import resolve_lookups

logger = logging.getLogger('integration.kafka')

# ─── Lookup configuration ────────────────────────────────────────────────────

# Parent-level: Account (customer name) → customer_id
ORDER_B2B_PARENT_LOOKUPS = [
    (models.Customer, models.Customer.name, 'Account', 'customer_id'),
]

# Child-level: Name (product name) → product_id
ORDER_B2B_CHILD_LOOKUPS = [
    (models.Product, models.Product.name, 'Name', 'product_id'),
]

ORDER_B2B_CHILD_KEY = 'Items'


# ─── Shared parse + persist function ─────────────────────────────────────────

def process_order_b2b_payload(payload: str, session, blob_id: int = None):
    """Parse payload, resolve lookups, persist domain rows, mark blob processed.

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
                logger.exception("order_b2b_processed parse error")   # blob stays is_processed=False
