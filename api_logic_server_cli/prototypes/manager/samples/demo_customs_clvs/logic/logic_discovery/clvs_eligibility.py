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

import logging

from logic_bank.logic_bank import Rule
from database import models

app_logger = logging.getLogger("api_logic_server_app")


# ---------------------------------------------------------------------------
# ShipmentCommodity early events — must fire BEFORE Rule.count where= evaluates
# ---------------------------------------------------------------------------

def _set_commodity_flags(row: models.ShipmentCommodity, old_row, logic_row):
    """Set is_controlled and is_prohibited by HS code lookup before Rule.count aggregates."""
    hs = row.harmonized_tariff_nbr or ''
    prefix = hs.replace('.', '')[:10]  # first 10 significant digits

    row.is_controlled = 0
    row.is_prohibited = 0

    if not prefix:
        return

    match = logic_row.session.query(models.ControlledRegulatedGood).filter(
        models.ControlledRegulatedGood.hs_code.like(prefix + '%')
    ).first()

    if match:
        row.is_controlled = 1
        row.controlled_regulated_goods_id = match.id
        app_logger.debug(f'clvs: HS {hs} → controlled (category={match.category})')

    if row.hazardous_material_cd:
        row.is_prohibited = 1
        app_logger.debug(f'clvs: HS {hs} hazardous_material_cd={row.hazardous_material_cd} → prohibited')


# ---------------------------------------------------------------------------
# Shipment early event — set customs_office_id before formula rules fire
# ---------------------------------------------------------------------------

def _set_customs_office(row: models.Shipment, old_row, logic_row):
    """Set customs_office_id by looking up PLANNED_CLEARANCE_LOCATION_CD in customs_office."""
    loc = row.planned_clearance_location_cd
    if not loc:
        return
    office = logic_row.session.query(models.CustomsOffice).filter_by(
        office_code=loc
    ).first()
    if office:
        row.customs_office_id = office.id
        app_logger.debug(f'clvs: clearance location {loc} → customs_office id={office.id}')
    else:
        app_logger.debug(f'clvs: clearance location {loc!r} not found in customs_office table')


# ---------------------------------------------------------------------------
# CLVS eligibility formulas — shared helper + two separate Rule.formula rules
# ---------------------------------------------------------------------------

def _reasons(row: models.Shipment, session) -> list:
    """Return list of CLVS ineligibility reasons (empty list = eligible)."""
    reasons = []

    if row.service_type_cd != row.clvs_service_type_cd:
        reasons.append(f'service type {row.service_type_cd!r} not CLVS-authorized (expected {row.clvs_service_type_cd!r})')

    value = float(row.local_customs_value_amt or 0)
    threshold = float(row.clvs_lvs_threshold or 3300)
    if value > threshold:
        reasons.append(f'duty value {value} exceeds CAD ${threshold} threshold')

    if (row.prohibited_item_count or 0) > 0:
        reasons.append(f'{row.prohibited_item_count} prohibited commodity line(s)')

    if (row.controlled_item_count or 0) > 0:
        reasons.append(f'{row.controlled_item_count} controlled/regulated goods line(s)')

    if row.customs_office_id is None:
        reasons.append('no CBSA-designated customs office assigned')
    else:
        # Do NOT use row.customs_office relationship — FK was set in same flush, may be stale
        office = session.query(models.CustomsOffice).get(row.customs_office_id)
        if office is None or office.clvs_release != 1:
            reasons.append('customs office not CLVS-designated')

    return reasons


def _clvs_eligible(row: models.Shipment, old_row, logic_row):
    """Derive clvs_eligible: 1 if shipment meets all CLVS criteria, else 0."""
    # Dependency anchor — LB scans this body; keep in sync with _reasons().
    _ = (row.service_type_cd, row.clvs_service_type_cd, row.local_customs_value_amt,
         row.clvs_lvs_threshold, row.controlled_item_count, row.prohibited_item_count,
         row.customs_office_id)
    return 1 if not _reasons(row, logic_row.session) else 0


def _clvs_reason(row: models.Shipment, old_row, logic_row):
    """Derive clvs_reason: comma-delimited list of CLVS ineligibility reasons (blank if eligible)."""
    # Dependency anchor — LB scans this body; keep in sync with _reasons().
    _ = (row.service_type_cd, row.clvs_service_type_cd, row.local_customs_value_amt,
         row.clvs_lvs_threshold, row.controlled_item_count, row.prohibited_item_count,
         row.customs_office_id)
    return ', '.join(_reasons(row, logic_row.session))


# ---------------------------------------------------------------------------
# Rule declarations
# ---------------------------------------------------------------------------

def declare_logic():
    # TODO: Review parent-value rules below.
    #   Rule.copy = snapshot (value frozen at insert time, no cascade on SysConfig change) ← default
    #   Rule.formula referencing row.parent.attr = live (re-derives if parent changes)
    #   Change Rule.copy → Rule.formula where live propagation is required.

    # ShipmentCommodity: set is_controlled / is_prohibited BEFORE Rule.count where= runs
    Rule.early_row_event(on_class=models.ShipmentCommodity, calling=_set_commodity_flags)

    # Shipment: set customs_office_id BEFORE formula rules run
    Rule.early_row_event(on_class=models.Shipment, calling=_set_customs_office)

    # Aggregate counts on parent Shipment (reactive to child changes)
    Rule.count(derive=models.Shipment.controlled_item_count, as_count_of=models.ShipmentCommodity,
               where=lambda row: row.is_controlled == 1)
    Rule.count(derive=models.Shipment.prohibited_item_count, as_count_of=models.ShipmentCommodity,
               where=lambda row: row.is_prohibited == 1)

    # Copy regulatory constants from SysConfig (snapshot at insert time)
    Rule.copy(derive=models.Shipment.clvs_lvs_threshold,    from_parent=models.SysConfig.clvs_lvs_threshold)
    Rule.copy(derive=models.Shipment.clvs_service_type_cd,  from_parent=models.SysConfig.clvs_service_type_cd)

    # CLVS eligibility formulas
    Rule.formula(derive=models.Shipment.clvs_eligible, calling=_clvs_eligible)
    Rule.formula(derive=models.Shipment.clvs_reason,   calling=_clvs_reason)
