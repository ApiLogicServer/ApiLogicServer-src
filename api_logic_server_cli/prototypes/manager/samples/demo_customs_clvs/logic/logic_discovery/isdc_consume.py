"""
Feature: Subscribe to Kafka and persist shipments

Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.

Parse and persist to the database using the field mappings in
`message_formats/Classify_Entity_Details.csv`.

Use `message_formats/MDE-CDV-HVS-WR-Rev260328.xml` as the reference message.

Duplicate replay behavior (required for this project):
- Match existing shipments by `LOCAL_SHIPMENT_OID_NBR` (`Shipment.local_shipment_oid_nbr`).
- If a duplicate key is found, replace the existing shipment graph in Tx 2:
    parse first, then replace the prior shipment graph and insert parsed rows.
    Implementation is not prescribed; behavior must match the verification checks below.
- Keep this behavior configurable via env policy (`fail|replace`), default `replace` for this project.

Important mapping note (prevent PK collisions):
- In this payload, party OID fields may carry placeholder value `0` for multiple rows.
- If mapped to local primary-key columns (e.g. `ShipmentParty.shipment_party_oid_nbr`),
  normalize placeholder IDs to `None` so DB autoincrement assigns unique PK values.
"""
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _publish_isdc(row: models.ShipmentXml, old_row, logic_row: LogicRow):
    """ShipmentXml event: publishes the raw XML blob to topic isdc_processed after Tx 1 commits, so Consumer 2
    parses it in a clean Tx 2 (2-message pattern). Skipped for the simulated path (blob already processed)."""
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
