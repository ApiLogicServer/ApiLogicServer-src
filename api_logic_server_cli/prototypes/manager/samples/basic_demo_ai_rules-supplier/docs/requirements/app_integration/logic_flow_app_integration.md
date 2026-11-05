# Logic Flow — demo_ai_rules_supplier [app_integration]

> Scoped to requirement: **app_integration**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_app_integration.svg)

</td>
<td width="35%">

### Rules

1. `Order` → `send_row_to_kafka` (after_flush)

</td>
</tr>
</table>

## Requirements

```
Requirement: App Integration

1. Publish the Order to Kafka topic 'order_shipping' if the date_shipped is not None

version: 1.0
created: 2026-11-04
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
```

---
_Generated 2026-11-04 17:42_
