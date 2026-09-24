"""
row_event bridge for the order_b2b 2-message pattern (Req §3).
Publishes the raw blob to order_b2b_processed after Tx 1 commits — no inline parse.
"""
from logic_bank.logic_bank import Rule
import database.models as models


def _publish_order_b2b(row: models.OrderB2bMessage, old_row, logic_row):
    """OrderB2bMessage event: publishes the raw blob to order_b2b_processed after Tx 1
    commits, so Consumer 2 can parse it in a clean Tx 2 (2-message pattern)."""
    if not logic_row.is_inserted() or not row.payload:
        return
    if row.is_processed:
        # debug path: process_order_b2b_payload() already ran Tx 2 inline
        # (blob created with is_processed=True) — do NOT re-publish, Consumer 2
        # would attempt a duplicate insert and crash on UNIQUE constraint
        logic_row.log(f"_publish_order_b2b: skipping re-publish — blob.id={row.id} already is_processed=True (debug path)")
        return
    import integration.kafka.kafka_producer as kafka_producer
    if kafka_producer.producer is None:
        # Kafka not configured — /consume_debug does Tx 2 directly; nothing to do here
        logic_row.log("_publish_order_b2b: Kafka not configured — skipping publish")
        return
    kafka_producer.producer.produce(topic='order_b2b_processed', key=str(row.id), value=row.payload.encode('utf-8'))
    kafka_producer.producer.flush(timeout=10)


def declare_logic():
    Rule.after_flush_row_event(on_class=models.OrderB2bMessage, calling=_publish_order_b2b)
