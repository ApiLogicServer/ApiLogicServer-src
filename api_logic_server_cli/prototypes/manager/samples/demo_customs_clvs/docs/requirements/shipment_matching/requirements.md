---
created: 2026-06-29T00:00:00
created_by: claude-sonnet-4-6 (valjhuber@gmail.com)
use_case: shipment_matching
---

Logic discovery: Shipment matching (Phase 2).

Create `logic/logic_discovery/shipment_matching.py`.

On Shipment insert, look up the matching Customer using:
    Shipment.trprt_bill_to_acct_nbr == Customer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row, matching high confidence columns
from Customer to ShipmentParty.
Use Rule.row_event (not early_row_event) — fires before_flush so the new
ShipmentParty writes atomically with the parent Shipment.
