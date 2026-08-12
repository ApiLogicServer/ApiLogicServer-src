"""
Scenario: Shipment at or below the LVS threshold is eligible
  Given a shipment imported by an authorized CLVS courier
  And the shipment has an estimated value for duty not exceeding CAD $3,300
  And the shipment has no prohibited commodity lines (ShipmentCommodity.is_prohibited = 1)
  And the shipment has no controlled or regulatory goods (lookup using first ten digits of the harmonized tariff number)
  And the shipment is released at a CBSA-designated customs office
  When the shipment eligibility is evaluated
  Then the shipment shall be eligible for the CLVS Program
  And set the clvs_reason as a comma delimited list of short all reasons why failed (or blank)
"""
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _set_customs_office(row: models.Shipment, old_row, logic_row: LogicRow):
    """Shipment event: looks up CustomsOffice by planned_clearance_location_cd == office_code
    and sets customs_office_id before Row Logic formulas evaluate CLVS eligibility."""
    location_cd = row.planned_clearance_location_cd
    if not location_cd:
        return
    office = logic_row.session.query(models.CustomsOffice).filter(
        models.CustomsOffice.office_code == location_cd).first()
    if office is not None:
        row.customs_office_id = office.id


def _set_controlled_good(row: models.ShipmentCommodity, old_row, logic_row: LogicRow):
    """ShipmentCommodity event: looks up ControlledRegulatedGood by the harmonized_tariff_nbr
    prefix (matched to the lookup table's stored precision) and sets controlled_regulated_goods_id
    before Rule.count aggregates it on Shipment."""
    tariff_nbr = row.harmonized_tariff_nbr
    if not tariff_nbr:
        return
    digits = ''.join(ch for ch in tariff_nbr if ch.isdigit())
    if len(digits) < 8:
        return
    prefix = digits[:8]
    formatted_hs_code = f"{prefix[0:4]}.{prefix[4:6]}.{prefix[6:8]}"
    match = logic_row.session.query(models.ControlledRegulatedGood).filter(
        models.ControlledRegulatedGood.hs_code == formatted_hs_code).first()
    if match is not None:
        row.controlled_regulated_goods_id = match.id


def _is_prohibited(row, old_row, logic_row):
    """Derive is_prohibited: 1 if the commodity line carries a hazardous material code, else 0."""
    hazmat_cd = row.hazardous_material_cd
    return 1 if hazmat_cd else 0


def _clvs_reason(row, old_row, logic_row):
    """Derive clvs_reason: comma-delimited list of CLVS ineligibility reasons (blank if eligible)."""
    reasons = []
    courier_ok = row.authorized_clvs_courier
    if courier_ok != 1:
        reasons.append("not an authorized CLVS courier")
    value_amt = row.local_customs_value_amt
    threshold = row.clvs_lvs_threshold_cad
    if value_amt is not None and threshold is not None and value_amt > threshold:
        reasons.append(f"value for duty {value_amt} exceeds CLVS threshold {threshold}")
    prohibited_count = row.prohibited_commodity_count
    if prohibited_count and prohibited_count > 0:
        reasons.append(f"{prohibited_count} prohibited commodity line(s)")
    controlled_count = row.controlled_item_count
    if controlled_count and controlled_count > 0:
        reasons.append(f"{controlled_count} controlled or regulated goods line(s)")
    office_id = row.customs_office_id
    if office_id is None:
        reasons.append("not released at a CBSA-designated customs office")
    else:
        office = logic_row.session.query(models.CustomsOffice).get(office_id)
        if office is None or office.clvs_release != 1:
            reasons.append("not released at a CBSA-designated customs office")
    return ", ".join(reasons)


def declare_logic():
    Rule.early_row_event(on_class=models.Shipment, calling=_set_customs_office)
    Rule.early_row_event(on_class=models.ShipmentCommodity, calling=_set_controlled_good)

    Rule.copy(derive=models.Shipment.clvs_lvs_threshold_cad, from_parent=models.SysConfig.clvs_lvs_threshold_cad)

    Rule.formula(derive=models.ShipmentCommodity.is_prohibited, calling=_is_prohibited)

    Rule.count(derive=models.Shipment.prohibited_commodity_count, as_count_of=models.ShipmentCommodity,
               where=lambda row: row.is_prohibited == 1)
    Rule.count(derive=models.Shipment.controlled_item_count, as_count_of=models.ShipmentCommodity,
               where=lambda row: row.controlled_regulated_goods_id is not None)

    Rule.formula(derive=models.Shipment.clvs_reason, calling=_clvs_reason)
    Rule.formula(derive=models.Shipment.clvs_eligible, as_expression=lambda row: 1 if row.clvs_reason == "" else 0)
