# Logic Flow — samples/demo_customs_clvs

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram.svg)

</td>
<td width="35%">

### Rules

1. `clvs_lvs_threshold = copy(clvs_lvs_threshold)`<br>
2. `clvs_service_type_cd = copy(clvs_service_type_cd)`<br>
3. `clvs_eligible = _clvs_eligible(row)` — Derive clvs_eligible: 1 if shipment meets all CLVS criteria, else 0.<br>
4. `clvs_reason = _clvs_reason(row)` — Derive clvs_reason: comma-delimited list of CLVS ineligibility reasons (blank if eligible).<br>
5. `controlled_item_count = count(ShipmentCommodity where is_controlled)`<br>
6. `prohibited_item_count = count(ShipmentCommodity where is_prohibited)`<br>
E. `ShipmentCommodity` → `_set_commodity_flags` (early) — Set is_controlled and is_prohibited by HS code lookup before Rule.count aggregates.<br>
E. `Shipment` → `_set_customs_office` (early) — Set customs_office_id by looking up PLANNED_CLEARANCE_LOCATION_CD in customs_office.<br>
E. `ShipmentXml` → `_publish_isdc_processed` (after_flush) — Publish ShipmentXml.id to isdc_processed topic so Consumer 2 can parse the blob.

</td>
</tr>
</table>

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
Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.
...
(Step 1 — EAI row_event bridge: after ShipmentXml insert, publish blob.id to isdc_processed)
```

```
Logic discovery: Shipment matching (Phase 2).

Create `logic/logic_discovery/shipment_matching.py`.

On Shipment insert, look up the matching Customer using:
    Shipment.trprt_bill_to_acct_nbr == Customer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row, matching high confidence columns
from Customer to ShipmentParty.
Use Rule.row_event (not early_row_event) — fires before_flush so the new
ShipmentParty writes atomically with the parent Shipment.
```

---
_Generated 2026-07-03 07:39_
