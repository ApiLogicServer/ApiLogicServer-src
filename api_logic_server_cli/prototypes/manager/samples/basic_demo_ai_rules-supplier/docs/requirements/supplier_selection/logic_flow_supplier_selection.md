# Logic Flow — demo_ai_rules_supplier [supplier_selection]

> Scoped to requirement: **supplier_selection**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_supplier_selection.svg)

</td>
<td width="35%">

### Rules

1. `SysSupplierReq` → `select_supplier_via_ai` (early) — SysSupplierReq event: chooses the optimal ProductSupplier by calling OpenAI with the candidates and

</td>
</tr>
</table>

## Requirements

```
AI Supplier Selection - Request Pattern handler for Check Credit clause 6.

Not a requirement file: it implements "Use AI to Set Item field unit_price by finding the optimal
Product Supplier based on cost, lead time, and world conditions" (see place_order/check_credit.py).
```

---
_Generated 2026-11-04 17:42_
