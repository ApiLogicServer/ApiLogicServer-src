## Ad-Libs Report
**12 items need your review. 12 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — Company, Customer Group, Customer, customer / customer-group credit-limit rows, Ledger Entry, Sales Order, Delivery Note (+ lines), Sales Invoice (+ lines), Journal Entry (+ account lines); Accounts Settings = `sys_config.credit_controller`.
2. **Derived/predicted schema additions** — a `customer_company` bucket (one row per customer and company) holding the three outstanding parts, outstanding, and the customer row's limit / bypass flag; derived columns on documents and lines (open amount, billed qty, unbilled amounts, unlinked-line counts, grand-total shares); no SysConfig numeric constants (the only constant is the 100 of a percentage); no allocate junction tables; no Request Pattern.
3. **Create db** — `database/erpnext_credit_ddl.sql` + `rebuild-from-database` — 14 tables (13 domain + sys_config); one follow-up ALTER (Delivery Note share columns, see Error Correction Loops).
4. **Run impl-req** — 4 logic files: 9 Rule.sum, 3 Rule.count, 9 Rule.formula, 3 Rule.constraint, 4 Rule.commit_constraint, 6 early_row_event registrations; 1 custom API (copy from group).
5. **Test data / testing** — `alp_init.py` seeded 2 companies, 3 groups, 5 customers, 1 Sales Order, 1 Sales Invoice (rules computed the bucket rows); API smoke test passed (reject over limit as admin, allow as credit controller sam); Behave tests created in the test step.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
*(written before any code — both phases completed in order)*

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md` (all sections), `message_formats/*` (none present), `database/models.py` (SysConfig only)

| Step | Signal |
|---|---|
| §1 Data | 13 domain tables from starter.sqlite; Accounts Settings → reuse `SysConfig` (singleton) |
| §2 Credit Limit Lookup | lookup at check time (customer row → group row → company default); no aggregate |
| §3 Outstanding | Rule.sum needed ×3 into a per-(customer, company) bucket; Rule.formula on SO/DN/DN line; Rule.sum billed qty from invoice lines |
| §4 Credit Check | constraint helper; role check via `Security.current_user_has_role` (security.md) |
| §5 Check On Documents | Rule.constraint(calling=) per document; Rule.count of unlinked lines on DN/SI; Rule.sum of bypass extra on DN |
| §6 Maintenance | uniqueness constraints (+ DB UNIQUE); constraint on customer credit-limit row vs outstanding; copy-from-group action (custom API) |
| §8 Simplifications | ledger posting from Sales Invoice / Journal Entry (early_row_event inserts LedgerEntry); cancel sets flag |

DDL change list *(one row per change — covers ALL steps, run once before any coding)*:

| Table | Change | Reason |
|---|---|---|
| sys_config | ADD COLUMN credit_controller TEXT | §1/§4 Accounts Settings.credit_controller |
| company, customer_group, customer | CREATE TABLE | §1 |
| customer_credit_limit, customer_group_credit_limit | CREATE TABLE, UNIQUE(parent, company) | §1, §6 one row per company |
| customer_company | CREATE TABLE (ledger_balance, open_sales_order_amount, unbilled_delivery_amount, outstanding, outstanding_ignoring_sales_orders, customer_credit_limit, bypass_credit_limit_check) | §3 Rule.sum ×3 + Rule.formula ×2; §5 bypass flag Rule.sum; §6 |
| ledger_entry | CREATE TABLE + amount (Rule.formula), customer_company_id (early_row_event), sales_invoice_id / journal_entry_account_id (posting source) | §1, §3 part 1, §8 |
| sales_order | CREATE TABLE + open_amount (Rule.formula), customer_company_id | §3 part 2 |
| delivery_note | CREATE TABLE + per_billed, unbilled_line_total (Rule.sum), unbilled_amount (Rule.formula), unlinked_line_count / no_invoice_line_count (Rule.count), bypass_extra_line_total (Rule.sum), bypass_extra_amount (Rule.formula), customer_company_id | §3 part 3, §5 |
| delivery_note_item | CREATE TABLE + billed_qty (Rule.sum), unbilled_amount, bypass_extra_amount (Rule.formula) | §3 part 3, §5 |
| sales_invoice | CREATE TABLE + grand_total, unlinked_line_count (Rule.count) | §5, §8 |
| sales_invoice_item | CREATE TABLE + counts_as_billed (Rule.formula) | §3 billed quantity |
| journal_entry, journal_entry_account | CREATE TABLE | §1, §5, §8 |

**Phase 2 — CE / Pattern Assessment**
Files read: `logic_bank_api.md`, `logic_bank_patterns.md`, `security.md` (no EAI)

| Step | Rule Plan |
|---|---|
| §3 Outstanding | early_row_event links each LedgerEntry / SalesOrder / DeliveryNote / CustomerCreditLimit to its CustomerCompany (FK set in event, never by a rule); Rule.formula LedgerEntry.amount; Rule.sum ledger_balance where not cancelled; Rule.formula SalesOrder.open_amount; Rule.sum open_sales_order_amount; Rule.formula SalesInvoiceItem.counts_as_billed; Rule.sum DeliveryNoteItem.billed_qty; Rule.formula DeliveryNoteItem.unbilled_amount; Rule.sum DeliveryNote.unbilled_line_total; Rule.formula DeliveryNote.unbilled_amount; Rule.sum unbilled_delivery_amount; Rule.formula outstanding / outstanding_ignoring_sales_orders |
| §2/§4 | functions `applicable_credit_limit()` and `check_credit()` (raise ConstraintException with customer, outstanding, limit) |
| §5 | Rule.constraint(calling=) on SalesOrder, DeliveryNote, SalesInvoice, JournalEntry; Rule.count unlinked lines; Rule.sum + Rule.formula bypass extra |
| §6 | Rule.constraint(calling=) uniqueness ×2; Rule.constraint(calling=) limit ≥ outstanding on CustomerCreditLimit (fires only when the row itself changes); Rule.sum customer_credit_limit / bypass on bucket; custom API `copy_credit_limits_from_group` |
| §8 | early_row_event on SalesInvoice and JournalEntry posts / cancels LedgerEntry rows (early, so the posting is in outstanding before the document's constraint runs) |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct (unlinked lines are Rule.count on the line tables)
- [x] No `as_expression=lambda row: my_func(row)` — using `calling=my_func`
- [x] No `session.query()` inside formula or row_event (queries only in the bucket-link lookup and the check-time credit-limit lookup)
- [x] EAI: not present

**Implementation Plan** *(ordered steps written before any file was changed)*:

| Step | What was planned |
|---|---|
| 1 | Run DDL + rebuild-from-database |
| 2 | logic/logic_discovery/outstanding_amount.py — bucket link events + §3 rules |
| 3 | logic/logic_discovery/credit_check.py — §2 lookup + §4 check helpers |
| 4 | logic/logic_discovery/credit_check_on_documents.py — §5 constraints |
| 5 | logic/logic_discovery/credit_limit_maintenance.py + api/api_discovery/copy_credit_limits_from_group.py — §6 |
| 6 | logic/logic_discovery/ledger_posting.py — §8 posting |
| 7 | security/declare_security.py — credit controller role note; seed (alp_init.py) |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Per-(customer, company) bucket with Rule.sum for outstanding; check-time lookup for the limit; commit constraints per document so the check sees settled roll-ups |
| CE Files Loaded | implement_requirements.md, logic_bank_api.md (via CLAUDE.md), logic_bank_patterns.md, security.md |
| Schema Read First | Yes — models.py read before any logic |
| Sample Data Read | N/A — no message_formats |
| Subagent Used | No — single pass |
| Self-Verification | Yes — seed run (rules fired, bucket rows correct), server started, API smoke test |
| Lightweight Checks Used | Yes — sqlite3 queries + curl-style requests |
| Gate Test Run Count | 1 smoke run before the Behave suite |
| Gate Test Purpose | Final verification |
| Error Correction Loops | 4 |
| Long-Run Diagnostics | None |

**Error Correction Loops**:

```
Loop 1:
  Symptom:   design gap found while coding credit_check.py: a Delivery Note's own submit cascades to its lines
             after its constraints, so a docstatus-dependent line formula gave draft-time values to the check
  Diagnosis: read LogicRow.update() phase order (constraints before cascade to children)
  Fix:       ALTER delivery_note / delivery_note_item: grand_total_share per line, two shares summed on the note,
             note-level formula picks the share by docstatus; checks moved to Rule.commit_constraint
  Time:      ~4 min
  Root cause type: missing read (engine phase order) during Phase 1
Loop 2:
  Symptom:   seed script: optimistic-lock ALSError when updating an invoice the rules had just updated
  Diagnosis: logs - the stale ORM object's checksum
  Fix:       seed enters the invoice already submitted, with its line, in one commit
  Time:      ~2 min
  Root cause type: seed-script plumbing (not logic)
Loop 3:
  Symptom:   (none at runtime) a `row.JournalEntryAccountList:` token in a constraint body would have reached the
             dependency scanner with a trailing colon
  Diagnosis: re-read against the CE tokenizer gotcha before first start
  Fix:       query the lines by journal_entry_id into a local
  Time:      ~1 min
  Root cause type: CE gap avoided by checklist
Loop 4:
  Symptom:   first Behave run: 3 of 53 scenarios failed - a ledger entry, Sales Order or Delivery Note moved to
             another customer was added to the new customer but not removed from the old one
  Diagnosis: the new customer's bucket was created in the same flush with no id yet, so the engine saw no
             foreign key change and adjusted only the new parent
  Fix:       outstanding_amount.py inserts a missing bucket directly (all roll-ups 0) so it has an id at once
  Time:      ~1.5 min (fix, server restart, re-run: 53 of 53 passed)
  Root cause type: engine behavior not covered by the CE (parent created inside an early_row_event)
```

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/credit_check.py:65` | §2 step 2: a group row with bypass off and a credit_limit of 0 is taken as the match, so it means "no limit" and the company default is NOT used (literal "first match wins"; only step 1 says "if not zero"). | Confirm, or say the group row should also fall through to the company default when its limit is 0. |
| `logic/logic_discovery/credit_check.py:77-86` | No signed-in user (seed script, direct insert, `SECURITY_ENABLED = False`) is treated as "not a credit controller": the check is enforced. | Confirm the no-user policy. |
| `database/test_data/alp_init.py:40` | The credit controller role is seeded as `manager` (the Keycloak realm role held by sam and u2); the requirements do not name the role. `admin` / `sa` are not excused. | Set `sys_config.credit_controller` to the real role, or NULL for "nobody is excused". |
| `logic/logic_discovery/credit_check.py:89-116` | The excuse belongs to whoever commits the transaction. Nothing records that a credit controller let a document through, and a later edit of that document by another user (e.g. an update after submit of a Sales Order) is checked again and may be rejected. | Decide whether overrides need an audit record or a sticky approval. |
| `logic/logic_discovery/credit_check.py:236-241` | The check runs at commit, so outstanding includes the document's own effect (the Sales Order's open amount, the Sales Invoice's own debit, the Journal Entry's postings) and the delivery lines an invoice bills. The requirements do not say whether the document's own amount is counted. | Confirm. |
| `logic/logic_discovery/credit_check.py:120-131` | "On update after submit" is read as any insert or update of a submitted Sales Order (docstatus 1); an update that leaves or sets status Closed is not checked (closing can only lower outstanding), and a cancel (docstatus 2) is not checked. | Confirm the scope of "update after submit". |
| `logic/logic_discovery/credit_check.py:169-179` | §5 "or the note is a draft": the check runs on submit, when the note is no longer a draft and its own unlinked lines are already in outstanding part 3, so the draft branch is computed (bypass_extra_amount) but no trigger reaches it. | Confirm, or name a draft-time trigger for the check. |
| `logic/logic_discovery/credit_limit_maintenance.py:50-66` | "When a Customer's credit-limit rows change, each row ... must be at least outstanding": only the rows inserted or changed in the transaction are checked (an unchanged sibling row is not re-validated), and rows are not re-checked later when outstanding grows. | Confirm per-row scope. |
| `api/api_discovery/copy_credit_limits_from_group.py:31-34` | Copy from group: the copied rows pass through the maintenance rule, so a copy whose group limit is below the customer's outstanding is rejected (all or nothing). The requirements do not say. | Confirm. |
| `database/erpnext_credit_ddl.sql` | Domain-floor constraints NOT added (spec does not state them): quantities > 0, totals >= 0, `per_billed` between 0 and 100, `returned_qty <= qty`, debit/credit >= 0. | Say which you want. |
| `ui/admin/admin.yaml` | `rebuild-from-database` wrote `ui/admin/admin-merge.yaml` with the new tables; `admin.yaml` was NOT replaced (the CE requires your confirmation), so the Admin App does not yet show the domain tables. | Approve: back up admin.yaml and copy admin-merge.yaml over it. |
| `database/erpnext_credit_ddl.sql:21` | "Customer belongs to a Customer Group" is enforced as a required FK (NOT NULL). | Confirm customers without a group are not allowed. |

#### Reviewer notes (2026-10-29): suggestions only, nothing resolved

Added after the run by the reviewing assistant, checked against the ERPNext source where possible. The code was **not** changed: this system is a modernization test, not a deployment, so these stay open.

| # | Issue | Suggested disposition | Basis |
|---|---|---|---|
| 1 | Group row with limit 0 | **Differs from ERPNext.** In `get_credit_limit`, after the group lookup comes `if not credit_limit: credit_limit = company default`, so a group row with limit 0 **falls through** to the company default. The rebuild treats it as "no limit". The requirements did not say it (their section 2 states "if not zero" for the customer row only), so the gap is in the requirements text, not only in the AI's reading. | ERPNext source, `customer.py:get_credit_limit` |
| 2 | No signed-in user means enforced | Keep | Safe default; same as the `demo_emp_types` budget rule |
| 3 | Role seeded as `manager` | Keep for the demo; configurable via `sys_config` | Requirements name a role without naming it |
| 4 | Override leaves no record | Open. ERPNext shows the same behavior (no record); an audit record would be a new requirement | Source shows none |
| 5 | Document's own amount is counted | Keep | ERPNext checks after the document is saved/submitted |
| 6 | "Update after submit" scope | Keep | Closing can only lower outstanding |
| 7 | Delivery Note "draft" branch unreachable | Keep | Preview mode was out of scope; ERPNext's pre-submit warning is the only place a draft is checked |
| 8 | Maintenance checks changed rows only | Keep | Matches the stated rule |
| 9 | Copy from group is all or nothing | Keep; the AI's call | Not in ERPNext's code |
| 10 | No floor checks added | Open (faithful means not adding) | Spec silent |
| 11 | `admin.yaml` not replaced | **Resolved**: backed up to `admin.yaml.bak`, `admin-merge.yaml` copied over (approved 2026-10-29) | |
| 12 | Customer must belong to a group (NOT NULL) | Likely **stricter than ERPNext**: `customer_group` is not marked required in ERPNext's Customer doctype definition (not checked whether code elsewhere requires it) | `customer.json` |

---

### 🟡 FYI
- `database/erpnext_credit_ddl.sql` — "submitted state" modeled as ERPNext's `docstatus` (0 draft, 1 submitted, 2 cancelled) on Sales Order, Delivery Note, Sales Invoice, Journal Entry; "on submit" = docstatus becomes 1 (insert with 1, or update from another value).
- `database/erpnext_credit_ddl.sql` — Delivery Note has an input `per_billed` (§5 needs it; §1 does not list it).
- `database/erpnext_credit_ddl.sql` — credit-limit rows are two tables (customer, customer group) with UNIQUE(parent, company) as a database backstop for §6.
- `logic/logic_discovery/outstanding_amount.py:37` — `customer_company` bucket rows are created on first use by an early_row_event (the FK is set in the event, never by a rule); the empty bucket is inserted with a direct SQL insert (all roll-ups 0, no rules to run on an empty row) so it has an id and a later move to another customer adjusts both buckets.
- `logic/logic_discovery/credit_check.py:55` — the applicable limit is looked up at check time (customer row, group row, company), not stored, so it is always current.
- `logic/logic_discovery/outstanding_amount.py:97` — return Delivery Notes are not excluded from part 3 (the requirement does not exclude them).
- `logic/logic_discovery/ledger_posting.py:46` — a Sales Invoice posts `abs(grand_total)`: a debit, or a credit for a return; cancel (docstatus 1 to 2) sets `is_cancelled` on the entries it posted (Journal Entry the same).
- `logic/logic_discovery/credit_check.py:213` — a Journal Entry line is a customer line when `party_type == 'Customer'`; the party is the `customer_id` FK.
- `logic/logic_discovery/credit_check.py:114` — the rejection message is "Credit limit has been crossed for customer <name> (<outstanding>/<limit>)"; the API returns it as an HTTP error (500 from a commit constraint).
- `logic/logic_discovery/credit_check.py:77` — role check via `Security.current_user_has_role(<sys_config.credit_controller>)` (docs/training/security.md, "Roles inside business rules").
- `api/api_discovery/copy_credit_limits_from_group.py` — the "action" is `POST /copy_credit_limits_from_group {"customer_id": n}` (JWT required when security is on); deletes are flushed before the copies are inserted.
- `security/declare_security.py` — Keycloak (container already running); no grants changed; the requirements have no access-control section.

</details>
