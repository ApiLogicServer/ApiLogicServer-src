"""
ISDC consume bridge: ShipmentXml insert → publish to isdc_processed topic.
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _publish_isdc(row: models.ShipmentXml, old_row, logic_row: LogicRow):
    if not logic_row.is_inserted() or not row.payload:
        return
    if row.is_processed:
        # debug path: process_isdc_payload() already ran Tx 2 inline (blob is_processed=True)
        # do NOT re-publish — Consumer 2 would crash on duplicate insert
        logic_row.log(f"_publish_isdc: skipping re-publish — blob.id={row.id} already is_processed=True (debug path)")
        return
    import integration.kafka.kafka_producer as kafka_producer
    if kafka_producer.producer is None:
        logic_row.log("_publish_isdc: Kafka not configured — skipping publish")
        return
    kafka_producer.producer.produce(
        topic='isdc_processed',
        key=str(row.id),
        value=row.payload.encode('utf-8')
    )
    kafka_producer.producer.flush(timeout=10)


def declare_logic():
    Rule.after_flush_row_event(on_class=models.ShipmentXml, calling=_publish_isdc)
