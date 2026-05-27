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
import logging
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

app_logger = logging.getLogger("api_logic_server_app")

CLVS_SERVICE_TYPE = '04'
CLVS_VALUE_THRESHOLD = 3300.0


# ---------------------------------------------------------------------------
# Early row event: resolve customs_office_id from planned_clearance_location_cd
# ---------------------------------------------------------------------------

def _set_customs_office(row: models.Shipment, old_row: models.Shipment, logic_row: LogicRow):
    """Set customs_office_id FK from planned_clearance_location_cd on insert."""
    if not logic_row.is_inserted():
        return
    if not row.planned_clearance_location_cd:
        return
    office = logic_row.session.query(models.CustomsOffice).filter_by(
        office_code=row.planned_clearance_location_cd
    ).first()
    if office:
        row.customs_office_id = office.id
        logic_row.log(f"clvs: customs_office_id={office.id} ({office.name}) for {row.planned_clearance_location_cd}")
    else:
        logic_row.log(f"clvs: no CBSA office for planned_clearance_location_cd={row.planned_clearance_location_cd}")


# ---------------------------------------------------------------------------
# Early row event: resolve controlled_regulated_goods_id from harmonized_tariff_nbr
# ---------------------------------------------------------------------------

def _normalize_hs(hs_code: str) -> str:
    """Strip non-digit chars from HS code for prefix matching."""
    return re.sub(r'[^0-9]', '', hs_code or '')


def _set_controlled_goods(row: models.ShipmentCommodity, old_row: models.ShipmentCommodity, logic_row: LogicRow):
    """Set controlled_regulated_goods_id FK by matching HS code first 10 digits."""
    if not logic_row.is_inserted():
        return
    if not row.harmonized_tariff_nbr:
        return
    commodity_hs = _normalize_hs(row.harmonized_tariff_nbr)
    if not commodity_hs:
        return
    controlled_goods = logic_row.session.query(models.ControlledRegulatedGood).all()  # @health-check: suppress — prefix HS match requires full table scan; no LB-expressible WHERE equivalent
    for cg in controlled_goods:
        ctrl_hs = _normalize_hs(cg.hs_code)
        # Commodity HS must start with the controlled HS code prefix
        if ctrl_hs and commodity_hs.startswith(ctrl_hs):
            row.controlled_regulated_goods_id = cg.id
            logic_row.log(f"clvs: commodity HS {row.harmonized_tariff_nbr} matched controlled good id={cg.id}: {cg.clvs_reason}")
            return


# ---------------------------------------------------------------------------
# CLVS eligibility reasons (shared helper)
# ---------------------------------------------------------------------------

def _reasons(row: models.Shipment) -> list:
    reasons = []
    if row.service_type_cd != CLVS_SERVICE_TYPE:
        reasons.append(f"service_type {row.service_type_cd} not CLVS courier")
    if row.local_customs_value_amt is not None:
        if float(row.local_customs_value_amt) > CLVS_VALUE_THRESHOLD:
            reasons.append(f"value {row.local_customs_value_amt} exceeds ${CLVS_VALUE_THRESHOLD:.0f}")
    if row.prohibited_commodity_count and row.prohibited_commodity_count > 0:
        reasons.append(f"{row.prohibited_commodity_count} prohibited commodity line(s)")
    if row.controlled_item_count and row.controlled_item_count > 0:
        reasons.append(f"{row.controlled_item_count} controlled/regulated item(s)")
    if row.customs_office_id is None:
        reasons.append("clearance location not a CBSA customs office")
    elif row.customs_office is not None and not row.customs_office.clvs_release:
        reasons.append(f"customs office {row.planned_clearance_location_cd} not CLVS-designated")
    return reasons


def _clvs_eligible(row: models.Shipment, old_row: models.Shipment, logic_row: LogicRow):
    """Derive clvs_eligible: 1 if shipment meets all CLVS criteria, else 0."""
    _ = row.service_type_cd, row.local_customs_value_amt, row.prohibited_commodity_count, row.controlled_item_count, row.customs_office_id  # LB dependency tracking
    return 1 if not _reasons(row) else 0


def _clvs_reason(row: models.Shipment, old_row: models.Shipment, logic_row: LogicRow):
    """Derive clvs_reason: comma-delimited list of CLVS ineligibility reasons (blank if eligible)."""
    _ = row.service_type_cd, row.local_customs_value_amt, row.prohibited_commodity_count, row.controlled_item_count, row.customs_office_id  # LB dependency tracking
    return ", ".join(_reasons(row))


def declare_logic():
    # TODO: Review parent-value rules below.
    #   Rule.copy  = snapshot (value frozen at transaction time, no cascade on parent change)  ← default
    #   Rule.formula referencing row.parent.attr = live (re-derives if parent changes)
    #   Change Rule.copy → Rule.formula where live propagation is required.

    # Resolve FK for customs office on Shipment insert
    Rule.early_row_event(on_class=models.Shipment, calling=_set_customs_office)

    # Resolve FK for controlled goods on ShipmentCommodity insert
    Rule.early_row_event(on_class=models.ShipmentCommodity, calling=_set_controlled_goods)

    # is_prohibited = 1 if commodity has a controlled/regulated goods match
    Rule.formula(derive=models.ShipmentCommodity.is_prohibited,
                 as_expression=lambda row: 1 if row.controlled_regulated_goods_id is not None else 0)

    # Aggregate counts on Shipment (reactive: re-fires when child rows change)
    Rule.count(derive=models.Shipment.prohibited_commodity_count,
               as_count_of=models.ShipmentCommodity,
               where=lambda row: row.is_prohibited == 1)

    Rule.count(derive=models.Shipment.controlled_item_count,
               as_count_of=models.ShipmentCommodity,
               where=lambda row: row.controlled_regulated_goods_id is not None)

    # CLVS eligibility (depends on counts and customs office FK)
    Rule.formula(derive=models.Shipment.clvs_eligible, calling=_clvs_eligible)
    Rule.formula(derive=models.Shipment.clvs_reason, calling=_clvs_reason)
