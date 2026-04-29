"""
IsdcMapper — XML mapper for the CIMCorpShipment / isdc Kafka topic.

Maps ns2:CIMCorpShipment XML sections to:
  Shipment        ← ns2:shipment  (parent)
  ShipmentParty   ← ns2:consignee, ns2:shipper
  Piece           ← ns2:piece
  ShipmentCommodity ← ns2:commodities
  SpecialHandling ← ns2:specialHandlingCodes
  VirtualRouteLeg ← ns2:virtualRouteLegs  (stored as-is, no FK to Shipment)

Sections skipped (no matching table): ns2:mawbAsgmt, ns2:mawb, ns2:currencies, ns2:extraData
"""

import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

# Fields that require special handling — skip or remap
SHIPMENT_EXCEPTIONS: dict = {
    "LOCAL_SHIPMENT_OID_NBR": None,   # used as PK — set via custom callback, not auto
}

PARTY_EXCEPTIONS: dict = {
    "PARTY_OID_NBR": None,   # sentinel placeholder; PK normalized to None in custom callback
    "LOCAL_SHIPMENT_OID_NBR": None,   # FK set by parent relationship append
}

PIECE_EXCEPTIONS: dict = {
    "LOCAL_PIECE_OID_NBR": None,      # PK — set via custom callback
    "LOCAL_SHIPMENT_OID_NBR": None,   # FK set by parent relationship append
}

COMMODITY_EXCEPTIONS: dict = {
    "LOCAL_SHIPMENT_OID_NBR": None,   # FK set by parent relationship append
}

SPECIAL_HANDLING_EXCEPTIONS: dict = {
    "OID_NBR": None,   # FK set by parent relationship append
}

VIRTUAL_ROUTE_LEG_EXCEPTIONS: dict = {}


def _find_local(element, local_name: str):
    """Find first child whose local name (namespace stripped) matches local_name."""
    for child in element:
        if _local(child.tag) == local_name:
            return child
    return None


def _shipment_custom(row: models.Shipment, element):
    """Set shipment PK from LOCAL_SHIPMENT_OID_NBR element."""
    el = _find_local(element, "LOCAL_SHIPMENT_OID_NBR")
    if el is not None and el.text:
        try:
            row.local_shipment_oid_nbr = int(el.text)
        except (ValueError, TypeError):
            pass


def _piece_custom(row: models.Piece, element):
    """Set piece PK from LOCAL_PIECE_OID_NBR; normalize 0 → None."""
    el = _find_local(element, "LOCAL_PIECE_OID_NBR")
    if el is not None and el.text:
        try:
            val = int(el.text)
            row.local_piece_oid_nbr = None if val == 0 else val
        except (ValueError, TypeError):
            row.local_piece_oid_nbr = None


def _party_custom(row: models.ShipmentParty, element):
    """Normalize PARTY_OID_NBR sentinel 0 → None so autoincrement assigns PK."""
    el = _find_local(element, "PARTY_OID_NBR")
    if el is not None and el.text:
        try:
            val = int(el.text)
            row.shipment_party_oid_nbr = None if val == 0 else val
        except (ValueError, TypeError):
            row.shipment_party_oid_nbr = None
    else:
        row.shipment_party_oid_nbr = None
    # Map SHIPMENT_PARTY_TYPE_CD (already handled by Tier 1 auto, but ensure it's set)
    el2 = _find_local(element, "SHIPMENT_PARTY_TYPE_CD")
    if el2 is not None and el2.text:
        row.shipment_party_type_cd = el2.text.strip()


def _commodity_sequence(row: models.ShipmentCommodity, element):
    el = element.find("SEQUENCE_NBR")
    if el is not None and el.text:
        try:
            row.sequence_nbr = int(el.text)
        except (ValueError, TypeError):
            pass


# Section tag → (model class, exceptions, custom callback)
TAG_ROUTING = {
    "shipment":            (models.Shipment,           SHIPMENT_EXCEPTIONS,       _shipment_custom),
    "consignee":           (models.ShipmentParty,      PARTY_EXCEPTIONS,          _party_custom),
    "shipper":             (models.ShipmentParty,      PARTY_EXCEPTIONS,          _party_custom),
    "piece":               (models.Piece,              PIECE_EXCEPTIONS,          _piece_custom),
    "commodities":         (models.ShipmentCommodity,  COMMODITY_EXCEPTIONS,      _commodity_sequence),
    "specialHandlingCodes":(models.SpecialHandling,    SPECIAL_HANDLING_EXCEPTIONS, None),
    "virtualRouteLegs":    (models.VirtualRouteLeg,    VIRTUAL_ROUTE_LEG_EXCEPTIONS, None),
}

# Sections whose rows are attached to shipment.ChildList
SHIPMENT_CHILDREN = {
    "consignee":           "ShipmentPartyList",
    "shipper":             "ShipmentPartyList",
    "piece":               "PieceList",
    "commodities":         "ShipmentCommodityList",
    "specialHandlingCodes":"SpecialHandlingList",
}


def parse(payload: str, exceptions: dict = None) -> tuple:
    """
    Parse CIMCorpShipment XML.

    Returns:
        (shipment_row, extras)
        - shipment_row: models.Shipment with child lists populated via relationship
        - extras: list of models.VirtualRouteLeg rows (no FK to Shipment in schema)
    """
    root = ET.fromstring(payload)
    shipment_row = None
    extras = []

    for section in root:
        tag = _local(section.tag)
        if tag not in TAG_ROUTING:
            continue
        model_class, exc, custom_fn = TAG_ROUTING[tag]
        row = model_class()
        populate_row(row, section, exceptions=exc, custom=custom_fn)

        if tag == "shipment":
            shipment_row = row
        elif tag in SHIPMENT_CHILDREN and shipment_row is not None:
            child_list = getattr(shipment_row, SHIPMENT_CHILDREN[tag])
            child_list.append(row)
        elif tag == "virtualRouteLegs":
            extras.append(row)

    if shipment_row is None:
        raise ValueError("IsdcMapper.parse: no <ns2:shipment> section found in payload")

    return shipment_row, extras
