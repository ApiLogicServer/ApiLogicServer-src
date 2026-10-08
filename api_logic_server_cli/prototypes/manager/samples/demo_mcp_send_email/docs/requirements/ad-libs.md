## Ad-Libs Report
**0 items need your review. 3 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — Reused existing `basic_demo.sqlite` schema (Customer, Order, Item, Product, Supplier, ProductSupplier) unchanged; it already carried `Customer.email`/`email_opt_out` and `Order.CreatedOn`.
2. **Derived/predicted schema additions** — No SysConfig constants, no new FK/lookup columns, no Allocate junction tables. One new table: `SysEmail` (child of Customer) per the explicit spec — request fields only, fire-and-forget pattern (no Request Pattern response/audit columns needed).
3. **Create db** — `genai-logic create --project-name=demo_mcp_send_email --db_url=sqlite:///samples/dbs/basic_demo.sqlite`; 1 DDL change (`CREATE TABLE sys_email`) + `rebuild-from-database`; admin.yaml replaced from admin-merge.yaml (user confirmed).
4. **Run impl-req** — Check Credit: 2 sum, 1 formula, 1 copy, 1 constraint. Send Email: 1 `after_flush_row_event` (fire-and-forget). MCP client: added via `genai-logic genai-add-mcp-client` (generic tool — separate `mcp` bind-key db, `SysMcp` table, generated `row_event` logic file, Admin UI entry).
5. **Test data / testing** — No new seed needed; `basic_demo.sqlite`'s existing rows (5 customers incl. one opted-out, 5 orders spanning shipped/unshipped and before/after the cutoff date) already covered every test scenario. Verified live via curl against the running server (see Diagnostic Appendix).

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment**
Files read: `samples/prompts/demo_mcp_send_email.prompt.md` (all 3 sections), `database/models.py` (post-create)

| Step | Signal |
|---|---|
| Check Credit | All referenced columns (`balance`, `credit_limit`, `date_shipped`, `amount_total`, `quantity`, `unit_price`) already present in `basic_demo.sqlite` — no schema change |
| Send Email | New child table required (`SysEmail`) — `Rule.after_flush_row_event` fire-and-forget pattern; `Customer.email_opt_out` already present |
| MCP client | No direct DDL — handled by the dedicated `genai-logic genai-add-mcp-client` tool, which adds its own `mcp`-bind-key database (`SysMcp`) |

DDL change list:

| Table | Change | Reason |
|---|---|---|
| sys_email | CREATE TABLE (id, customer_id FK, subject, message, CreatedOn) | Send Email — child-of-Customer audit/request table, per spec |

**Phase 2 — CE / Pattern Assessment**
Files read: `logic_bank_api.md`, `logic_bank_patterns.md`, `RequestObjectPattern.md`

| Step | Rule Plan |
|---|---|
| Check Credit | `Rule.sum(Customer.balance)`, `Rule.sum(Order.amount_total)`, `Rule.formula(Item.amount)`, `Rule.copy(Item.unit_price)`, `Rule.constraint(Customer, balance<=credit_limit)` |
| Send Email | `Rule.after_flush_row_event(SysEmail, ...)` — logs "email sent" unless `customer.email_opt_out` |
| MCP client | Generic `genai-logic genai-add-mcp-client` — no custom rule authored |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct (n/a — no child-rollup-as-flag case here)
- [x] No `as_expression=lambda row: my_func(row)` — n/a, all formulas are direct lambdas
- [x] No `session.query()` inside formula or row_event
- [x] Boundary-operator convention applied: "less than the credit limit" → `<=` (matches CE's standing convention, not strict `<`)

**Implementation Plan**:

| Step | What was planned |
|---|---|
| 1 | `CREATE TABLE sys_email` + `rebuild-from-database` |
| 2 | Confirm/replace `admin.yaml` from `admin-merge.yaml` (user confirmed Replace) |
| 3 | `genai-logic genai-add-mcp-client` — adds SysMcp infra |
| 4 | Write `logic/logic_discovery/check_credit.py` |
| 5 | Write `logic/logic_discovery/send_email.py` |
| 6 | Start server, verify all 3 use cases live (curl) |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Reused existing seeded schema/data for Check Credit; added one child table for Send Email; used the project's own generic `genai-add-mcp-client` CLI tool (not hand-authored) for the MCP client, since it is documented in `integration/mcp/readme-mcp.md` as the supported way to add this feature |
| CE Files Loaded | logic_bank_api.md, logic_bank_patterns.md, RequestObjectPattern.md, implement_requirements.md, MCP_Copilot_Integration.md |
| Schema Read First | Yes — `database/models.py` and `basic_demo.sqlite`'s live schema/data read before writing any rule |
| Sample Data Read | Yes — existing `basic_demo.sqlite` seed rows read first; confirmed they already cover both opt-out and date-cutoff test scenarios, so no new seed script was written |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started, curl against `/api/Item`, `/api/SysEmail`, `/api/mcp-SysMcp`, and `logs/als.log` rule-fire trace checked for each use case |
| Lightweight Checks Used | Yes — curl + `logs/als.log` per use case |
| Gate Test Run Count | 1 per use case (diagnostic, not just final) |
| Gate Test Purpose | Diagnostic — confirmed constraint rejection, opt-out skip, and end-to-end MCP fan-out all fired correctly |
| Error Correction Loops | 2 (see below) |
| Long-Run Diagnostics | None — clean run |

**Error Correction Loops**:

```
Loop 1:
  Symptom:   First Check-Credit constraint test (inserting a huge Item against order_id=1) succeeded instead of rejecting.
  Diagnosis: order_id=1 was already shipped (date_shipped set), so it is excluded from the Customer.balance sum by design — not a rule bug.
  Fix:       Deleted the stray test Item, retried against an unshipped order (order_id=2); constraint correctly rejected with error 2001.
  Time:      ~1 min
  Root cause type: test design, not a CE/code gap.

Loop 2:
  Symptom:   POST to /api/SysMcp/ returned 405.
  Diagnosis: SysMcp lives on a separate `mcp` bind-key database; its JSON:API collection name is "mcp-SysMcp" (per `_s_collection_name` in the generated `database/mcp_models.py`), not "SysMcp".
  Fix:       Used /api/mcp-SysMcp/ — succeeded (201), full MCP flow traced in logs/als.log.
  Time:      ~1 min
  Root cause type: generic-tool naming convention, not a CE gap in the use-case logic I authored.
```

---

### 🔴 Review Required
*None — all decisions were specified or followed standard patterns.*

---

### 🟡 FYI
- `logic/logic_discovery/check_credit.py` — "less than the credit limit" implemented as `<=` per the CE's standing boundary-operator convention (not strict `<`).
- `logic/logic_discovery/send_email.py` — used `Rule.after_flush_row_event` (fire-and-forget, per `RequestObjectPattern.md`'s `SysEmail` worked example) rather than `commit_row_event`, since the two project training files name different event types for this exact pattern and `RequestObjectPattern.md` is the more detailed/authoritative one for this table shape.
- `database/models.py` / `database/mcp_models.py` — MCP client (3rd prompt section) implemented entirely via the project's own `genai-logic genai-add-mcp-client` CLI command rather than hand-authored rules, per `integration/mcp/readme-mcp.md`'s explicit instruction; no custom logic was written for this section.

</details>
