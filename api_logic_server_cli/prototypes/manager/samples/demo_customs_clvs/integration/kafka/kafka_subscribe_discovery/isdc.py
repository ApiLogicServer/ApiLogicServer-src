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

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc
       reads message, inserts raw payload into ShipmentXml blob (Tx 1)
  2. logic/logic_discovery/isdc_consume.py
       blob insert -> publishes payload to topic: isdc_processed
  3. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc_processed
       parses payload -> Shipment graph (mapper + LogicBank rules) (Tx 2); duplicate policy fail|replace
  4. api/api_discovery/isdc_kafka_consume_debug.py
       /consume_debug/isdc bypasses Kafka (simulated) or publishes live

Enable Kafka: KAFKA_SERVER / KAFKA_CONSUMER_GROUP in config/default.env; reset with `bash integration/kafka/isdc_reset.sh`.
Duplicate policy: ISDC_DUPLICATE_POLICY in config/default.env (fail|replace, default replace).
"""
import logging
import os
import safrs
from database import models
from integration.system.EaiSubscribeMapper import record_error_text

logger = logging.getLogger('integration.kafka')

_CHILD_LISTS = {models.Piece: "PieceList", models.ShipmentParty: "ShipmentPartyList",
                models.ShipmentCommodity: "ShipmentCommodityList"}


def duplicate_policy() -> str:
    """ISDC config: the duplicate-shipment policy, fail or replace (default replace)."""
    policy = (os.getenv("ISDC_DUPLICATE_POLICY") or "replace").strip().lower()
    return policy if policy in ("fail", "replace") else "replace"


def process_isdc_payload(payload: str, session, blob_id: int = None):
    """ISDC subscribe: parse the XML, apply the duplicate policy, persist the Shipment graph and mark the blob (Tx 2).
    Shared by Consumer 2 (Kafka, blob_id set) and /consume_debug simulated (blob created here, already processed)."""
    from integration.IsdcMapper import parse
    shipment, children = parse(payload)          # parse first: a bad message never touches the existing graph
    existing = session.get(models.Shipment, shipment.local_shipment_oid_nbr)
    if existing is not None:
        if duplicate_policy() == "fail":
            raise ValueError(f"duplicate shipment {shipment.local_shipment_oid_nbr} (policy=fail)")
        for each in (list(existing.ShipmentPartyList) + list(existing.PieceList)
                     + list(existing.ShipmentCommodityList) + list(existing.SpecialHandlingList)):
            session.delete(each)
        session.delete(existing)
        session.flush()                          # same Tx: old graph gone before the new rows are inserted
    for child in children:
        getattr(shipment, _CHILD_LISTS[type(child)]).append(child)
    session.add(shipment)
    if blob_id:
        blob = session.get(models.ShipmentXml, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.ShipmentXml(payload=payload, is_processed=True)
        session.add(blob)
    session.commit()
    return shipment, blob


def register(bus):
    """Kafka subscribe isdc: wires Consumer 1 (save blob) and Consumer 2 (parse and persist)."""

    @bus.handle('isdc')
    def isdc(msg, safrs_api):
        """Kafka subscribe isdc: Consumer 1 saves the raw XML as a ShipmentXml blob and commits (Tx 1)."""
        from datetime import datetime
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.ShipmentXml(payload=msg.value().decode('utf-8'), is_processed=False,
                                      received_at=datetime.utcnow())
            session.add(blob)
            session.commit()

    @bus.handle('isdc_processed')
    def isdc_processed(msg, safrs_api):
        """Kafka subscribe isdc_processed: Consumer 2 parses the blob and persists the Shipment graph (Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_isdc_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception as e:
                logger.exception(f"isdc_processed parse error (blob_id={blob_id})")
                if blob_id:
                    try:
                        record_error_text(models.ShipmentXml, blob_id, str(e))
                    except Exception:   # never let error-recording end the consumer
                        logger.exception(f"could not record error_text for blob_id={blob_id}")
