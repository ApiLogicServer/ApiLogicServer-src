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
import re
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

CLVS_SERVICE_TYPE = "04"


def _resolve_hs_controlled(row: models.ShipmentCommodity, old_row, logic_row: LogicRow):
    """Resolve controlled_regulated_goods_id and is_prohibited from HS code lookup on insert."""
    if not logic_row.is_inserted():
        return
    if not row.harmonized_tariff_nbr:
        return
    hs_raw = re.sub(r'[^0-9]', '', row.harmonized_tariff_nbr)[:10]
    session = logic_row.session
    from sqlalchemy import func
    with session.no_autoflush:
        crg = (
            session.query(models.ControlledRegulatedGood)
            .filter(func.replace(models.ControlledRegulatedGood.hs_code, '.', '') == hs_raw)
            .first()
        )
    if crg:
        row.controlled_regulated_goods_id = crg.id
        row.is_prohibited = 1


def _clvs_reasons(row: models.Shipment, session) -> list:
    reasons = []
    if row.service_type_cd != CLVS_SERVICE_TYPE:
        reasons.append(f"service_type {row.service_type_cd} not CLVS")
    val = float(row.local_customs_value_amt or 0)
    if val > 3300:
        reasons.append(f"value {val} exceeds CAD $3,300")
    if (row.prohibited_commodity_count or 0) > 0:
        reasons.append(f"{row.prohibited_commodity_count} prohibited line(s)")
    if (row.controlled_commodity_count or 0) > 0:
        reasons.append(f"{row.controlled_commodity_count} controlled line(s)")
    if row.planned_clearance_location_cd:
        with session.no_autoflush:
            office = (
                session.query(models.CustomsOffice)
                .filter(
                    models.CustomsOffice.office_code == row.planned_clearance_location_cd,
                    models.CustomsOffice.clvs_release == 1,
                )
                .first()
            )
        if office is None:
            reasons.append(f"office {row.planned_clearance_location_cd} not CLVS-designated")
    else:
        reasons.append("no planned_clearance_location_cd")
    return reasons


def _clvs_reason(row: models.Shipment, old_row, logic_row: LogicRow):
    """Derive clvs_reason: comma-delimited CLVS ineligibility reasons (blank if eligible)."""
    # LB dependency scan: reference all input columns directly
    _ = row.service_type_cd, row.local_customs_value_amt, row.prohibited_commodity_count, row.controlled_commodity_count, row.planned_clearance_location_cd
    return ", ".join(_clvs_reasons(row, logic_row.session))


def _clvs_eligible(row: models.Shipment, old_row, logic_row: LogicRow):
    """Derive clvs_eligible: 1 if shipment meets all CLVS criteria, else 0."""
    _ = row.service_type_cd, row.local_customs_value_amt, row.prohibited_commodity_count, row.controlled_commodity_count, row.planned_clearance_location_cd
    return 1 if not _clvs_reasons(row, logic_row.session) else 0


def declare_logic():
    # TODO: Review parent-value rules below.
    #   Rule.copy  = snapshot (value frozen at transaction time, no cascade on parent change) ← default
    #   Rule.formula referencing row.parent.attr = live (re-derives if parent changes)

    # Set controlled_regulated_goods_id and is_prohibited via HS code lookup on commodity insert
    Rule.early_row_event(on_class=models.ShipmentCommodity, calling=_resolve_hs_controlled)

    # Count prohibited and controlled commodity lines on parent Shipment
    Rule.count(derive=models.Shipment.prohibited_commodity_count, as_count_of=models.ShipmentCommodity, where=lambda row: row.is_prohibited == 1)
    Rule.count(derive=models.Shipment.controlled_commodity_count, as_count_of=models.ShipmentCommodity, where=lambda row: row.controlled_regulated_goods_id is not None)

    # Derive clvs_reason and clvs_eligible on Shipment (depend on count columns above)
    Rule.formula(derive=models.Shipment.clvs_reason, calling=_clvs_reason)
    Rule.formula(derive=models.Shipment.clvs_eligible, calling=_clvs_eligible)
