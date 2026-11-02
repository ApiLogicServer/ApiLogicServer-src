"""
ISDC mapper: CIMCorp shipment XML -> Shipment graph (Shipment, ShipmentParty, Piece, ShipmentCommodity,
SpecialHandling, VirtualRouteLeg), per message_formats/Classify_Entity_Details.csv.

3-tier contract (EaiSubscribeMapper): Tier 1 lowercase(tag) -> column; Tier 2 exceptions/overrides below;
Tier 3 custom callbacks (extraData name/value pairs, party placeholder keys).
"""
import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

# section tag -> (model class, forced column values)
TAG_ROUTING = {
    "shipment":           (models.Shipment, {}),
    "consignee":          (models.ShipmentParty, {}),
    "shipper":            (models.ShipmentParty, {}),
    "piece":              (models.Piece, {}),
    "commodities":        (models.ShipmentCommodity, {}),
    "specialHandlingCodes": (models.SpecialHandling, {}),
    "virtualRouteLegs":   (models.VirtualRouteLeg, {}),
}

# Tier 2: XML field -> column remap (str) or skip (None)
SHIPMENT_EXCEPTIONS = {}
PARTY_EXCEPTIONS = {"PARTY_OID_NBR": "shipment_party_oid_nbr"}

# <extraData> dataName -> Shipment column (per the CSV)
EXTRA_DATA_MAP = {
    "AdmissibilityModeNm": "admissibility_mode",
    "PrevAdmissibilityModeNm": "prev_admissibility_mode",
    "CargoControlNbr": "cargocontrolnbr",
    "PortOfExitNm": "portofexit",
    "WarehouseCd": "warehousecode",
    "PortOfEntryNm": "portofentry",
    "SurfaceIntlShipmentNbr": "surface_intl_shipment_nbr",
}


def _normalize_party(row, element):
    """Placeholder party OIDs (0) must not become the local PK: let autoincrement assign it."""
    if row.shipment_party_oid_nbr in (0, None):
        row.shipment_party_oid_nbr = None


def parse(payload: str, exceptions: dict = None) -> tuple:
    """Returns (shipment_row, list of child model rows), all attached to nothing yet.
    Plain model rows, NOT (row, src) tuples. Children: ShipmentParty, Piece, ShipmentCommodity,
    SpecialHandling (attached to the shipment by the caller) and VirtualRouteLeg (stored standalone)."""
    root = ET.fromstring(payload)
    shipment = None
    children = []
    extra = []
    for section in root:
        tag = _local(section.tag)
        if tag == "extraData":
            extra.append(section)
            continue
        if tag not in TAG_ROUTING:
            continue                                  # messageMetadata, mawb, mawbAsgmt, currencies: not stored
        model_class, overrides = TAG_ROUTING[tag]
        row = model_class()
        if model_class is models.ShipmentParty:
            populate_row(row, section, exceptions=PARTY_EXCEPTIONS, overrides=overrides, custom=_normalize_party)
        else:
            populate_row(row, section, exceptions=exceptions, overrides=overrides)
        if model_class is models.Shipment:
            shipment = row
        else:
            children.append(row)
    if shipment is None:
        raise ValueError("message has no <shipment> section")
    for el in extra:                                  # Tier 3: name/value pairs
        name = (el.findtext("dataName") or "").strip()
        value = (el.findtext("dataValue") or "").strip() or None
        col = EXTRA_DATA_MAP.get(name)
        if col and value is not None:
            setattr(shipment, col, value)
    return shipment, children
