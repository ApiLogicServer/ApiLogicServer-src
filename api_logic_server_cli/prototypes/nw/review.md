---
title: nw_sample Review — CE Gaps, Contradictions, and Teaching Examples
notes: nw_sample predates Method 4 / System Creation Services and the logic_discovery convention; its domain content (declare_logic.py, models.py, admin.yaml, declare_security.py) was hand-built before AI-assisted creation existed. nw_sample also doubles as Val's pre-release regression test for LogicBank itself — read the "Also: LB Regression Test" section before treating anything here as simple tech debt. This review looks for patterns worth folding into CE training docs, and stale patterns worth flagging as superseded.
date: 2026-07-03
---

# nw_sample Review

## Caveat

nw_sample is **not** a pure "pre-AI" fossil — it has been retrofitted with current-generation CE scaffolding (`docs/training/*`, `logic/logic_discovery/`, `.github/.copilot-instructions.md` matching the current Manager version, a governance report, an auto-generated `docs/requirements/logic_flow_nw_sample.md`). What's genuinely pre-CE is the **domain content** (`declare_logic.py`, `models.py`, `admin.yaml`, `security/declare_security.py`) — a long-accumulated teaching/demo corpus, not something Method 4 would produce today. That gap — CE scaffolding present vs. CE conventions actually followed — is itself informative.

---

## Also: LB Regression Test — Read Before Treating Anything Here as Cleanup

**(Per Val, 2026-07-03.)** `nw_sample` is not just a rich teaching/demo project — it is Val's manual pre-release regression check for **LogicBank itself**, run before every LB release. This reframes several findings below:

- The **"CE Contradictions" section is not simply a list of anti-patterns to fix.** Some of what looks like tech debt (`declare_logic.py` as one large file rather than `logic_discovery/`, the `as_exp=` string parameter on `Rule.formula`, the custom `calling=` Kafka function, wildcard imports) may be **deliberately preserved to keep exercising specific LogicBank code paths** across releases — including possibly legacy/compat surfaces that must keep working even though current CE steers new projects away from them. Do not "clean up" or migrate this project's domain logic without first checking whether the pattern is intentionally there as a regression probe.
- The **`Ready` flag / min-cardinality workaround is likely doing double duty**: it's a genuine UX pattern (see the Origin Story above) *and* probably a deliberate exercise of commit-event timing, `Rule.count` reactivity, and cascade-add ordering — exactly the kind of thing a LogicBank release needs to verify hasn't regressed.
- **`test/api_logic_server_behave/features/place_order.feature`'s 11 scenarios are likely the actual pass/fail gate**, not merely a teaching example (see "Good Teaching / Support Examples" #1 below) — treat test failures here as release blockers, not documentation bugs.

**Practical implication:** findings in this review that read as "this should be modernized" are offered as CE/docs opportunities, not as a to-do list for editing `nw_sample`'s domain code. Any actual change to `nw_sample`'s logic, models, or admin.yaml should be run past Val first, specifically to check it isn't removing intentional LB test coverage.

---

## Origin Story: Min-Cardinality Constraints and Why `Ready` Exists

**(Per Val, 2026-07-03 — recorded here as design history, not independently re-derived from code alone.)**

This is part of a larger, classic problem: **minimum cardinality constraints** — e.g. "an Order must have at least one Item." LogicBank supports this via commit events (`Rule.commit_row_event`, which fires after row logic completes, so aggregates like `OrderDetailCount` are already finalized). But **getting this to work cleanly through SAFRS has never been reliable**, for a specific, structural reason:

**The core problem — "cascade add" PK stamping:** when a client submits an Order together with its Items in one request, the Order's primary key is **database-computed** (autoincrement). Each Item needs that PK **cascade-added** — stamped into its own FK column (`OrderId`) — before it can be considered "attached" to the parent, but the PK isn't assigned until flush. SAFRS's nested-object insert handling and LogicBank's row-logic timing don't line up cleanly enough to guarantee "check the child count" happens at a point where (a) cascade add has already stamped the parent PK into every child AND (b) it's still early enough to reject the whole transaction atomically if the count is zero. `declare_logic.py:130`'s own comment confirms half of this timing problem from the LogicBank side: *"the after_flush event makes Order.Id available"* — i.e., even Order's own PK isn't visible to rule code until after flush, let alone cascade-added to children in time for a pre-commit rejection.

**The workaround that emerged:** rather than solve "reject an empty Order at insert time" directly, `nw_sample` defers the cardinality check to a **later, explicit state transition** — the `Ready` flag (or shipping). See `do_not_ship_empty_orders` (`declare_logic.py:187-195`):
```python
def do_not_ship_empty_orders(row: Order, old_row: Order, logic_row: LogicRow) -> bool:
    if row.OrderDetailCount == 0:
        if logic_row.is_deleted():
            pass
        else:
            if row.ShippedDate is not None or row.Ready == True:
                raise ConstraintException("Empty Order - Cannot Ship or Make Ready")
Rule.commit_row_event(on_class=Order, calling=do_not_ship_empty_orders)
```
An empty Order can be inserted and sit around — the constraint only fires when the user tries to mark it `Ready` or ship it, by which point `OrderDetailCount` (a `Rule.count`, reliably reactive to child inserts) is trustworthy and the transaction boundary is unambiguous. This sidesteps the SAFRS nested-insert timing problem entirely, by never trying to enforce the constraint *at* insert time.

**The twist — it turned into better UX, not just a workaround:** what began as an engineering workaround for a SAFRS limitation was then recognized as a *better business workflow in its own right* — orders naturally go through a draft/staging state before being finalized ("Ready") for shipping, independent of whatever's true about the item count. The constraint timing problem and the UX both point to the same design: don't gate on cardinality at the moment of insert; gate on an explicit, user-controlled state transition, and let cardinality (and other completeness checks) be enforced at that transition instead.

**Why this matters for CE:** this is a reusable pattern for min-cardinality generally, not just this one Order/Item case — "a parent object with required children should have an explicit 'submit'/'finalize'/'ready' state, and cardinality constraints should be commit-events gated on *that* transition, not on raw insert." Nothing in current `logic_bank_api.md` or `logic_bank_patterns.md` documents min-cardinality-via-explicit-state-transition as a pattern, or explains *why* trying to enforce it at raw insert time is unreliable through SAFRS specifically. Worth a dedicated pattern writeup (possibly in `logic_bank_patterns.md` or a new `min_cardinality.md`), since "an Order must have Items" / "an Invoice must have Line Items" is an extremely common real-world ask that will otherwise get a naive (and broken) first attempt.

---

## CE Gaps

Patterns nw_sample uses that current CE training docs don't teach, and arguably should.

1. **The `Ready` flag — a user-controlled gate on aggregate inclusion, distinct from any derived/system column.** `Order.Ready` (`models.py:390`) is a plain boolean the user sets in the UI, and it participates directly in the core credit-check aggregate:
   ```python
   Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal,
       where=lambda row: row.ShippedDate is None and row.Ready == True)  # declare_logic.py:110-112
   ```
   This is worth calling out on its own because it demonstrates several things CE doesn't currently emphasize together:
   - **A `where=` clause can combine a system-derived condition (`ShippedDate is None`) with a user-set business flag (`Ready == True`)** — the aggregate isn't just "unshipped," it's "unshipped AND business-approved to count." CE's `Rule.sum`/`where=` examples are all single-condition; a compound business-state example would be more realistic.
   - **`Ready` gates more than the aggregate** — it also gates the outbound Kafka/n8n notification (`declare_logic.py:137-138, 148`: only fire `send_order_to_shipping`/n8n when `Ready == True` transitions from `False`→`True` or is `True` on insert), and it's enforced by a dedicated constraint preventing shipment of a not-ready order (`declare_logic.py:198-204`, `ship_ready_orders_only`). One flag, three independent rule types (sum where-clause, event trigger condition, constraint) all keyed off the same business state — a compact illustration of "declare the state once, every rule reacts to it independently," which is the core pitch CE already makes but doesn't have a single concrete multi-rule example for.
   - **Defaulting pattern**: `order_defaults` (`declare_logic.py:216-222`) explicitly sets `row.Ready = False` if not set in the UI, with a comment explaining *why*: `do_not_ship_empty_orders()` depends on `Ready` never being `None`. This is a good concrete instance of "always default booleans that participate in `where=`/constraint logic — `None` breaks `== True`/`== False` comparisons silently."
   - **This is a stronger real-world analog than STI's `type` discriminator** for teaching "a flag column changes which rules apply and what an aggregate counts" — worth considering as the primary example in `logic_bank_api.md`'s `Rule.sum`/`where=` section, with STI's `type` as the secondary/specialized case.

2. **PascalCase column naming isn't addressed.** `database/models.py` uses `Customer.Id`, `Order.AmountTotal`, `OrderDetail.UnitPrice`. Every CE example uses snake_case. Since Method 4 is DDL-driven and real-world/legacy DDL is often mixed-case, CE should state whether/how rules handle non-snake_case columns — same class of gotcha as the documented `type`/`Type` STI wire-naming issue, more general.

3. **Composite FK relationships aren't covered.** `Order` has `ForeignKeyConstraint(['Country', 'City'], ['Location.country', 'Location.city'])` (`models.py:369-371`), exposed in `admin.yaml` via a `tab_groups` entry with two `fks:` entries. CE's `child_role_name` guidance covers single-column ambiguity, not composite keys.

4. **`RuleExtension.copy_row` for audit trails isn't documented.** `declare_logic.py:282-285`:
   ```python
   RuleExtension.copy_row(copy_from=Employee, copy_to=EmployeeAudit,
       copy_when=lambda logic_row: logic_row.ins_upd_dlt == "upd" and
               logic_row.are_attributes_changed([Employee.Salary, Employee.Title]))
   ```
   One line replaces an 8-line manual alternative (kept commented out just below, as an intentional contrast). `logic_bank_api.md` never mentions `copy_row` or `are_attributes_changed`, despite audit trails being a common enterprise ask.

5. **`copy_children` / row-cloning isn't documented.** `declare_logic.py:301-313` — a full working "duplicate this Order and its OrderDetails" pattern (`Rule.row_event` + `logic_row.copy_children(...)`). Common business ask ("copy this order," "duplicate this quote"); absent from `logic_bank_api.md` and `logic_bank_patterns.md`.

6. **`Rule.early_row_event_all_classes` for cross-cutting stamping isn't documented.** `declare_logic.py:316-353` (`handle_all`) implements created/updated timestamp + user stamping + optimistic locking for every class in one hook, keyed off `hasattr(row, "CreatedOn")`. No CE guidance on this vs. per-table events for "stamp every table with who/when."

7. **A second Kafka-send function (`send_kafka_message`) isn't reconciled with CE's canonical `publish_kafka_message`.** `logic/logic_discovery/integration.py:56-70` and `declare_logic.py:139,162` use `send_kafka_message` with three call variants (raw `logic_row`, `payload=dict`, `row_dict_mapper=`). CE only teaches `publish_kafka_message(mapper=...)`. Worth confirming whether `send_kafka_message` is a still-supported parallel API or legacy.

8. **n8n webhook integration is entirely absent from CE.** Used in `declare_logic.py:149-157` and `integration.py:47,77,86-94`. If still supported, CE's EAI/Kafka sections should name-check it; if deprecated, flag to support.

9. **Multi-filter security interaction example is richer than what's likely in `security.md`.** `security/declare_security.py:51-70` stacks 4 `GlobalFilter`s (tenant isolation, department level, sales region, discontinued-product hiding) plus an explicit comment on how Filters AND together while Grants OR (lines 62-63, 87-89), with a worked resulting WHERE clause. Strong candidate to lift into `docs/training/security.md` if it doesn't already have an example this concrete.

10. **Dashboard/graphics generation isn't in CE's capabilities list.** `api/api_discovery/dashboard_services.py` references a `genai-graphics` CLI command (line 22: "rebuilt on `als genai-graphics`") — a first-class generated feature missing from `.github/.copilot-instructions.md`'s capabilities section.

---

## CE Contradictions

Patterns in nw_sample that conflict with current CE mandates — evidence the CE has since improved, not something to imitate.

1. **All core rules live in `logic/declare_logic.py`** (362 lines, ~14 weighted rules + 8 events) rather than `logic/logic_discovery/*.py`. The project's own governance report flags this as the #1 finding (-2 points, "needs migration"). Good "before" example for a legacy-migration doc; the governance report's suggested restructure (lines 103-116) is a usable template.

2. **Wildcard imports** (`from database.models import *`, `declare_logic.py:7`) — flagged by the project's own governance report as an anti-pattern. Other files in the same project (`simple_constraints.py`) already use explicit imports, showing internal inconsistency as the convention evolved.

3. **Custom `calling=` function for Kafka send contradicts CE's explicit "do NOT do this" example.** `declare_logic.py:125-162` wires a custom function via `calling=` with internal branching logic calling `kafka_producer.send_kafka_message` — this is close to verbatim the "WRONG" example in `logic_bank_api.md`'s event-handling section. Confirms CE's stricter guidance is a deliberate improvement, not an oversight.

4. **Latent one-event-per-class gotcha, undocumented as a constraint.** `integration.py:32` has a comment "important - only one after_flush_row_event per class," and indeed `fn_order_workflow` is defined in `integration.py` but never registered (only `Customer` and `Employee` get registered at lines 97-98) — likely because `Order` already has an event in `declare_logic.py`. This is a near-miss bug pattern worth documenting explicitly in `logic_bank_patterns.md`: LogicBank restricts one `after_flush_row_event` per class, so consolidate multiple concerns into a single dispatcher function, not multiple files each declaring their own event for the same class.

5. **`Rule.formula(derive=OrderDetail.ShippedDate, as_exp="row.Order.ShippedDate")`** (`declare_logic.py:251-252`) uses `as_exp=` (a string) — not a documented parameter anywhere in `logic_bank_api.md` (which only shows `as_expression=Callable`). Either a legacy/deprecated alias that still works, or silently broken. Needs engineering confirmation; either way it's an API-reference gap.

---

## Good Teaching / Support Examples

1. **`test/api_logic_server_behave/features/place_order.feature`** — 11 Behave scenarios (e.g. *"Alter Required Date - adjust logic pruned"*, *"Set Shipped - adjust logic reuse"*) each mapping directly to a rule in `declare_logic.py`. A compact, runnable demonstration of CE's core pitch — pruning and automatic reuse across change paths — matching the "9 Transaction Paths" table CE describes rhetorically, but here it's executable and asserted. Strong candidate for a support-facing walkthrough.

2. **`info_list`/`info_show` blocks in `admin.yaml` turn the running app into a self-guided tour.** E.g. Employee's `info_list` (lines 189-194) explicitly calls out the `Manager`/`Manages` virtual relationship and invites the user to click through it live. Category, Customer, Department, Order pages all have this. Worth recommending broadly as an onboarding technique: embed live, clickable tutorial text directly in `admin.yaml`, referencing specific rows/fields that demonstrate a feature (e.g. "login as `u1` vs `aneu` to see GlobalFilter tenant isolation").

3. **Two distinct `show_when` use cases, only one currently emphasized in CE.**
   - STI type-branching: `show_when: record["EmployeeType"] == "Hourly"` (`admin.yaml:210`) — matches CE's documented STI pattern exactly (double-quoted values, pure-letter field name).
   - Hiding server-derived fields until first save: `show_when: isInserting == false`, used repeatedly across Order/OrderDetail fields (Id, ShippedDate, AmountTotal, UnitPrice, Amount). This second pattern is arguably more universally useful than the STI case CE currently emphasizes, since "hide fields that don't exist yet" applies to nearly every project, not just STI ones. Worth promoting in CE/docs as the more common use case.

4. **`Employee.ProperSalary` via `@jsonapi_attr`** (`database/customize_models.py:62-87`) — a clean, minimal example of a computed API-only attribute with no backing rule or dependency tracking. Good FAQ answer to "how do I add a computed field that isn't a stored rule."

5. **`nw_sample_governance_report.md` itself** is a realistic, non-synthetic example of "vital signs" output — could be adapted directly into customer-facing docs showing what a health-check report looks like and how coverage/integrity scoring plays out on a real, imperfect project.

6. **Multi-tenant filter math spelled out in a comment**, `security/declare_security.py:87-89`:
   ```python
   # so user s1 sees the CTWSR customer row, per the resulting where from 2 global filters and 2 Grants:
   # where (Client_id=2 and region="British Isles") and (CreditLimit>300 or ContactName="Mike")
   ```
   An unusually concrete worked example of Filter-AND / Grant-OR interaction — exactly the kind of thing that generates support tickets ("why isn't my Grant excluding what I expected") and is rarely spelled out this explicitly elsewhere.
