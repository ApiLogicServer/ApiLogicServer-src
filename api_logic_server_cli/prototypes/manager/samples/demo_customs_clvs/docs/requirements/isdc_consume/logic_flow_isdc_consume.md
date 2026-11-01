# Logic Flow — demo_customs_clvs [isdc_consume]

> Scoped to requirement: **isdc_consume**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_isdc_consume.svg)

</td>
<td width="35%">

### Rules

1. `ShipmentXml` → `_publish_isdc` (after_flush) — ShipmentXml event: publishes the raw blob to isdc_processed after Tx 1 commits, so Consumer 2 parses it in a clean Tx 2.

</td>
</tr>
</table>

## Requirements

```
Feature: Subscribe to Kafka and persist shipments

Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.
```

---
_Generated 2026-11-01 10:06_
