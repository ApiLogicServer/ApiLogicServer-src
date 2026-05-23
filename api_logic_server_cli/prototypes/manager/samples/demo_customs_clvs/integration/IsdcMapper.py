"""
IsdcMapper — CIMCorp Shipment XML → Shipment domain rows.

Parses one ns2:CIMCorpShipment XML message into:
  parent_row : models.Shipment
  children   : list of [Piece, ShipmentCommodity, ShipmentParty (C/S), SpecialHandling, VirtualRouteLeg]

Returns (parent_row, children) — plain model rows, NOT (row, src_dict) tuples.
The caller (process_isdc_payload) attaches children to parent relationship lists.
"""
import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

# ---------------------------------------------------------------------------
# FIELD_EXCEPTIONS — xml-tag → None (skip) or "col_name" (remap)
# ---------------------------------------------------------------------------

SHIPMENT_EXCEPTIONS = {
    "LOCAL_SHIPMENT_OID_NBR": None,     # set as PK directly in parse()
    "PLANNED_CLEARANCE_LOCATION_CD": "planned_clearance_location_cd",
    "SHIPMENT_DESC": "shipment_desc",
    "SHIPMENT_CONTROL_NBR": "shipment_control_nbr",
    "DIM_SHIPMENT_FLG": "dim_shipment_flg",
    "SPLIT_SHIPMENT_FLG": "split_shipment_flg",
}

PARTY_EXCEPTIONS = {
    "PARTY_OID_NBR": None,          # sentinel 0 — normalized to None; DB assigns autoincrement PK
    "OID_NBR": None,                # internal OID — not a model column
    "OID_TYPE_CD": "oid_type_cd",
    "SHIPMENT_PARTY_TYPE_CD": "shipment_party_type_cd",
    "LOCAL_SHIPMENT_OID_NBR": None, # set via relationship
}

PIECE_EXCEPTIONS = {
    "LOCAL_PIECE_OID_NBR": None,    # set as PK directly
    "LOCAL_SHIPMENT_OID_NBR": None, # set via relationship
}

COMMODITY_EXCEPTIONS = {
    "LOCAL_SHIPMENT_OID_NBR": None, # set via relationship
    "SEQUENCE_NBR": None,           # set as composite PK directly
}

SPECIAL_HANDLING_EXCEPTIONS = {
    "OID_NBR": "oid_nbr",
    "OID_TYPE_CD": "oid_type_cd",
    "SPECIAL_HANDLING_CD": "special_handling_cd",
    "SHIPMENT_TYPE_CD": "shipment_type_cd",
}

VIRTUAL_ROUTE_EXCEPTIONS: dict = {}   # all column names match via Tier 1 auto-mapping


def parse(payload: str, exceptions: dict = None):
    """
    Parse CIMCorp shipment XML.

    Returns (shipment_row, children_list) where children_list contains
    Piece, ShipmentCommodity, ShipmentParty (C, S) and SpecialHandling rows.
    VirtualRouteLeg rows are standalone — returned via children_list with
    caller responsible for separate session.add() (no FK to Shipment).

    PARTY_OID_NBR sentinel 0 is normalized to None so DB assigns a unique PK.
    """
    root = ET.fromstring(payload)
    ns_shipment = "http://cim.corp.ship"

    # ---- Locate ns2:shipment element ----
    shipment_el = root.find(f"{{{ns_shipment}}}shipment")
    if shipment_el is None:
        raise ValueError("No ns2:shipment element found in payload")

    # Read LOCAL_SHIPMENT_OID_NBR
    raw_id = _get_text(shipment_el, "LOCAL_SHIPMENT_OID_NBR")
    if raw_id is None:
        raise ValueError("LOCAL_SHIPMENT_OID_NBR missing from shipment element")
    local_shipment_oid = int(raw_id)

    shipment_row = models.Shipment()
    shipment_row.local_shipment_oid_nbr = local_shipment_oid
    populate_row(shipment_row, shipment_el, exceptions=SHIPMENT_EXCEPTIONS)

    children = []

    for section in root:
        tag = _local(section.tag)

        if tag == "consignee" or tag == "shipper":
            party_row = models.ShipmentParty()
            populate_row(party_row, section, exceptions=PARTY_EXCEPTIONS)
            # Normalize placeholder sentinel ID → None so DB autoincrement assigns unique PK
            if party_row.shipment_party_oid_nbr in (0, None):
                party_row.shipment_party_oid_nbr = None
            children.append(party_row)

        elif tag == "piece":
            piece_row = models.Piece()
            raw_piece_id = _get_text(section, "LOCAL_PIECE_OID_NBR")
            if raw_piece_id:
                piece_row.local_piece_oid_nbr = int(raw_piece_id)
            populate_row(piece_row, section, exceptions=PIECE_EXCEPTIONS)
            children.append(piece_row)

        elif tag == "commodities":
            comm_row = models.ShipmentCommodity()
            raw_seq = _get_text(section, "SEQUENCE_NBR")
            if raw_seq:
                comm_row.sequence_nbr = int(raw_seq)
            comm_row.local_shipment_oid_nbr = local_shipment_oid
            populate_row(comm_row, section, exceptions=COMMODITY_EXCEPTIONS)
            children.append(comm_row)

        elif tag == "specialHandlingCodes":
            sh_row = models.SpecialHandling()
            populate_row(sh_row, section, exceptions=SPECIAL_HANDLING_EXCEPTIONS)
            children.append(sh_row)

        elif tag == "virtualRouteLegs":
            vrl_row = models.VirtualRouteLeg()
            populate_row(vrl_row, section, exceptions=VIRTUAL_ROUTE_EXCEPTIONS)
            children.append(vrl_row)

        # mawbAsgmt, mawb, currencies, extraData, messageMetadata — skip

    return shipment_row, children


def _get_text(element: ET.Element, local_name: str):
    """Return text of first direct child with the given local name, or None."""
    for child in element:
        if _local(child.tag) == local_name:
            return child.text.strip() if child.text and child.text.strip() else None
    return None
