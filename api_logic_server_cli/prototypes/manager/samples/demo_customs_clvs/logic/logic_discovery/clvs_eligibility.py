"""
Feature: CVLS Eligibility

Scenario: Shipment at or below the LVS threshold is eligible
  Given a shipment imported by an authorized CLVS courier
  And the shipment has an estimated value for duty not exceeding CAD $3,300
  And the shipment has no prohibited commodity lines (ShipmentCommodity.is_prohibited = 1)
  And the shipment has no controlled or regulatory goods (lookup using first ten digits of the harmonized tariff number)
  And the shipment is released at a CBSA-designated customs office
  When the shipment eligibility is evaluated
  Then the shipment shall be eligible for the CLVS Program
  And set the clvs_reason as a comma delimited list of short all reasons why failed (or blank)

version: 1.0
created: 2026-11-01
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
"""
import re
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _digits(text) -> str:
    """digits only of an HS code, e.g. '6110.20.00.01' -> '6110200001'"""
    return re.sub(r"\D", "", text or "")


def _set_customs_office(row: models.Shipment, old_row, logic_row: LogicRow):
    """Shipment event: looks up the CustomsOffice whose location_cd equals the shipment's
    final_import_clearance_loc_cd and sets customs_office_id (FK) before the copy and eligibility rules read it."""
    office = None
    if row.final_import_clearance_loc_cd:
        office = logic_row.session.query(models.CustomsOffice).filter(
            models.CustomsOffice.location_cd == row.final_import_clearance_loc_cd).first()
    row.customs_office_id = office.id if office else None


def _match_controlled_goods(row: models.ShipmentCommodity, old_row, logic_row: LogicRow):
    """ShipmentCommodity event: looks up ControlledRegulatedGood whose HS code is the start of the first ten digits
    of harmonized_tariff_nbr; sets controlled_regulated_goods_id (FK) and is_prohibited (1 if the matched
    good's clvs_reason says prohibited) before the Rule.count rules on Shipment aggregate them."""
    digits = _digits(row.harmonized_tariff_nbr)[:10]
    match = None
    if digits:
        for good in logic_row.session.query(models.ControlledRegulatedGood).all():
            code = _digits(good.hs_code)
            if code and digits.startswith(code):
                match = good
                break
    row.controlled_regulated_goods_id = match.id if match else None
    row.is_prohibited = 1 if (match and "prohibited" in (match.clvs_reason or "").lower()) else 0


def _clvs_reason(row: models.Shipment, old_row, logic_row: LogicRow):
    """Derive clvs_reason: comma-delimited short list of every reason the shipment fails CLVS eligibility (blank if eligible)."""
    reasons = []
    courier_ok = row.service_type_cd == row.clvs_courier_service_type_cd
    if not courier_ok:
        reasons.append("not an authorized CLVS courier")
    if (row.local_customs_value_amt or 0) > (row.clvs_threshold_cad or 0):
        reasons.append("value exceeds CAD threshold")
    if (row.prohibited_commodity_count or 0) > 0:
        reasons.append("prohibited commodity")
    if (row.controlled_item_count or 0) > 0:
        reasons.append("controlled or regulated goods")
    if row.customs_office_id is None:
        reasons.append("release office unknown")
    elif row.office_clvs_release != 1:
        reasons.append("release office not CLVS-designated")
    return ", ".join(reasons)


def declare_logic():
    Rule.copy(derive=models.Shipment.clvs_threshold_cad, from_parent=models.SysConfig.clvs_threshold_cad)
    Rule.copy(derive=models.Shipment.clvs_courier_service_type_cd, from_parent=models.SysConfig.clvs_courier_service_type_cd)
    Rule.early_row_event(on_class=models.Shipment, calling=_set_customs_office)
    Rule.copy(derive=models.Shipment.office_clvs_release, from_parent=models.CustomsOffice.clvs_release)
    Rule.early_row_event(on_class=models.ShipmentCommodity, calling=_match_controlled_goods)
    Rule.count(derive=models.Shipment.prohibited_commodity_count, as_count_of=models.ShipmentCommodity, where=lambda row: row.is_prohibited == 1)
    Rule.count(derive=models.Shipment.controlled_item_count, as_count_of=models.ShipmentCommodity, where=lambda row: row.controlled_regulated_goods_id is not None)
    Rule.formula(derive=models.Shipment.clvs_reason, calling=_clvs_reason)
    Rule.formula(derive=models.Shipment.clvs_eligible, as_expression=lambda row: 1 if row.clvs_reason == "" else 0)
