# credit_limit_maintenance

Verbatim excerpt of docs/requirements/erpnext_credit/requirements.md that drives logic/logic_discovery/credit_limit_maintenance.py

---

## 6. Maintaining limits

Feature: Credit Limit Maintenance

* A Customer or Customer Group with two credit-limit rows for the same company is rejected.
* When a Customer's credit-limit rows change, each row with a non-zero `credit_limit` must be at least the customer's current outstanding for that company (with Sales Orders ignored when that row's flag is on). Otherwise the change is rejected. A row with a zero limit is allowed.
* **Copy from group**: an action on a Customer replaces its credit-limit rows with copies of its Customer Group's rows (company, `credit_limit`, flag).
