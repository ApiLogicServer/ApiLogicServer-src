"""
IsdcMapper — CIMCorp Shipment XML → DB mapper for the isdc Kafka topic.

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc consumer
       reads message, inserts raw payload into ShipmentXml blob (Tx 1)
  2. logic/logic_discovery/isdc_consume.py
       insert → publishes payload to topic: isdc_processed
  3. integration/kafka/kafka_subscribe_discovery/isdc.py  - isdc_processed consumer
       parses payload → domain rows (LogicBank rules fire in Tx 2)
  4. api/api_discovery/isdc_kafka_consume_debug.py
       /consume_debug/isdc bypasses Kafka, calls same parse function directly

XML sections → tables:
  ns2:shipment          → Shipment (parent)
  ns2:consignee         → ShipmentParty (attached to PieceList[0] or shipment)
  ns2:shipper           → ShipmentParty
  ns2:piece             → Piece
  ns2:commodities       → ShipmentCommodity
  ns2:specialHandlingCodes → SpecialHandling
  (mawbAsgmt, mawb, currencies, virtualRouteLegs, extraData, messageMetadata skipped)
"""
import re
import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

# Tier 2 exceptions: None=skip, str=remap to model column name
SHIPMENT_EXCEPTIONS = {
    'FEDEX_ASSIGNED_MAWB_NBR': 'carrier_assigned_mawb_nbr',
}

PARTY_EXCEPTIONS = {
    'PARTY_OID_NBR': None,      # handled in custom_mapping (normalize 0 → None)
    'OID_NBR': 'local_shipment_oid_nbr',
    'OID_TYPE_CD': None,
    'ADDRESS_1': None,
    'ADDRESS_2': None,
}

COMMODITY_EXCEPTIONS = {
    'COMMODITY_OID_NBR': None,  # skip — no matching column
}

PIECE_EXCEPTIONS = {}

SPECIAL_HANDLING_EXCEPTIONS = {}

# Sections to skip entirely (no matching table or handled separately)
_SKIP_TAGS = frozenset({
    'messageMetadata', 'mawbAsgmt', 'mawb', 'currencies',
    'virtualRouteLegs', 'extraData',
})


def _custom_party(row: models.ShipmentParty, section, logic_row=None):
    """Normalize PARTY_OID_NBR=0 → None so autoincrement assigns unique PK."""
    raw_oid = section.find('PARTY_OID_NBR')
    val = int(raw_oid.text) if (raw_oid is not None and raw_oid.text and raw_oid.text.strip()) else 0
    row.shipment_party_oid_nbr = None if val == 0 else val


def parse(payload: str, exceptions: dict = None) -> tuple:
    """
    Parse CIMCorp shipment XML into (shipment_row, []).

    Children (Piece, ShipmentParty, ShipmentCommodity, SpecialHandling) are
    pre-attached to the shipment's relationship lists.  Returns an empty flat
    list because the caller loop has nothing left to zip.
    """
    root = ET.fromstring(payload)
    shipment = models.Shipment()
    first_piece = None  # piece row for piece-level party FK

    for section in root:
        tag = _local(section.tag)
        if tag in _SKIP_TAGS:
            continue

        if tag == 'shipment':
            populate_row(shipment, section, exceptions=SHIPMENT_EXCEPTIONS)

        elif tag == 'piece':
            piece = models.Piece()
            populate_row(piece, section, exceptions=PIECE_EXCEPTIONS)
            shipment.PieceList.append(piece)
            if first_piece is None:
                first_piece = piece

        elif tag in ('consignee', 'shipper'):
            party = models.ShipmentParty()
            populate_row(party, section, exceptions=PARTY_EXCEPTIONS)
            _custom_party(party, section)
            # Consignee/shipper are shipment-level parties (local_piece_oid_nbr stays None)
            shipment.ShipmentPartyList.append(party)

        elif tag == 'commodities':
            commodity = models.ShipmentCommodity()
            populate_row(commodity, section, exceptions=COMMODITY_EXCEPTIONS)
            shipment.ShipmentCommodityList.append(commodity)

        elif tag == 'specialHandlingCodes':
            sh = models.SpecialHandling()
            populate_row(sh, section, exceptions=SPECIAL_HANDLING_EXCEPTIONS)
            shipment.SpecialHandlingList.append(sh)

    return shipment, []
