# ledger_posting

Verbatim excerpt of docs/requirements/erpnext_credit/requirements.md that drives logic/logic_discovery/ledger_posting.py

---

## 8. Simplifications for this rebuild

* One ledger-entry table. Submitting a Sales Invoice posts a debit for its total; a return posts a credit. A Journal Entry line for a customer posts its debit or credit. Cancelling sets the cancelled flag.
* One currency; "base" amounts equal the document amounts.
* Documents are entered with their totals; no item, price or tax calculation.
