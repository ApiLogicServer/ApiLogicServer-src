# Logic Flow — erpnext_credit_modernized [credit_limit_maintenance]

> Scoped to requirement: **credit_limit_maintenance**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_credit_limit_maintenance.svg)

</td>
<td width="35%">

### Rules

1. `customer_credit_limit = sum(credit_limit)`<br>
2. `bypass_credit_limit_check = sum(bypass_credit_limit_check)`<br>
3. constraint: `CustomerCreditLimit`<br>
4. constraint: `CustomerGroupCreditLimit`

</td>
</tr>
</table>

## Requirements

```
## 6. Maintaining limits

Feature: Credit Limit Maintenance

* A Customer or Customer Group with two credit-limit rows for the same company is rejected.
* When a Customer's credit-limit rows change, each row with a non-zero `credit_limit` must be at least the customer's current outstanding for that company (with Sales Orders ignored when that row's flag is on). Otherwise the change is rejected. A row with a zero limit is allowed.
* **Copy from group**: an action on a Customer replaces its credit-limit rows with copies of its Customer Group's rows (company, `credit_limit`, flag).

version: 1.0
created: 2026-10-29T18:32:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
```

---
_Generated 2026-10-29 18:24_
