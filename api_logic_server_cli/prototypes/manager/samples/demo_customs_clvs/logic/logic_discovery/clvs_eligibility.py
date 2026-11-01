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
from sqlalchemy import func, literal
from logic_bank.logic_bank import Rule
from database import models


def _set_customs_office(row: models.Shipment, old_row, logic_row):
    """Shipment event: looks up the CustomsOffice whose office_code is the planned clearance location and sets
    customs_office_id (FK), so Rule.copy can bring the office's clvs_release down before the eligibility reason is derived."""
    code = row.planned_clearance_location_cd
    office = None
    if code:
        office = logic_row.session.query(models.CustomsOffice).filter(models.CustomsOffice.office_code == code).first()
    row.customs_office_id = office.id if office else None


def _match_controlled_goods(row: models.ShipmentCommodity, old_row, logic_row):
    """ShipmentCommodity event: looks up ControlledRegulatedGood by the first ten digits of the harmonized tariff number
    (a controlled hs_code is a prefix of them) and sets controlled_regulated_goods_id (FK) before Rule.count aggregates it."""
    digits = "".join(ch for ch in (row.harmonized_tariff_nbr or "") if ch.isdigit())[:10]
    match = None
    if len(digits) >= 8:
        controlled_digits = func.replace(models.ControlledRegulatedGood.hs_code, ".", "")
        match = (logic_row.session.query(models.ControlledRegulatedGood)
                 .filter(literal(digits).like(controlled_digits + "%")).first())
    row.controlled_regulated_goods_id = match.id if match else None


def _clvs_reason(row: models.Shipment, old_row, logic_row):
    """Derive clvs_reason: comma-delimited short reasons why the shipment fails CLVS eligibility (blank if eligible)."""
    config = models.SysConfig.current(logic_row.session)
    service_type = row.service_type_cd
    value = row.local_customs_value_amt
    prohibited = row.prohibited_commodity_count
    controlled = row.controlled_commodity_count
    release = row.customs_office_clvs_release
    reasons = []
    if service_type != config.clvs_service_type_cd:
        reasons.append("courier not authorized")
    if value is None or value > config.clvs_lvs_threshold_cad:
        reasons.append("value over threshold")
    if (prohibited or 0) > 0:
        reasons.append("prohibited goods")
    if (controlled or 0) > 0:
        reasons.append("controlled goods")
    if release != 1:
        reasons.append("office not designated")
    return ", ".join(reasons)


def declare_logic():
    Rule.early_row_event(on_class=models.Shipment, calling=_set_customs_office)
    Rule.early_row_event(on_class=models.ShipmentCommodity, calling=_match_controlled_goods)
    Rule.copy(derive=models.Shipment.customs_office_clvs_release, from_parent=models.CustomsOffice.clvs_release)
    Rule.count(derive=models.Shipment.prohibited_commodity_count, as_count_of=models.ShipmentCommodity, where=lambda row: row.is_prohibited == 1)
    Rule.count(derive=models.Shipment.controlled_commodity_count, as_count_of=models.ShipmentCommodity, where=lambda row: row.controlled_regulated_goods_id is not None)
    Rule.formula(derive=models.Shipment.clvs_reason, calling=_clvs_reason)
    Rule.formula(derive=models.Shipment.clvs_eligible, as_expression=lambda row: 1 if row.clvs_reason == "" else 0)
