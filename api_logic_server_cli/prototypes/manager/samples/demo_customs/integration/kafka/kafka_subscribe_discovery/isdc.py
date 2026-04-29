"""
ISDC Kafka Consumer — CIMCorpShipment XML → Shipment domain tables

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/isdc.py  (this file)
       Consumer 1 (`isdc`): saves raw XML payload as ShipmentXml blob row (Tx 1 — always succeeds)
  2. logic/logic_discovery/isdc_consume.py
       after_flush_row_event on ShipmentXml insert → publishes blob to topic `isdc_processed`
  3. integration/kafka/kafka_subscribe_discovery/isdc.py  (this file)
       Consumer 2 (`isdc_processed`): parses XML → Shipment + children (Tx 2 — parse failure isolated)
  4. api/api_discovery/isdc_kafka_consume_debug.py
       /consume_debug/isdc  — bypasses Kafka, calls process_isdc_payload() directly (same code path)

Debug test (no Kafka required):
  export APILOGICPROJECT_CONSUME_DEBUG=true   (already set in config/default.env)
  curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'

Live Kafka:
  Uncomment KAFKA_SERVER + KAFKA_CONSUMER_GROUP in config/default.env, then:
    docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d
    bash integration/kafka/isdc_reset.sh
    python test/send_isdc.py

Duplicate policy: ISDC_DUPLICATE_POLICY env var (default: replace).
  replace — delete existing shipment graph, reinsert parsed graph (ON DELETE CASCADE handles children)
  fail    — raise DuplicateShipmentError on repeated LOCAL_SHIPMENT_OID_NBR
"""

import logging
import os
import xml.etree.ElementTree as ET

import safrs

from database import models

logger = logging.getLogger('integration.kafka')

ISDC_DUPLICATE_POLICY = os.getenv('ISDC_DUPLICATE_POLICY', 'replace').lower()


class DuplicateShipmentError(Exception):
    pass


def _local_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _get_local_shipment_oid(payload: str) -> int | None:
    """Extract LOCAL_SHIPMENT_OID_NBR from raw XML without full parse."""
    try:
        root = ET.fromstring(payload)
        for section in root:
            if _local_tag(section.tag) == "shipment":
                for child in section:
                    if _local_tag(child.tag) == "LOCAL_SHIPMENT_OID_NBR" and child.text:
                        return int(child.text)
    except Exception:
        pass
    return None


def process_isdc_payload(payload: str, session, blob_id: int = None):
    """
    Parse CIMCorpShipment XML and persist domain rows.

    Called by both Consumer 2 (Kafka path, blob_id set) and /consume_debug (debug path, blob_id=None).

    Duplicate policy (ISDC_DUPLICATE_POLICY env var):
      replace (default) — delete prior shipment graph; cascade removes children; reinsert parsed graph
      fail              — raise DuplicateShipmentError

    Returns (shipment_row, blob_row).
    """
    from integration.IsdcMapper import parse

    local_oid = _get_local_shipment_oid(payload)

    if local_oid is not None:
        existing = session.get(models.Shipment, local_oid)
        if existing is not None:
            if ISDC_DUPLICATE_POLICY == 'fail':
                raise DuplicateShipmentError(
                    f"Duplicate LOCAL_SHIPMENT_OID_NBR={local_oid} (policy=fail)"
                )
            logger.info(f"process_isdc_payload: replacing existing shipment {local_oid} (policy=replace)")
            session.delete(existing)
            session.flush()   # let ON DELETE CASCADE remove children before re-insert

    shipment_row, virtual_legs = parse(payload)

    session.add(shipment_row)
    for leg in virtual_legs:
        session.add(leg)

    if blob_id:
        blob = session.get(models.ShipmentXml, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.ShipmentXml(payload=payload, is_processed=True)
        session.add(blob)

    session.commit()

    return shipment_row, blob


def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('isdc')
    def isdc(msg, safrs_api):
        """Consumer 1: save raw XML blob, commit. row_event publishes to isdc_processed."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.ShipmentXml(
                payload=msg.value().decode('utf-8'),
                is_processed=False,
            )
            session.add(blob)
            session.commit()

    @bus.handle('isdc_processed')
    def isdc_processed(msg, safrs_api):
        """Consumer 2: parse XML + persist domain rows, mark blob processed (Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_isdc_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception:
                logger.exception(f"isdc_processed parse error (blob_id={blob_id})")
