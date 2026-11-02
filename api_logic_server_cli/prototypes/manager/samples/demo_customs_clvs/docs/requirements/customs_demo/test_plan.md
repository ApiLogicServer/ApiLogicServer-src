# Test plan: customs_demo

Written before any `.feature` file. Closed out at the end (scenario name beside each row, or NOT covered and why).
Features are named as the `Feature:` lines in `requirements.md`.

Delivery: every message goes through `GET /consume_debug/isdc?file=...` in mode `auto` (live through Kafka when a
broker answers, else simulated); the mode used is recorded per scenario for the report.

| # | Rule / behavior | Scenarios planned (create / change / delete / enters-leaves / boundary / accepted-rejected) | Scenario(s) written |
|---|---|---|---|
| 1 | Subscribe `isdc`: parse and persist Shipment graph (Consumer 1 + bridge + Consumer 2) | create (graph persisted, placeholder party OIDs get distinct keys); malformed message (live only: blob stays unprocessed, error_text set) | Shipment message is persisted with its graph; Malformed message leaves an unprocessed blob with error text (live Kafka only) |
| 2 | Duplicate replay, policy `replace` | replay same message: graph counts stable, blob count +1 | Replayed shipment message replaces the graph |
| 3 | No orphans on delete | delete the Shipment through the API: parties, piece, commodity, special handling gone | Deleting the shipment leaves no orphans |
| 4 | Duplicate policy `fail` (env switch) | rejected duplicate | **NOT covered**: the policy is an environment switch read at runtime start-up (`ISDC_DUPLICATE_POLICY`); a Behave scenario cannot flip it on a running server |
| 5 | `Shipment` row_event: importer match (Customer by account) | match found (party type I with customer data); no match (none, shipment persisted); replay (one I party); update does not add a party | Importer account matches a customer; Importer account matches no customer; Replayed message keeps exactly one importer party; Updating the shipment does not add another importer party |
| 6 | `Rule.copy` Shipment.clvs_threshold_cad / clvs_courier_service_type_cd from SysConfig | create (value copied) ; parent SysConfig change | Shipment at or below the LVS threshold is eligible (threshold copied: boundary scenarios prove the value). **NOT covered**: a SysConfig threshold change (Rule.copy is a snapshot by design: existing shipments keep their copied value) |
| 7 | `Rule.formula` clvs_reason / clvs_eligible: input = local_customs_value_amt | at threshold (boundary, eligible); just above (rejected); value lowered; value raised | Shipment exactly at the threshold is eligible; Shipment just above the threshold is not eligible; Lowering the value makes the shipment eligible; Raising the value above the threshold makes the shipment not eligible |
| 8 | Courier clause: service_type_cd vs courier code | authorized; not authorized | Shipment at or below the LVS threshold is eligible; Shipment from an unauthorized courier is not eligible |
| 9 | `Rule.count` controlled_item_count (where FK not null) + early_row_event on ShipmentCommodity | create child controlled; change child tariff (enters set); delete child (leaves set); add second line; move child to another parent | Controlled goods line makes the shipment not eligible; Changing a commodity to a controlled tariff makes the shipment not eligible; Changing the controlled commodity back makes the shipment eligible; Adding a prohibited commodity line makes the shipment not eligible; Deleting the controlled commodity line makes the shipment eligible. **NOT covered**: move a line to another Shipment (the parent key is part of the line's primary key, so a line cannot be re-parented) |
| 10 | `Rule.count` prohibited_commodity_count (where is_prohibited = 1) | prohibited line; enters / leaves via tariff change | Prohibited commodity line makes the shipment not eligible; Adding a prohibited commodity line makes the shipment not eligible |
| 11 | early_row_event + `Rule.copy` office_clvs_release (released at CLVS-designated office) | designated; not designated; unknown location; change the location to a different office | Shipment at or below the LVS threshold is eligible; Release at an office that is not CLVS-designated is not eligible; Release at an unknown office is not eligible; Moving the release location to a non-designated office makes the shipment not eligible |
| 12 | clvs_reason lists all failures | several failures at once; blank when eligible | Several failed checks are listed together; Shipment at or below the LVS threshold is eligible (blank reason) |
| 13 | Live Kafka end to end (`Live Kafka end-to-end test`) | live-only: blob, shipment, importer party appear with no curl | Message sent through Kafka creates the blob, shipment and importer party (live Kafka only) |


**Close-out:** 13 rows; 3 NOT covered (rows 4, 6 parent change, 9 move to another parent), each with its reason above. 26 scenarios in 4 Features.
