"""
ISDC EAI Consume Pipeline — CIMCorp Shipment XML → Shipment domain rows.

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc
       reads message, inserts raw payload into ShipmentXml blob (Tx 1)
  2. logic/logic_discovery/isdc_consume.py
       insert → publishes payload to topic: isdc_processed
  3. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc_processed
       parses payload → domain rows (ShipmentXml, Shipment, Piece, ShipmentParty, ShipmentCommodity) (Tx 2)
  4. api/api_discovery/isdc_kafka_consume_debug.py
       /consume_debug/isdc bypasses Kafka, calls process_isdc_payload() directly

Creating prompt:
  Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.
  Parse and persist to the database using field mappings in Classify_Entity_Details.csv.
  Duplicate replay policy: replace (match by LOCAL_SHIPMENT_OID_NBR, delete prior graph, reinsert).
  Normalize PARTY_OID_NBR placeholder 0 → None (DB autoincrement assigns PK).

Debug test (no Kafka required):
  curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'

Kafka test:
  Set KAFKA_SERVER = localhost:9092 and KAFKA_CONSUMER_GROUP = customs_demo-group1 in config/default.env
  bash integration/kafka/isdc_reset.sh
  python test/send_isdc.py
"""
import logging
import os
import safrs
from database import models

logger = logging.getLogger('integration.kafka')

# Duplicate policy: 'replace' (default for this project) or 'fail'
_DUPLICATE_POLICY = os.getenv("ISDC_DUPLICATE_POLICY", "replace")


def process_isdc_payload(payload: str, session, blob_id: int = None):
    """
    Parse CIMCorp shipment XML, persist domain rows, mark blob processed.

    blob_id=None (debug path): blob created inside this function in the same Tx.
    blob_id set  (Kafka path): existing blob fetched and is_processed set to True.

    Duplicate policy (env: ISDC_DUPLICATE_POLICY):
      'replace' (default): delete existing Shipment graph, reinsert parsed rows.
      'fail':              raise on duplicate LOCAL_SHIPMENT_OID_NBR.
    """
    from integration.IsdcMapper import parse

    shipment_row, children = parse(payload)

    # Guard: parse() must return plain model rows
    for child in children:
        if not hasattr(child, '__tablename__'):
            raise TypeError(
                f"parse() must return list[model_instance]; got {type(child).__name__} — check IsdcMapper.parse()"
            )

    local_shipment_oid = shipment_row.local_shipment_oid_nbr

    # Duplicate handling
    existing = session.get(models.Shipment, local_shipment_oid)
    if existing is not None:
        if _DUPLICATE_POLICY == "replace":
            # ShipmentCommodity has passive_deletes='all' (composite PK prevents ORM null-out).
            # SQLite requires PRAGMA foreign_keys=ON for DB-level cascade — not guaranteed.
            # Explicitly delete via query before deleting parent to ensure they're removed.
            session.query(models.ShipmentCommodity).filter(
                models.ShipmentCommodity.local_shipment_oid_nbr == local_shipment_oid
            ).delete(synchronize_session='fetch')
            session.delete(existing)   # ORM cascade handles Piece, SpecialHandling, ShipmentParty
            session.flush()            # execute DELETEs before inserting new graph
        else:
            raise ValueError(
                f"Duplicate LOCAL_SHIPMENT_OID_NBR={local_shipment_oid}; ISDC_DUPLICATE_POLICY=fail"
            )

    # Attach children to parent via relationships (mandatory per eai_subscribe.md)
    for child in children:
        t = child.__tablename__
        if t == "piece":
            shipment_row.PieceList.append(child)
        elif t == "shipment_party":
            shipment_row.ShipmentPartyList.append(child)
        elif t == "shipment_commodity":
            # ShipmentCommodity has a composite PK; set FK and append via relationship
            child.local_shipment_oid_nbr = local_shipment_oid
            shipment_row.ShipmentCommodityList.append(child)
        elif t == "special_handling":
            shipment_row.SpecialHandlingList.append(child)
        elif t == "virtual_route_leg":
            session.add(child)     # VirtualRouteLeg has no FK to Shipment; add standalone
        # unknown tables: skip

    session.add(shipment_row)

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
            except Exception:
                logger.exception(f"isdc_processed parse error (blob_id={blob_id})")
                # blob stays is_processed=False; queryable for retry
