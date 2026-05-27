"""
isdc Kafka consumer — CIMCorp Shipment XML → database (2-message design).

Basic Design:
  1. isdc.py / isdc handler
       Consumer 1: saves raw XML payload into ShipmentXml blob row, commits (Tx 1)
  2. logic/logic_discovery/isdc_consume.py
       after_flush_row_event on ShipmentXml insert → publishes to topic isdc_processed
  3. isdc.py / isdc_processed handler
       Consumer 2: parses XML → Shipment + children, marks blob processed (Tx 2)
  4. api/api_discovery/isdc_kafka_consume_debug.py
       /consume_debug/isdc — bypasses Kafka, same parse function, no Kafka required

Debug (no Kafka):
  curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'

Live Kafka — enable in config/default.env:
  KAFKA_SERVER = localhost:9092
  KAFKA_CONSUMER_GROUP = customs_demo-group1

  bash integration/kafka/isdc_reset.sh   # reset topics + log between runs
  python test/send_isdc.py               # send a test message

Duplicate policy: REPLACE (configurable via env ISDC_DUPLICATE_POLICY=fail|replace)
  If LOCAL_SHIPMENT_OID_NBR already exists, the existing shipment graph is deleted
  and the new parsed graph is inserted.
"""
import logging
import os
import safrs
from datetime import datetime
from sqlalchemy import text
from database import models

logger = logging.getLogger('integration.kafka')

DUPLICATE_POLICY = os.getenv('ISDC_DUPLICATE_POLICY', 'replace')


def process_isdc_payload(payload: str, session, blob_id: int = None):
    """
    Parse CIMCorp XML payload, persist Shipment graph, mark blob processed.

    blob_id=None (debug path): blob created inline in the same Tx.
    blob_id set  (Kafka path): existing blob fetched, is_processed set to True.

    Returns (shipment, blob).
    """
    from integration.IsdcMapper import parse

    shipment, _ = parse(payload)

    # Enforce SQLite FK cascade so DELETE propagates to children
    session.execute(text("PRAGMA foreign_keys = ON"))

    if DUPLICATE_POLICY == 'replace':
        existing = session.get(models.Shipment, shipment.local_shipment_oid_nbr)
        if existing:
            logger.info(f"isdc: replace-on-duplicate for LOCAL_SHIPMENT_OID_NBR={shipment.local_shipment_oid_nbr}")
            session.execute(
                text("DELETE FROM shipment WHERE local_shipment_oid_nbr = :id"),
                {"id": shipment.local_shipment_oid_nbr}
            )
            session.flush()
    elif DUPLICATE_POLICY == 'fail':
        existing = session.get(models.Shipment, shipment.local_shipment_oid_nbr)
        if existing:
            raise ValueError(f"Duplicate LOCAL_SHIPMENT_OID_NBR={shipment.local_shipment_oid_nbr}")

    session.add(shipment)

    if blob_id:
        blob = session.get(models.ShipmentXml, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.ShipmentXml(
            payload=payload,
            received_at=datetime.utcnow(),
            is_processed=True,
        )
        session.add(blob)

    session.commit()

    pieces = len(shipment.PieceList)
    parties = len(shipment.ShipmentPartyList)
    commodities = len(shipment.ShipmentCommodityList)
    logger.info(
        f"isdc: persisted shipment={shipment.local_shipment_oid_nbr} "
        f"awb={shipment.awb_nbr} pieces={pieces} parties={parties} commodities={commodities}"
    )
    return shipment, blob


def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('isdc')
    def isdc(msg, safrs_api):
        """Consumer 1: save blob, commit. row_event publishes to isdc_processed."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.ShipmentXml(
                payload=msg.value().decode('utf-8'),
                received_at=datetime.utcnow(),
                is_processed=False,
            )
            session.add(blob)
            session.commit()

    @bus.handle('isdc_processed')
    def isdc_processed(msg, safrs_api):
        """Consumer 2: parse + persist domain rows, mark blob processed (Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_isdc_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception:
                logger.exception(f"isdc_processed parse error (blob_id={blob_id})")
