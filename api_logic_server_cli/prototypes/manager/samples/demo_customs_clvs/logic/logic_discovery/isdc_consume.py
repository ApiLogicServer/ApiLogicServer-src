"""
EAI Consume — isdc topic, row-event bridge.

On ShipmentXml insert (Tx 1, from Consumer 1 or /consume_debug), publish the raw
payload to isdc_processed so Consumer 2 can parse and persist domain rows in Tx 2.
See integration/kafka/kafka_subscribe_discovery/isdc.py for the full pipeline.
"""
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _publish_isdc(row: models.ShipmentXml, old_row, logic_row: LogicRow):
    """ShipmentXml event: publishes the raw payload to Kafka topic isdc_processed so
    Consumer 2 can parse and persist domain rows in its own transaction (Tx 2)."""
    if not logic_row.is_inserted() or not row.payload:
        return
    if row.is_processed:
        # debug path: process_isdc_payload() already ran Tx 2 inline (blob created with is_processed=True)
        # do NOT re-publish — Consumer 2 would attempt a duplicate insert and crash on UNIQUE constraint
        logic_row.log(f"_publish_isdc: skipping re-publish — blob.id={row.id} already is_processed=True (debug path)")
        return
    import integration.kafka.kafka_producer as kafka_producer
    if kafka_producer.producer is None:
        # Kafka not configured — /consume_debug does Tx 2 directly; nothing to do here
        logic_row.log("_publish_isdc: Kafka not configured — skipping publish")
        return
    kafka_producer.producer.produce(topic='isdc_processed', key=str(row.id), value=row.payload.encode('utf-8'))
    kafka_producer.producer.flush(timeout=10)


def declare_logic():
    Rule.after_flush_row_event(on_class=models.ShipmentXml, calling=_publish_isdc)
