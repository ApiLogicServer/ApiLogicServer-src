"""
Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc
       reads message, inserts raw payload into ShipmentXml blob (Tx 1)
  2. logic/logic_discovery/isdc_consume.py
       insert -> publishes payload to topic: isdc_processed
  3. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc_processed
       parses payload -> domain rows (lookups + LogicBank rules) (Tx 2)
  4. api/api_discovery/isdc_kafka_consume_debug.py
       /consume_debug/isdc bypasses Kafka, calls same parse function directly

Creating prompt (docs/requirements/customs_demo/requirements.md, Step 1):
  Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.
  Parse and persist to the database using the field mappings in
  message_formats/Classify_Entity_Details.csv.
  Duplicate replay: match existing shipments by LOCAL_SHIPMENT_OID_NBR; if found, replace
  the existing shipment graph in Tx 2 (parse first, then replace + insert parsed rows).
  Policy configurable via ISDC_DUPLICATE_POLICY env var, default 'replace'.

Debug test (no Kafka required):
  curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'

Enable Kafka:
  Set KAFKA_SERVER / KAFKA_CONSUMER_GROUP in config/default.env, then:
  bash integration/kafka/isdc_reset.sh
"""
import os
import logging
import safrs
from database import models

logger = logging.getLogger('integration.kafka')


def process_isdc_payload(payload: str, session, blob_id: int = None):
    """
    Parse payload, replace-on-duplicate, persist domain rows, mark blob processed.
    Single function called by both consumer 2 (Kafka) and /consume_debug (no-Kafka debug).

    blob_id=None (debug path): blob created inside this function in the same Tx.
    blob_id set  (Kafka path): existing blob fetched and is_processed set to True.
    """
    from integration.IsdcMapper import parse
    parent_row, child_rows = parse(payload)
    if child_rows and not hasattr(child_rows[0], '__tablename__'):
        raise TypeError(f"parse() must return list[model_instance]; got {type(child_rows[0]).__name__} — check IsdcMapper.parse() return value")

    duplicate_policy = os.getenv('ISDC_DUPLICATE_POLICY', 'replace')
    existing = session.query(models.Shipment).filter(
        models.Shipment.local_shipment_oid_nbr == parent_row.local_shipment_oid_nbr).first()
    if existing is not None:
        if duplicate_policy != 'replace':
            raise ValueError(
                f"Duplicate Shipment local_shipment_oid_nbr={parent_row.local_shipment_oid_nbr} "
                f"(ISDC_DUPLICATE_POLICY={duplicate_policy})")
        session.delete(existing)
        session.flush()   # ON DELETE CASCADE (PRAGMA foreign_keys=ON) removes children

    for child_row in child_rows:
        if isinstance(child_row, models.Piece):
            parent_row.PieceList.append(child_row)
        elif isinstance(child_row, models.ShipmentParty):
            parent_row.ShipmentPartyList.append(child_row)
        elif isinstance(child_row, models.ShipmentCommodity):
            parent_row.ShipmentCommodityList.append(child_row)
        elif isinstance(child_row, models.SpecialHandling):
            parent_row.SpecialHandlingList.append(child_row)

    session.add(parent_row)
    if blob_id:
        blob = session.get(models.ShipmentXml, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.ShipmentXml(payload=payload, is_processed=True)
        session.add(blob)
    session.commit()
    return parent_row, blob


def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('isdc')
    def isdc(msg, safrs_api):
        """Consumer 1: save blob, commit. row_event publishes to isdc_processed."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.ShipmentXml(payload=msg.value().decode('utf-8'), is_processed=False)
            session.add(blob)
            session.commit()   # blob.id assigned; row_event publishes to isdc_processed

    @bus.handle('isdc_processed')
    def isdc_processed(msg, safrs_api):
        """Consumer 2: parse + persist domain rows, mark blob processed (atomic Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_isdc_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception as e:
                logger.exception(f"isdc_processed parse error (blob_id={blob_id})")  # blob stays is_processed=False; full traceback logged
