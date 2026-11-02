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
import logging
import os
import safrs
from database import models
from integration.system.EaiSubscribeMapper import record_error_text

logger = logging.getLogger('integration.kafka')


def _duplicate_policy() -> str:
    """Subscribe isdc: duplicate-shipment policy from env ISDC_DUPLICATE_POLICY (fail|replace); default replace."""
    policy = os.getenv("ISDC_DUPLICATE_POLICY", "replace").strip().lower()
    return policy if policy in ("fail", "replace") else "replace"


def _replace_existing(shipment_oid: int, session) -> bool:
    """Subscribe isdc: deletes the prior Shipment graph (parties, commodities, pieces, special handling, shipment)
    for this LOCAL_SHIPMENT_OID_NBR, flushed before the new rows are inserted, so rules see delete then insert."""
    existing = session.get(models.Shipment, shipment_oid)
    if existing is None:
        return False
    policy = _duplicate_policy()
    if policy == "fail":
        raise ValueError(f"duplicate shipment {shipment_oid} (ISDC_DUPLICATE_POLICY=fail)")
    for child_list in (existing.ShipmentPartyList, existing.ShipmentCommodityList,
                       existing.SpecialHandlingList, existing.PieceList):
        for child in list(child_list):
            session.delete(child)
    session.flush()
    session.expire(existing)          # drop the stale child collections, or deleting the parent tries to blank their PKs
    session.delete(existing)
    session.flush()
    return True


def process_isdc_payload(payload: str, session, blob_id: int = None):
    """Subscribe isdc: parse the shipment XML, replace any prior graph for the same shipment, insert the parsed
    graph and mark the blob processed. One function for Consumer 2 (Kafka) and /consume_debug (simulated)."""
    from integration.IsdcMapper import parse
    shipment, children = parse(payload)
    if children and not hasattr(children[0], '__tablename__'):
        raise TypeError("parse() must return plain model rows")
    replaced = False
    if shipment.local_shipment_oid_nbr is not None:
        replaced = _replace_existing(shipment.local_shipment_oid_nbr, session)
    for child in children:
        if isinstance(child, models.ShipmentParty):
            shipment.ShipmentPartyList.append(child)
        elif isinstance(child, models.Piece):
            shipment.PieceList.append(child)
        elif isinstance(child, models.ShipmentCommodity):
            shipment.ShipmentCommodityList.append(child)
        elif isinstance(child, models.SpecialHandling):
            shipment.SpecialHandlingList.append(child)
        else:
            session.add(child)                       # VirtualRouteLeg: no shipment link in the model; just store
    session.add(shipment)
    if blob_id:
        blob = session.get(models.ShipmentXml, blob_id)
        if blob:
            blob.is_processed = True
    else:
        from datetime import datetime
        blob = models.ShipmentXml(payload=payload, is_processed=True, received_at=datetime.utcnow())
        session.add(blob)
    session.commit()
    logger.info(f"isdc: shipment {shipment.local_shipment_oid_nbr} persisted (replaced prior graph: {replaced})")
    return shipment, blob


def register(bus):
    """Subscribe isdc: wires Consumer 1 (topic isdc) and Consumer 2 (topic isdc_processed); see auto_discovery."""

    @bus.handle('isdc')
    def isdc(msg, safrs_api):
        """Kafka subscribe isdc: Consumer 1 saves the raw XML to ShipmentXml and commits (Tx 1);
        the bridge event then publishes it to isdc_processed."""
        from datetime import datetime
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.ShipmentXml(payload=msg.value().decode('utf-8'), is_processed=False,
                                      received_at=datetime.utcnow())
            session.add(blob)
            session.commit()

    @bus.handle('isdc_processed')
    def isdc_processed(msg, safrs_api):
        """Kafka subscribe isdc_processed: Consumer 2 parses the blob and persists the Shipment graph (Tx 2);
        a failure is recorded on the blob's error_text and the consumer carries on."""
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
                    except Exception:
                        logger.exception(f"could not record error_text for blob_id={blob_id}")
