# Logic Flow — demo_customs_clvs [isdc_consume]

> Scoped to requirement: **isdc_consume**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_isdc_consume.svg)

</td>
<td width="35%">

### Rules

1. `ShipmentXml` → `_publish_isdc` (after_flush) — ShipmentXml event: publishes the raw XML blob to topic isdc_processed after Tx 1 commits, so Consumer 2

</td>
</tr>
</table>

## Requirements

```
Feature: Subscribe to Kafka and persist shipments

Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.

Parse and persist to the database using the field mappings in
`message_formats/Classify_Entity_Details.csv`.

Use `message_formats/MDE-CDV-HVS-WR-Rev260328.xml` as the reference message.

Duplicate replay behavior (required for this project):
- Match existing shipments by `LOCAL_SHIPMENT_OID_NBR` (`Shipment.local_shipment_oid_nbr`).
- If a duplicate key is found, replace the existing shipment graph in Tx 2:
    parse first, then replace the prior shipment graph and insert parsed rows.
    Implementation is not prescribed; behavior must match the verification checks below.
- Keep this behavior configurable via env policy (`fail|replace`), default `replace` for this project.

Important mapping note (prevent PK collisions):
- In this payload, party OID fields may carry placeholder value `0` for multiple rows.
- If mapped to local primary-key columns (e.g. `ShipmentParty.shipment_party_oid_nbr`),
  normalize placeholder IDs to `None` so DB autoincrement assigns unique PK values.
```

---
_Generated 2026-11-01 17:28_
