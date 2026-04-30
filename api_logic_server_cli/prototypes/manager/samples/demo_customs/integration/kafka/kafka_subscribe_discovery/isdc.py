"""
ISDC Kafka Consumer — CIMCorpShipment XML → Shipment domain graph.

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/isdc.py  (this file)
       Consumer 1: reads raw message, saves to ShipmentXml blob (Tx 1)
  2. logic/logic_discovery/isdc_consume.py
       after_flush_row_event: blob insert → publishes payload to topic isdc_processed
  3. integration/kafka/kafka_subscribe_discovery/isdc.py  (Consumer 2: isdc_processed)
       Parses XML → Shipment domain graph, applies duplicate policy, commits (Tx 2)
  4. api/api_discovery/isdc_kafka_consume_debug.py
       /consume_debug/isdc  — bypasses Kafka, calls process_isdc_payload() directly

Duplicate policy (env: ISDC_DUPLICATE_POLICY, default "replace"):
  replace — delete existing Shipment + cascade children, reinsert parsed graph
  fail    — raise ValueError on duplicate LOCAL_SHIPMENT_OID_NBR

Debug (no Kafka required):
  export APILOGICPROJECT_CONSUME_DEBUG=true  (already set in config/default.env)
  F5 to start server, then:
  curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'

Live Kafka:
  Uncomment KAFKA_SERVER + KAFKA_CONSUMER_GROUP in config/default.env:
    KAFKA_SERVER = localhost:9092
    KAFKA_CONSUMER_GROUP = customs_demo-group1
  docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d
  bash integration/kafka/isdc_reset.sh
  python test/send_isdc.py

Test files:
  docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml  (primary)
  docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328-another.xml
"""

import logging
import os
import safrs
from database import models
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

logger = logging.getLogger('integration.kafka')

_DUPLICATE_POLICY = os.getenv('ISDC_DUPLICATE_POLICY', 'replace').lower()

# Enable SQLite FK enforcement so ON DELETE CASCADE fires on db-level deletes
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def process_isdc_payload(payload: str, session, blob_id: int = None):
    """
    Parse ISDC XML payload → persist Shipment domain graph.
    Called by both Consumer 2 (Kafka) and /consume_debug (no-Kafka debug).

    blob_id=None  → debug path: creates blob inline in this Tx (is_processed=True)
    blob_id set   → Kafka path: fetches existing blob and flips is_processed=True
    """
    from integration.IsdcMapper import parse

    parent_row, extras = parse(payload)
    if parent_row is None:
        raise ValueError("No <ns2:shipment> element found in ISDC payload")

    # Guard: parse() must return plain model rows
    for row in extras:
        if not hasattr(row, '__tablename__'):
            raise TypeError(f"parse() must return list[model_instance]; got {type(row).__name__}")

    # Attach child rows via parent relationships (mandatory — standalone session.add raises Missing Parent)
    for row in extras:
        if isinstance(row, models.Piece):
            parent_row.PieceList.append(row)
        elif isinstance(row, models.ShipmentCommodity):
            parent_row.ShipmentCommodityList.append(row)
        elif isinstance(row, models.SpecialHandling):
            parent_row.SpecialHandlingList.append(row)
        elif isinstance(row, models.ShipmentParty):
            parent_row.ShipmentPartyList.append(row)
        elif isinstance(row, models.VirtualRouteLeg):
            session.add(row)   # VirtualRouteLeg has no FK to Shipment

    # Duplicate policy
    existing = session.get(models.Shipment, parent_row.local_shipment_oid_nbr)
    if existing is not None:
        if _DUPLICATE_POLICY == 'fail':
            raise ValueError(
                f"Duplicate shipment: LOCAL_SHIPMENT_OID_NBR={parent_row.local_shipment_oid_nbr} "
                f"(set ISDC_DUPLICATE_POLICY=replace to overwrite)"
            )
        # replace: delete existing graph (ORM cascade removes children), flush, then insert
        logger.info(f"process_isdc_payload: replacing existing shipment {parent_row.local_shipment_oid_nbr}")
        session.delete(existing)
        session.flush()

    session.add(parent_row)

    if blob_id is not None:
        blob = session.get(models.ShipmentXml, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.ShipmentXml(payload=payload, is_processed=True)
        session.add(blob)

    session.commit()

    pieces      = len([r for r in extras if isinstance(r, models.Piece)])
    parties     = len([r for r in extras if isinstance(r, models.ShipmentParty)])
    commodities = len([r for r in extras if isinstance(r, models.ShipmentCommodity)])

    return parent_row, blob, {"pieces": pieces, "parties": parties, "commodities": commodities}


def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('isdc')
    def isdc(msg, safrs_api):
        """Consumer 1: save raw XML blob, commit. row_event publishes to isdc_processed."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.ShipmentXml(payload=msg.value().decode('utf-8'), is_processed=False)
            session.add(blob)
            session.commit()   # blob.id assigned; after_flush_row_event publishes to isdc_processed

    @bus.handle('isdc_processed')
    def isdc_processed(msg, safrs_api):
        """Consumer 2: parse XML + persist domain graph, mark blob processed (Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_isdc_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception:
                logger.exception(f"isdc_processed parse error (blob_id={blob_id})")
