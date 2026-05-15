"""
ISDC Kafka Consumer — CIMCorp Shipment XML → Domain DB

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc consumer
       reads message, inserts raw payload into ShipmentXml blob (Tx 1)
  2. logic/logic_discovery/isdc_consume.py
       insert → publishes payload to topic: isdc_processed
  3. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc_processed consumer
       parses payload → domain rows (Tx 2); replace-on-duplicate by default
  4. api/api_discovery/isdc_kafka_consume_debug.py
       /consume_debug/isdc bypasses Kafka, calls same parse function directly

Creating prompt:
  Subscribe to Kafka topic `isdc` (CIMCorp XML). Parse and persist to
  Shipment + Piece + ShipmentParty + ShipmentCommodity + SpecialHandling +
  VirtualRouteLeg using field mappings in message_formats/Classify_Entity_Details.csv.

Debug test (no Kafka required):
  curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'

Live Kafka:
  1. Edit config/default.env: uncomment KAFKA_SERVER + KAFKA_CONSUMER_GROUP
  2. docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d
  3. bash integration/kafka/isdc_reset.sh
  4. python api_logic_server_run.py
  5. python test/send_isdc.py

Duplicate policy (env var ISDC_DUPLICATE_POLICY):
  replace (default) — delete + reinsert on same LOCAL_SHIPMENT_OID_NBR
  fail             — raise error on duplicate

SQLite FK enforcement: enabled per-connection in process_isdc_payload.
"""

import logging
import os
import safrs
from database import models
from integration.IsdcMapper import parse

logger = logging.getLogger('integration.kafka')

DUPLICATE_POLICY = os.environ.get('ISDC_DUPLICATE_POLICY', 'replace').lower()


def process_isdc_payload(payload: str, session, blob_id: int = None):
    """
    Parse CIMCorp XML payload, persist domain rows, mark blob processed.

    blob_id=None (debug path): blob created inside this function in the same Tx.
    blob_id set  (Kafka path): existing blob fetched and is_processed set to True.
    """
    # Enable FK enforcement for this connection (SQLite)
    session.execute(safrs.DB.text("PRAGMA foreign_keys = ON"))

    shipment_row, children = parse(payload)

    # Duplicate handling
    pk = shipment_row.local_shipment_oid_nbr
    existing = session.get(models.Shipment, pk) if pk else None
    if existing:
        if DUPLICATE_POLICY == 'fail':
            raise ValueError(f"Duplicate shipment: LOCAL_SHIPMENT_OID_NBR={pk}")
        # replace: delete cascades to Piece, ShipmentParty, ShipmentCommodity, SpecialHandling
        session.delete(existing)
        session.flush()

    # Attach children via relationships (mandatory per eai_subscribe.md)
    for piece in children['pieces']:
        shipment_row.PieceList.append(piece)

    for party in children['parties']:
        shipment_row.ShipmentPartyList.append(party)

    for commodity in children['commodities']:
        shipment_row.ShipmentCommodityList.append(commodity)

    for sh in children['special_handling']:
        shipment_row.SpecialHandlingList.append(sh)

    session.add(shipment_row)

    # VirtualRouteLeg has no FK to Shipment — add directly
    for leg in children['route_legs']:
        session.add(leg)

    if blob_id:
        blob = session.get(models.ShipmentXml, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.ShipmentXml(payload=payload, is_processed=True)
        session.add(blob)

    session.commit()

    awb = shipment_row.awb_nbr
    pieces = len(children['pieces'])
    parties = len(children['parties'])
    commodities = len(children['commodities'])
    return shipment_row, blob, {
        'awb_nbr': awb,
        'pieces': pieces,
        'parties': parties,
        'commodities': commodities,
    }


def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('isdc')
    def isdc(msg, safrs_api):
        """Consumer 1: save blob, commit. row_event publishes to isdc_processed."""
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
        """Consumer 2: parse + persist domain rows, mark blob processed (Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_isdc_payload(
                    msg.value().decode('utf-8'),
                    session,
                    blob_id=blob_id,
                )
            except Exception:
                logger.exception(f"isdc_processed parse error (blob_id={blob_id})")
