"""
Feature: Subscribe to Kafka and persist shipments

Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.
"""
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _publish_isdc(row: models.ShipmentXml, old_row, logic_row: LogicRow):
    """ShipmentXml event: publishes the raw blob to isdc_processed after Tx 1 commits, so Consumer 2 parses it in a clean Tx 2."""
    if not logic_row.is_inserted() or not row.payload:
        return
    if row.is_processed:
        logic_row.log(f"_publish_isdc: skipping re-publish - blob.id={row.id} already is_processed=True (debug path)")
        return
    import integration.kafka.kafka_producer as kafka_producer
    if not kafka_producer.kafka_available():
        logic_row.log("_publish_isdc: Kafka not configured or broker not reachable - skipping publish")
        return
    kafka_producer.producer.produce(topic='isdc_processed', key=str(row.id), value=row.payload.encode('utf-8'))
    kafka_producer.producer.flush(timeout=10)


def declare_logic():
    Rule.after_flush_row_event(on_class=models.ShipmentXml, calling=_publish_isdc)
