---
created: 2026-06-29T00:00:00
created_by: claude-sonnet-4-6 (valjhuber@gmail.com)
use_case: isdc_consume
---

Read `docs/training/eai_subscribe.md`, then:

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
