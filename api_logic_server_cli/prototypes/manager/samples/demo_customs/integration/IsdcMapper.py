"""
ISDC XML Mapper — CIMCorpShipment → Shipment domain graph.

Parses the CIMCorpShipment XML format (Kafka topic: isdc) into a Shipment parent row
plus child rows (ShipmentParty, Piece, ShipmentCommodity, SpecialHandling, VirtualRouteLeg).

Mapping contract (3-tier):
  Tier 1: lowercase(XML_FIELD_NAME) → model column name  (handles ~90% of fields)
  Tier 2: ISDC_EXCEPTIONS dict       → skip (None) or remap (str)
  Tier 3: custom_mapping callback    → extraData key-value block → Shipment attributes

SOURCE-PK normalization: PARTY_OID_NBR == 0 is a sentinel placeholder.
  Both consignee and shipper carry PARTY_OID_NBR=0 in typical payloads.
  Normalised to None so DB autoincrement assigns unique PKs.
"""

import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

# ExtraData <dataName> → Shipment column
_EXTRA_DATA_MAP = {
    "AdmissibilityModeNm":     "admissibility_mode",
    "PrevAdmissibilityModeNm": "prev_admissibility_mode",
    "CargoControlNbr":         "cargocontrolnbr",
    "PortOfExitNm":            "portofexit",
    "PortOfEntryNm":           "portofentry",
    "WarehouseCd":             "warehousecode",
    "SurfaceIntlShipmentNbr":  "surface_intl_shipment_nbr",
}

# Tier 2 exceptions — fields that cannot be auto-mapped by lowercase alone
ISDC_EXCEPTIONS: dict[str, str | None] = {
    # No remaps needed — Tier 1 handles all standard fields in the CIMCorp schema
}

# XML section tag → model class (shipment handled specially as parent)
TAG_ROUTING = {
    "shipment":             models.Shipment,
    "consignee":            models.ShipmentParty,
    "shipper":              models.ShipmentParty,
    "piece":                models.Piece,
    "commodities":          models.ShipmentCommodity,
    "specialHandlingCodes": models.SpecialHandling,
    "virtualRouteLegs":     models.VirtualRouteLeg,
}


def parse(payload: str, exceptions: dict = None) -> tuple:
    """
    Returns (shipment_row, list[child_rows]) — plain model instances, NOT tuples.

    child_rows contains: ShipmentParty (×2), Piece, ShipmentCommodity(s),
    SpecialHandling(s), VirtualRouteLeg(s).
    Caller attaches each child to the appropriate parent list.
    """
    exc = exceptions if exceptions is not None else ISDC_EXCEPTIONS
    root = ET.fromstring(payload)
    parent = None
    extras = []

    for section in root:
        tag = _local(section.tag)
        if tag == "extraData":
            continue   # processed below after parent is built
        if tag not in TAG_ROUTING:
            continue

        model_class = TAG_ROUTING[tag]
        row = model_class()
        populate_row(row, section, exceptions=exc)

        # SOURCE-PK normalization: sentinel PARTY_OID_NBR=0 → None (let DB assign PK)
        if model_class is models.ShipmentParty:
            if getattr(row, 'shipment_party_oid_nbr', 0) in (0, None, "0"):
                row.shipment_party_oid_nbr = None

        if model_class is models.Shipment:
            parent = row
        else:
            extras.append(row)

    # Apply extraData key-value pairs back onto the parent Shipment
    if parent is not None:
        for section in root:
            if _local(section.tag) != "extraData":
                continue
            name_el = section.find("dataName")
            val_el  = section.find("dataValue")
            if name_el is None or val_el is None:
                continue
            col = _EXTRA_DATA_MAP.get(name_el.text or "")
            if col and hasattr(parent, col) and val_el.text:
                setattr(parent, col, val_el.text)

    return parent, extras
