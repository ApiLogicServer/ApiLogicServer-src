"""
IsdcMapper — CIMCorp shipment XML -> Shipment + Piece + ShipmentParty + ShipmentCommodity + SpecialHandling.

Field mappings per docs/requirements/customs_demo/message_formats/Classify_Entity_Details.csv
(Tier 1 auto lowercase(field) -> column). Sections mawbAsgmt, mawb, currencies,
virtualRouteLegs, extraData have no corresponding target table in this schema and are skipped.
"""
import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

TAG_ROUTING = {
    "shipment":             (models.Shipment, {}),
    "consignee":            (models.ShipmentParty, {}),
    "shipper":              (models.ShipmentParty, {}),
    "piece":                (models.Piece, {}),
    "commodities":          (models.ShipmentCommodity, {}),
    "specialHandlingCodes": (models.SpecialHandling, {}),
    # ADD additional section tags here
}


def _normalize_party_pk(row: models.ShipmentParty, element):
    """ShipmentParty custom mapping: normalize sentinel PARTY_OID_NBR=0 to None so DB
    autoincrement assigns a unique PK (both consignee and shipper can carry placeholder 0)."""
    if row.shipment_party_oid_nbr == 0:
        row.shipment_party_oid_nbr = None


def parse(payload: str) -> tuple:
    """Returns (parent_row, list[model_instance]) — plain model rows, routed by class
    in process_isdc_payload (not a single homogeneous child list — multiple child tables)."""
    root = ET.fromstring(payload)
    parent = None
    children = []
    for section in root:
        tag = _local(section.tag)
        if tag not in TAG_ROUTING:
            continue
        model_class, overrides = TAG_ROUTING[tag]
        row = model_class()
        custom = _normalize_party_pk if model_class is models.ShipmentParty else None
        populate_row(row, section, overrides=overrides, custom=custom)
        if tag == "shipment":
            parent = row
        else:
            children.append(row)
    return parent, children
