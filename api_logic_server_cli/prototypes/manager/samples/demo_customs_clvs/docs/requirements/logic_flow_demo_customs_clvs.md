# Logic Flow — demo_customs_clvs

## Requirements

```
Scenario: Shipment at or below the LVS threshold is eligible
  Given a shipment imported by an authorized CLVS courier
  And the shipment has an estimated value for duty not exceeding CAD $3,300
  And the shipment has no prohibited commodity lines (ShipmentCommodity.is_prohibited = 1)
  And the shipment has no controlled or regulatory goods (lookup using first ten digits of the harmonized tariff number)
  And the shipment is released at a CBSA-designated customs office
  When the shipment eligibility is evaluated
  Then the shipment shall be eligible for the CLVS Program
  And set the clvs_reason as a comma delimited list of short all reasons why failed (or blank)
```

```
isdc_consume — row-event bridge: ShipmentXml insert → publish to isdc_processed.
```

```
Logic discovery: Shipment matching (Phase 2).

On Shipment insert, look up the matching Customer using:
    Shipment.trprt_bill_to_acct_nbr == Customer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row, matching high confidence columns
from Customer to ShipmentParty.
Use Rule.row_event (not early_row_event) — fires before_flush so the new
ShipmentParty writes atomically with the parent Shipment.
```

![logic flow](logic_diagrams/logic_diagram.svg)

## Rules

1. `is_prohibited = 1 if controlled_regulated_goods_id is not None ...`
2. `clvs_eligible = _clvs_eligible(row)` — Derive clvs_eligible: 1 if shipment meets all CLVS criteria, else 0.
3. `clvs_reason = _clvs_reason(row)` — Derive clvs_reason: comma-delimited list of CLVS ineligibility reasons (blank if eligible).
4. `prohibited_commodity_count = count(ShipmentCommodity where is_prohibited)`
5. `controlled_item_count = count(ShipmentCommodity where controlled_regulated_goods_id)`
E. `Shipment` → `_set_customs_office` (early) — Set customs_office_id FK from planned_clearance_location_cd on insert.
E. `ShipmentCommodity` → `_set_controlled_goods` (early) — Set controlled_regulated_goods_id FK by matching HS code first 10 digits.
E. `ShipmentXml` → `_publish_isdc` (after_flush)

---
_Generated 2026-05-26 08:20_
