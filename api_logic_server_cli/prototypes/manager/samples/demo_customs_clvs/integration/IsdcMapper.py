"""
Feature: Subscribe to Kafka and persist shipments

ISDC shipment mapper: CIMCorp shipment XML -> Shipment, Piece, ShipmentParty, ShipmentCommodity model rows.

Mapping contract (docs/requirements/customs_demo/message_formats/Classify_Entity_Details.csv, "Classify Storage - USE"):
  Tier 1: lowercase(XML element name) -> column name, when the column exists on the model
  Tier 2: exceptions below (placeholder ids)
Sections not stored: mawbAsgmt, mawb, currencies, specialHandlingCodes, virtualRouteLegs, extraData (see ad-libs.md).
"""
import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

# section tag -> (model class, forced column values)
TAG_ROUTING = {
    "shipment":    (models.Shipment, {}),
    "consignee":   (models.ShipmentParty, {}),
    "shipper":     (models.ShipmentParty, {}),
    "piece":       (models.Piece, {}),
    "commodities": (models.ShipmentCommodity, {}),
}


def _normalize_party(party_row, element):
    """ShipmentParty mapper: placeholder party ids (PARTY_OID_NBR = 0) must never reach the local primary key."""
    if party_row.shipment_party_oid_nbr in (0, None):
        party_row.shipment_party_oid_nbr = None   # DB autoincrement assigns a unique key


def parse(payload: str, exceptions: dict = None) -> tuple:
    """ISDC mapper: returns (shipment_row, [child model rows]) - plain rows, not (row, src) tuples."""
    root = ET.fromstring(payload)
    shipment = None
    children = []
    for section in root:
        tag = _local(section.tag)
        if tag not in TAG_ROUTING:
            continue
        model_class, overrides = TAG_ROUTING[tag]
        row = model_class()
        custom = _normalize_party if model_class is models.ShipmentParty else None
        populate_row(row, section, exceptions=exceptions, overrides=overrides, custom=custom)
        if tag == "shipment":
            shipment = row
        else:
            children.append(row)
    if shipment is None:
        raise ValueError("message has no <shipment> section")
    return shipment, children
