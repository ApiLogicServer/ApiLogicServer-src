"""
ISDC (CIMCorp Shipment) XML Mapper

Parses CIMCorp shipment XML into domain rows:
  Shipment  + Piece + ShipmentParty (consignee, shipper) +
  ShipmentCommodity + SpecialHandling + VirtualRouteLeg

Returns: (shipment_row, children_dict)
  children_dict keys: 'pieces', 'parties', 'commodities', 'special_handling', 'route_legs'
"""

import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

# Fields to skip when mapping to Shipment (set by logic or relationship)
_SHIPMENT_EXCEPTIONS = {
    'DUPLICATE_SHIPMENT_RECORD_FLG': None,
}

# Extra-data name → Shipment column
_EXTRA_DATA_MAP = {
    'AdmissibilityModeNm':      'admissibility_mode',
    'PrevAdmissibilityModeNm':  'prev_admissibility_mode',
    'CargoControlNbr':          'cargocontrolnbr',
    'PortOfExitNm':             'portofexit',
    'PortOfEntryNm':            'portofentry',
    'WarehouseCd':              'warehousecode',
    'SurfaceIntlShipmentNbr':   'surface_intl_shipment_nbr',
}

# FK columns to skip on children (set by relationship attachment)
_PIECE_EXCEPTIONS = {
    'LOCAL_SHIPMENT_OID_NBR': None,
}

_PARTY_EXCEPTIONS = {
    'OID_NBR': None,           # FK set by relationship
    'OID_TYPE_CD': None,       # not in ShipmentParty model columns we care about
}

_COMMODITY_EXCEPTIONS = {
    'LOCAL_SHIPMENT_OID_NBR': None,
    'COMMODITY_OID_NBR': None,
}

_SPECIAL_HANDLING_EXCEPTIONS = {
    'OID_NBR': None,           # FK set by relationship
}


def parse(payload: str, exceptions: dict = None):
    """
    Parse CIMCorp XML payload.
    Returns (shipment_row, children_dict).
    """
    root = ET.fromstring(payload)
    shipment_row = models.Shipment()

    children = {
        'pieces': [],
        'parties': [],
        'commodities': [],
        'special_handling': [],
        'route_legs': [],
    }

    for section in root:
        tag = _local(section.tag)

        if tag == 'shipment':
            populate_row(shipment_row, section, exceptions=_SHIPMENT_EXCEPTIONS)

        elif tag in ('consignee', 'shipper'):
            party = models.ShipmentParty()
            populate_row(party, section, exceptions=_PARTY_EXCEPTIONS)
            # Normalize placeholder PK (PARTY_OID_NBR=0 → None so autoincrement fires)
            if party.shipment_party_oid_nbr in (0, None):
                party.shipment_party_oid_nbr = None
            children['parties'].append(party)

        elif tag == 'piece':
            piece = models.Piece()
            populate_row(piece, section, exceptions=_PIECE_EXCEPTIONS)
            children['pieces'].append(piece)

        elif tag == 'commodities':
            commodity = models.ShipmentCommodity()
            populate_row(commodity, section, exceptions=_COMMODITY_EXCEPTIONS)
            children['commodities'].append(commodity)

        elif tag == 'specialHandlingCodes':
            sh = models.SpecialHandling()
            populate_row(sh, section, exceptions=_SPECIAL_HANDLING_EXCEPTIONS)
            children['special_handling'].append(sh)

        elif tag == 'virtualRouteLegs':
            leg = models.VirtualRouteLeg()
            populate_row(leg, section)
            children['route_legs'].append(leg)

        elif tag == 'extraData':
            _apply_extra_data(section, shipment_row)

        # mawbAsgmt, mawb, currencies, messageMetadata: skip

    return shipment_row, children


def _apply_extra_data(section, shipment_row):
    """Map <extraData> key-value pairs to Shipment columns."""
    name_el = section.find('dataName')
    value_el = section.find('dataValue')
    if name_el is None or value_el is None:
        return
    col = _EXTRA_DATA_MAP.get((name_el.text or '').strip())
    if col and value_el.text:
        setattr(shipment_row, col, value_el.text.strip())
