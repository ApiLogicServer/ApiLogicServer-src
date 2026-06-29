"""
CIMCorp ISDC XML Mapper
========================
Parses ns2:CIMCorpShipment XML into SQLAlchemy model graph.

TAG_ROUTING:
  ns2:shipment              → Shipment (parent row)
  ns2:consignee             → ShipmentParty (type C)
  ns2:shipper               → ShipmentParty (type S)
  ns2:piece                 → Piece
  ns2:commodities           → ShipmentCommodity (repeating)
  ns2:specialHandlingCodes  → SpecialHandling (repeating)
  ns2:extraData             → Shipment key-value overlay
  ns2:currencies, ns2:mawbAsgmt, ns2:mawb, ns2:virtualRouteLegs, ns2:messageMetadata → skip

SOURCE-PK normalization:
  ShipmentParty.PARTY_OID_NBR = 0  →  set to None (DB autoincrement assigns PK)
"""

import re
import xml.etree.ElementTree as ET

from integration.system.EaiSubscribeMapper import populate_row

# Maps ns2:extraData dataName → Shipment column name
_EXTRA_DATA_MAP = {
    'AdmissibilityModeNm':  'admissibility_mode',
    'CargoControlNbr':       'cargocontrolnbr',
    'PortOfEntryNm':         'portofentry',
    'WarehouseCode':         'warehousecode',
}

# Tier 2 exception dicts ─────────────────────────────────────────────────────

_SHIPMENT_EXCEPTIONS = {}   # Tier 1 auto-map sufficient for all shipment fields

_PARTY_EXCEPTIONS = {
    'PARTY_OID_NBR': 'shipment_party_oid_nbr',  # auto-map gives wrong column name
    'OID_NBR':       None,                       # FK set via relationship
}

_PIECE_EXCEPTIONS = {
    'LOCAL_SHIPMENT_OID_NBR': None,  # FK set via relationship
}

_COMMODITY_EXCEPTIONS = {
    'COMMODITY_OID_NBR': None,  # no column
    # LOCAL_SHIPMENT_OID_NBR is kept: auto-maps to local_shipment_oid_nbr (composite PK part)
}

_SPECIAL_HANDLING_EXCEPTIONS = {
    'OID_NBR':      None,   # FK set via relationship (oid_nbr)
    'OID_TYPE_CD':  None,   # informational only
}


def _local(tag: str) -> str:
    return re.sub(r"\{[^}]*\}", "", tag)


def _normalize_party_oid(row, element):
    """Normalize PARTY_OID_NBR sentinel 0 → None so DB autoincrement assigns PK."""
    if row.shipment_party_oid_nbr == 0:
        row.shipment_party_oid_nbr = None


def _apply_extra_data(shipment_row, element):
    """Map ns2:extraData key-value pairs to Shipment columns."""
    name_el = element.find('dataName')
    value_el = element.find('dataValue')
    if name_el is None or value_el is None:
        return
    name = (name_el.text or '').strip()
    value = (value_el.text or '').strip() or None
    col = _EXTRA_DATA_MAP.get(name)
    if col and hasattr(shipment_row, col):
        setattr(shipment_row, col, value)


def parse(xml_text: str):
    """
    Parse CIMCorp XML text and return a Shipment row with children attached.

    Children are appended via relationship (not session.add) per EAI CE rule 4b.
    Caller is responsible for session.add(shipment_row) and session.flush().
    """
    from database import models

    root = ET.fromstring(xml_text)
    shipment_row = models.Shipment()

    for element in root:
        tag = _local(element.tag)

        if tag == 'shipment':
            populate_row(shipment_row, element, _SHIPMENT_EXCEPTIONS)

        elif tag in ('consignee', 'shipper'):
            party = models.ShipmentParty()
            populate_row(party, element, _PARTY_EXCEPTIONS, custom=_normalize_party_oid)
            shipment_row.ShipmentPartyList.append(party)

        elif tag == 'piece':
            piece = models.Piece()
            populate_row(piece, element, _PIECE_EXCEPTIONS)
            shipment_row.PieceList.append(piece)

        elif tag == 'commodities':
            commodity = models.ShipmentCommodity()
            populate_row(commodity, element, _COMMODITY_EXCEPTIONS)
            shipment_row.ShipmentCommodityList.append(commodity)

        elif tag == 'specialHandlingCodes':
            sh = models.SpecialHandling()
            populate_row(sh, element, _SPECIAL_HANDLING_EXCEPTIONS)
            shipment_row.SpecialHandlingList.append(sh)

        elif tag == 'extraData':
            _apply_extra_data(shipment_row, element)

        # skip: messageMetadata, mawbAsgmt, mawb, currencies, virtualRouteLegs

    return shipment_row
