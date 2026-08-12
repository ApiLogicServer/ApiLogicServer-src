# Logic Flow — demo_customs_clvs [isdc_consume]

> Scoped to requirement: **isdc_consume**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_isdc_consume.svg)

</td>
<td width="35%">

### Rules

E. `ShipmentXml` → `_publish_isdc` (after_flush) — ShipmentXml event: publishes the raw payload to Kafka topic isdc_processed so

</td>
</tr>
</table>

## Requirements

```
EAI Consume — isdc topic, row-event bridge.

On ShipmentXml insert (Tx 1, from Consumer 1 or /consume_debug), publish the raw
payload to isdc_processed so Consumer 2 can parse and persist domain rows in Tx 2.
See integration/kafka/kafka_subscribe_discovery/isdc.py for the full pipeline.
```

---
_Generated 2026-08-11 18:36_
