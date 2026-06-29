"""
ISDC Kafka Consumer — CIMCorp Shipment XML

2-message EAI consume pattern:
  Consumer 1 (isdc topic):        save raw XML blob (Tx 1, always succeeds)
  after_flush_row_event on blob:  publish blob.id to isdc_processed topic
  Consumer 2 (isdc_processed):    parse + persist shipment graph (Tx 2)

Replace-on-duplicate policy:
  Match existing Shipment by local_shipment_oid_nbr.
  If duplicate found: PRAGMA foreign_keys ON, delete prior graph, insert replacement.
"""

import json
import logging

import safrs

logger = logging.getLogger('integration.kafka')


# ---------------------------------------------------------------------------
# Tx 2: parse + persist (used by both Consumer 2 and debug endpoint)
# ---------------------------------------------------------------------------

def process_isdc_payload(xml_text: str, session) -> dict:
    """
    Parse XML, apply replace-on-duplicate policy, persist shipment graph.
    Returns a summary dict for logging/API response.
    """
    from integration import IsdcMapper
    from database import models

    shipment_row = IsdcMapper.parse(xml_text)
    oid_nbr = shipment_row.local_shipment_oid_nbr

    existing = session.query(models.Shipment).get(oid_nbr)
    if existing is not None:
        logger.info(f'isdc: replace-on-duplicate — deleting prior Shipment {oid_nbr}')
        # Explicitly remove ShipmentCommodity (composite PK — passive_deletes='all' needs PRAGMA
        # which is unreliable per-connection; direct delete is simpler and guaranteed)
        session.query(models.ShipmentCommodity).filter_by(
            local_shipment_oid_nbr=oid_nbr
        ).delete(synchronize_session='fetch')
        session.delete(existing)
        session.flush()

    session.add(shipment_row)
    session.flush()

    summary = {
        'success': True,
        'awb_nbr': shipment_row.awb_nbr,
        'local_shipment_oid_nbr': oid_nbr,
        'pieces': len(shipment_row.PieceList),
        'parties': len(shipment_row.ShipmentPartyList),
        'commodities': len(shipment_row.ShipmentCommodityList),
        'special_handling': len(shipment_row.SpecialHandlingList),
        'duplicate_replaced': existing is not None,
    }
    logger.info(f'isdc: processed {summary}')
    return summary


# ---------------------------------------------------------------------------
# Consumer registration
# ---------------------------------------------------------------------------

def register(bus):

    @bus.handle('isdc')
    def handle_isdc(msg, safrs_api):
        """Consumer 1 — save raw XML blob (Tx 1). Logic event publishes to isdc_processed."""
        from database import models

        xml_text = msg.value().decode('utf-8')
        logger.info(f'isdc Consumer 1: received message len={len(xml_text)}')

        with safrs_api.app.app_context():
            db = safrs.DB
            session = db.session
            try:
                blob = models.ShipmentXml(payload=xml_text)
                session.add(blob)
                session.commit()
                logger.info(f'isdc Consumer 1: blob saved id={blob.id}')
            except Exception as exc:
                session.rollback()
                logger.error(f'isdc Consumer 1: blob save failed: {exc}')

    @bus.handle('isdc_processed')
    def handle_isdc_processed(msg, safrs_api):
        """Consumer 2 — parse + persist from blob (Tx 2)."""
        from database import models

        try:
            payload = json.loads(msg.value().decode('utf-8'))
            blob_id = payload.get('id')
        except Exception as exc:
            logger.error(f'isdc Consumer 2: bad message format: {exc}')
            return

        if blob_id is None:
            logger.error('isdc Consumer 2: message missing "id" key')
            return

        logger.info(f'isdc Consumer 2: processing blob id={blob_id}')

        with safrs_api.app.app_context():
            db = safrs.DB
            session = db.session
            try:
                blob = session.query(models.ShipmentXml).get(blob_id)
                if blob is None:
                    logger.error(f'isdc Consumer 2: blob {blob_id} not found')
                    return
                if blob.is_processed:
                    logger.info(f'isdc Consumer 2: blob {blob_id} already processed — skip')
                    return

                process_isdc_payload(blob.payload, session)
                blob.is_processed = 1
                session.commit()
                logger.info(f'isdc Consumer 2: committed blob {blob_id}')
            except Exception as exc:
                session.rollback()
                logger.error(f'isdc Consumer 2: failed blob {blob_id}: {exc}', exc_info=True)
