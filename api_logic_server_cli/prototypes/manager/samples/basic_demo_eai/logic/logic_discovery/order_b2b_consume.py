"""
Row-Event Bridge — order_b2b_message → order_b2b_processed topic
=================================================================
Req §3 (2-message pattern): After Consumer 1 commits an OrderB2bMessage blob,
this after_flush_row_event publishes the payload to the 'order_b2b_processed'
topic so Consumer 2 can parse and persist the domain rows.

Why after_flush_row_event (not row_event)?
  after_flush fires after SQLite assigns blob.id, so the Kafka key is a valid
  integer (not 'None'). row_event fires during before_flush — before the id is set.

is_processed guard (mandatory):
  The debug path (/consume_debug/order_b2b) runs process_order_b2b_payload()
  directly and creates the blob with is_processed=True in the same Tx.
  Without the guard, after_flush_row_event would re-publish to order_b2b_processed,
  causing Consumer 2 to attempt a duplicate insert → UNIQUE constraint crash.
"""
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
import database.models as models


def _publish_order_b2b(row: models.OrderB2bMessage, old_row, logic_row: LogicRow):
    if not logic_row.is_inserted() or not row.payload:
        return
    if row.is_processed:
        # Debug path: Tx 2 already ran inline; do NOT re-publish.
        return
    import integration.kafka.kafka_producer as kafka_producer
    if kafka_producer.producer is None:
        logic_row.log("_publish_order_b2b: Kafka not configured — skipping publish")
        return
    kafka_producer.producer.produce(
        topic='order_b2b_processed',
        key=str(row.id),
        value=row.payload.encode('utf-8'),
    )
    kafka_producer.producer.flush(timeout=10)


def declare_logic():
    Rule.after_flush_row_event(on_class=models.OrderB2bMessage, calling=_publish_order_b2b)
