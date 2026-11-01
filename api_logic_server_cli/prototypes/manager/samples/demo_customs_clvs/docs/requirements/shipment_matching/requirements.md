Feature: Importer matching

### Step 2 — Importer matching

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

**Required: seed `Customer` data before verifying.** Add at least one row via the Admin UI (or a SQL INSERT) with `duty_bill_to_acct_nbr` matching the `trprt_bill_to_acct_nbr` value in your test XML.

**Verify:** Re-run the Step 2 curl. A ShipmentParty with `shipment_party_type_cd="I"` should appear in Admin UI.
