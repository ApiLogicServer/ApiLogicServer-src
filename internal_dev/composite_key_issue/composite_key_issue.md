---
title: Composite-Key insert_parent + SAFRS — Investigation Notes
Description: insert_parent (Rule.sum/Rule.count) against a composite-natural-key parent had a
  real LogicBank engine bug, not a SAFRS bug as first suspected — it only manifested when a
  component of the composite key was set LATE (by an early_row_event) rather than at row
  construction time. Both the LogicBank bug (now fixed, gold source + regression test added)
  and the one genuine SAFRS bug (GET list default sort) are documented below.
Source: logic_bank/exec_row_logic/logic_row.py, logic_bank/rule_type/aggregate.py,
  safrs/jsonapi_formatting.py
Usage: Read this before recommending `insert_parent` with a composite/multi-column primary
  key as a CE pattern, and before touching SAFRS default-sort parsing for composite-PK models.
  As of v1.3, insert_parent + composite PK is SAFE to recommend — the fix shipped in
  LogicBank 1.34.00 (pyproject.toml pinned to >=1.34.00), with a regression test
  (examples/insert_parent_late_key in org_git/LogicBank).
version: 1.3
changelog:
  - 1.3 (Sep 10 2026) - **Released**: LogicBank 1.34.00 (Val) ships the v1.2 fix.
    `pyproject.toml` bumped to `LogicBank>=1.34.00` in gold source. Verified the PyPI
    package matches gold source exactly (`logic_row.py`/`aggregate.py` byte-identical)
    and re-ran `genai_demo_sales`'s Behave suite against the real release — 4/4 scenarios
    pass. No code changes from v1.2; this entry just closes out the "fixed but not yet
    released" status.
  - 1.2 (Sep 9 2026) - ROOT CAUSE CORRECTED — this was a LogicBank engine bug, not a SAFRS
    bug. What v1.0/1.1 called "Bug 2" (POST silently drops a composite-FK column) was actually
    two LogicBank bugs, reproducible with zero SAFRS/Flask involved (a plain
    `session.add(Order(...)); session.commit()` reproduced it identically — see "Corrected Root
    Cause" below). Both are fixed in `logic_bank/exec_row_logic/logic_row.py` and
    `logic_bank/rule_type/aggregate.py` (org_git/LogicBank gold source), verified against the
    full LogicBank test suite (`run_tests.py` — all 15 example directories including the 16+ NW
    tests, ALL PASSED, no regressions) and a new regression test,
    `examples/insert_parent_late_key`, that exercises exactly the timing gap the original
    `examples/insert_parent` test doesn't cover (see "Why the existing test passed" below).
    Re-tested end to end against the checked-in `genai_demo_sales` project: `insert_parent`
    now works correctly through the plain JSON:API `POST /api/Order/` path too — the SAFRS
    layer was never at fault, so fixing LogicBank fixed that path automatically as a side
    effect. Bug 1 (SAFRS default-sort) is unaffected by this — it's a real, separate, narrow
    SAFRS bug, still open, still has its workaround. **insert_parent + composite PK is now
    safe to recommend as a CE pattern** — the blocking condition from v1.1 no longer applies.
  - 1.1 (Sep 9 2026) - Val checked the reproduction artifacts into this same folder: the
    originating prompt (`genai_demo_sales.prompt`) and the full generated project
    (`genai_demo_sales/`), frozen at the exact schema state ("Schema iteration 2" below) that
    reproduces both Bug 1 and Bug 2. Previously this doc pointed at the transient
    `build_and_test/genai-logic/genai_demo_sales` workspace copy; updated all references and
    added a Reproduction section with concrete setup/run/repro steps against the checked-in copy.
  - 1.0 (Sep 9 2026) - Initial investigation. Found live while building a "SalesRepTotal"
    monthly-rollup sample (genai_demo_sales, build_and_test/genai-logic) to validate exposing
    `insert_parent` as a documented CE pattern. Confirmed the underlying LogicBank mechanism
    is sound (matches the existing `examples/insert_parent` test exactly); confirmed two
    separate SAFRS-layer bugs that block it from working end-to-end in a real generated
    project. One (GET list default sort) has a clean workaround. The other (POST silently
    drops a composite-FK column) does not yet have a known fix or convention — Val recalled
    "there might have been some workaround or convention" but this session's search of gold
    source, LogicBank, and SAFRS itself did not turn one up. Filed here for follow-up rather
    than guessing further.
---

# Composite-Key `insert_parent` + SAFRS — Investigation Notes

## Status (v1.2): LogicBank bug fixed and tested; 1 narrow SAFRS bug remains, with a workaround

**⚠️ Everything under "Part 2" / "Bug 2" below is the ORIGINAL (v1.0/1.1) investigation and is
now known to be a partially incorrect diagnosis** — kept intact for the record, but see
"Corrected Root Cause (v1.2)" further down for what was actually wrong and how it was fixed.
Bug 1 (SAFRS default-sort) is unaffected and still accurate as originally written.

| # | Symptom | Where | Status |
|---|---|---|---|
| 1 | `GET /api/<Resource>/` on a composite-PK class → `500`, `no such column: <table>.id` | SAFRS `jsonapi_sort()` default-sort path | ✅ Confirmed workaround — pass explicit `?sort=<real_pk_column>` |
| 2 (corrected) | `insert_parent` silently fails to create the parent AND nulls the child's own composite-FK columns, when a component of the key is set by an `early_row_event` rather than at row construction | **LogicBank**, not SAFRS — `logic_row.py` (`_get_parent_logic_row`, `_is_inserted_parent`) + `aggregate.py` (`adjust_from_inserted_child`) | ✅ Fixed in gold source (org_git/LogicBank), regression test added (`examples/insert_parent_late_key`), verified against `genai_demo_sales` end to end including the plain JSON:API POST path |

## Status (original, v1.0/1.1 — see correction above)

| # | Symptom | Where | Workaround? |
|---|---|---|---|
| 1 | `GET /api/<Resource>/` on a composite-PK class → `500`, `no such column: <table>.id` | SAFRS `jsonapi_sort()` default-sort path | ✅ Yes — pass explicit `?sort=<real_pk_column>` |
| 2 | `POST /api/<Child>/` with a column that's part of a **composite** relationship FK, given as a plain JSON:API attribute → silently dropped (ends up `null`), no error | SAFRS attribute/relationship parsing on create (exact site not yet pinned down) | ❌ Not found |

Bug 2 is the more serious one: it means a composite-key parent (the whole point of `insert_parent` for a "bucket/rollup" pattern — see Motivation below) can't be populated through plain JSON:API POST at all, silently, with no error to signal the problem.

**Reproduction artifacts are checked in alongside this doc:**
- [`genai_demo_sales.prompt`](./genai_demo_sales.prompt) — the originating domain prompt
- [`genai_demo_sales/`](./genai_demo_sales/) — the full generated project, frozen at the exact schema state that reproduces both bugs ("Schema iteration 2" below — composite PK on `SalesRepTotal`, overlap already fixed). See **Reproduction** at the end of this doc for exact steps.

&nbsp;

## Motivation: why this was being tested

Building out a domain prompt (`genai_demo_sales.prompt`, originally drafted in the local Manager workspace) that included:

> On Placing Orders, maintain sales totals
>   1. Orders can be assigned to people who are salesreps
>   2. Maintain monthly sales totals and order counts for each sales rep

This is a "bucket/rollup" requirement: a `SalesRepTotal(sales_rep_id, year_month)` row that should be **auto-created on first reference** and incrementally maintained thereafter — no pre-seeding of all possible rep/month combinations. `Rule.sum`/`Rule.count`'s `insert_parent=True` parameter is documented for exactly this ("create parent if it does not exist") but is otherwise unused/undocumented anywhere in the CE beyond its one-line docstring, and carries the caution "do not use unless directly requested." Before recommending it as a documented CE pattern with a real sample, it needed to be verified live — which surfaced this.

&nbsp;

## Part 1 — confirmed working: bare LogicBank, no SAFRS

`org_git/LogicBank/examples/insert_parent/` — an existing, currently-passing test (`test_summary.txt` line 30: `examples/insert_parent/tests PASSED`), not previously connected to any GenAI-Logic sample.

- `db/models.py`: `Parent` has a **composite natural primary key** — `parent_attr_1`, `parent_attr_2` both `primary_key=True`, no surrogate `id` column at all. `Child` has plain columns `parent_1`, `parent_2` tied to `Parent` via `ForeignKeyConstraint([parent_1, parent_2], [Parent.parent_attr_1, Parent.parent_attr_2])`.
- `logic/rules_bank.py`: `Rule.sum(derive=Parent.child_sum, as_sum_of=Child.summed, insert_parent=True)` and the same shape for `Rule.count`.
- `tests/test_insert_parent.py` Test 1: `Child(parent_1="auto_inserted", parent_2="parent", summed=2, ...)`, plain `session.add()` + `commit()` — no parent row exists yet for that key. LogicBank inserts the `Parent` row itself and seeds the aggregate correctly (confirmed via `tests/passes.log`: `{Insert Parent: Parent}` → `{Insert - Insert Parent from Child}` → `{Update - Adjusting Parent: child_sum, child_count}`).
- Test 2 (re-parenting): changing the child's key columns to a new, still-nonexistent key auto-creates *that* parent too, and decrements the old one back to 0.

This is raw SQLAlchemy + LogicBank — no Flask, no SAFRS, no JSON:API layer. **Confirms `insert_parent` itself works correctly against a composite natural-key parent.**

Mechanism (`org_git/LogicBank/logic_bank/exec_row_logic/logic_row.py`):
- `_load_parents_on_insert()` (~line 1075) iterates every `MANYTOONE` relationship on the child. For each with a non-null FK, it calls `_get_parent_logic_row(role_name)`.
- `_get_parent_logic_row()` (~line 248) builds `parent_key` as a **dict** (`{parent_col.name: getattr(row, child_col.name), ...}`, from `relationship.local_remote_pairs`) and calls `session.query(parent_class).get(parent_key)`.
- If that returns `None`, `_is_inserted_parent()` (~line 806) checks whether any aggregate on that relationship has `insert_parent=True`; if so, it constructs a new instance of the parent class, copies the FK values across via `local_remote_pairs` (positionally, not via the dict), and inserts it — `inserted_parent_row.insert(reason=f'Insert Parent from {self.name}')`.
- `_is_foreign_key_null()` — if any column in the composite FK is null, the relationship is treated as "no parent to load," and `insert_parent` is never attempted at all (no error, silent no-op). **This detail matters for Bug 2's downstream symptom — see below.**

&nbsp;

## Part 2 — building it into a real project: `genai_demo_sales`

Project location: [`genai_demo_sales/`](./genai_demo_sales/), checked in next to this doc (originally built in the local Manager workspace at `build_and_test/genai-logic/genai_demo_sales`, then copied here by Val as a permanent, self-contained repro artifact). Schema: `Customer`/`Order`/`Item`/`Product` (standard check_credit shape) plus `SalesRep` and `SalesRepTotal(sales_rep_id, year_month, total_amount, order_count)`, with `Order.sales_rep_id` + `Order.year_month` as a composite FK to `SalesRepTotal`. `year_month` is set via a plain `Rule.early_row_event` (never derive an FK-participating column with `Rule.formula` — same existing CE rule, just applying it to a column that's part of a *composite* FK rather than a single-column one).

### Schema iteration 1 — surrogate `id` PK + `UNIQUE(sales_rep_id, year_month)`

The "obvious" SAFRS-friendly shape: a normal auto-increment `id` primary key, with the natural key enforced via a separate unique constraint.

**Result:** `POST /api/Order/` → `500`:
```
Generic Error: Incorrect number of values in identifier to formulate primary key for session.get();
primary key columns are 'sales_rep_totals.id'
```
**Root cause:** `_get_parent_logic_row()`'s `parent_key` dict has 2 entries (from the composite relationship's `local_remote_pairs`: `sales_rep_id`, `year_month`), but the real mapper primary key is just `('id',)` — a genuine count mismatch. `insert_parent`'s lookup mechanism is coupled to the relationship's FK columns, not to whatever the model's actual primary key happens to be. **This confirms: the composite natural key must be the actual primary key for `insert_parent` to work at all** — a surrogate `id` + unique constraint does not.

### Schema iteration 2 — composite PK, matching the LogicBank test exactly

Dropped the surrogate `id`; made `(sales_rep_id, year_month)` the literal primary key, exactly like `examples/insert_parent`'s `Parent` class.

**New problem surfaced:** `rebuild-from-database` generated **three overlapping relationships** all touching the shared `sales_rep_id` column: `Order.sales_rep` (single-column, → `SalesRep`), `Order.sales_rep_total` (composite, → `SalesRepTotal`), `SalesRep.OrderList`. SQLAlchemy warned at mapper-configuration time:
```
SAWarning: relationship 'Order.sales_rep_total' will copy column sales_rep_totals.sales_rep_id
to column order.sales_rep_id, which conflicts with relationship(s): 'SalesRep.OrderList' ...
```
**Effect (not just a warning — a real silent bug):** in a direct-Python insert test (bypassing curl/SAFRS, calling `session.add(Order(...)); session.commit()` directly), `order.year_month` ended up `None` in the persisted row even though the `early_row_event` correctly set it (confirmed `order_date` persisted correctly in the same row — only `year_month` was wiped). Because `year_month` was null, `_is_foreign_key_null()` correctly-per-its-own-logic treated the composite FK as "not set" and **skipped `insert_parent` entirely** — no error, no `SalesRepTotal` row created, nothing to indicate anything went wrong. The likely mechanism: `_load_parents_on_insert()` unconditionally does `setattr(row, role_name, parent_row)` for every non-null-FK many-to-one relationship it processes (including the plain `sales_rep` role) — with two relationships both claiming `sales_rep_id`, resolving one appears to disturb the composite key state of the other.

**Fix:** dropped the redundant single-column FK constraint on `Order.sales_rep_id` entirely, so `sales_rep_id` is owned by exactly one relationship (the composite one to `SalesRepTotal`). Rebuild showed no more overlap warnings.

**Lesson for the CE, independent of the two SAFRS bugs below:** if a bucket/rollup pattern's key column (e.g. `sales_rep_id`) is *also* wanted as an ordinary direct FK elsewhere (e.g. "which sales rep is this order assigned to," queried directly rather than through the bucket), **do not declare both relationships on the same column set.** Access the single-column relationship transitively instead (`order.sales_rep_total.sales_rep`), or the composite key silently corrupts.

### Bug 1 — `GET` list endpoint, confirmed SAFRS bug, confirmed workaround

With the overlap fixed, `GET /api/SalesRepTotal/` (no `?sort=` param) → `500`:
```
Generic Error: (sqlite3.OperationalError) no such column: sales_rep_totals.id
[SQL: SELECT sales_rep_totals.id AS sales_rep_totals_id, ... FROM sales_rep_totals
      ORDER BY sales_rep_totals.id LIMIT ? OFFSET ?]
```
**Root cause**, `venv/.../site-packages/safrs/jsonapi_formatting.py`, function `jsonapi_sort()`:
```python
sort_attrs = request.args.get("sort", "") or "id"   # <-- defaults to "id" with no ?sort= given
...
if sort_attr == "id":
    if attr is None:
        if safrs_object.id_type.primary_keys:
            attr = getattr(safrs_object, safrs_object.id_type.primary_keys[0], None)  # todo: composite keys edge case
```
That `# todo: composite keys edge case` comment is in SAFRS's own source — this is an acknowledged gap in the library, not something GenAI-Logic introduced. `getattr(cls, "id", None)` for a composite-PK class does not cleanly hit the intended fallback, and the query ends up ordering by a column that doesn't exist.

Note this is a distinct SAFRS mechanism from the composite-`id` support that *does* exist and work: `safrs/safrs_types.py` (`get_id_type`, `SAFRSID` — synthesizes a single JSON:API `"id"` string by delimiter-joining composite PK values, used correctly elsewhere e.g. `safrs/base.py` `get_instance()` via `cls.id_type.get_pks(id)` + `.filter_by(**primary_keys)`). The *default-sort* code path specifically doesn't use that machinery.

**✅ Confirmed workaround:** pass an explicit sort on a real column — `GET /api/SalesRepTotal/?sort=sales_rep_id` — which takes the `elif` branch instead (`attr = getattr(safrs_object, sort_attr, None)`, a genuine mapped column) and works normally.

### Bug 2 — `POST` silently drops a composite-relationship FK column, ORIGINALLY FILED AS OPEN (see correction below — this was misdiagnosed as SAFRS; actual root cause and fix are in "Corrected Root Cause (v1.2)")

With Bug 1's cause understood but *not yet fixed in code*, tested `POST /api/Order/` via Flask's `test_client()` directly (to get real exceptions instead of the wrapped generic-500 curl shows):

```python
client.post('/api/Order/', json={'data': {'type': 'Order', 'attributes': {
    'customer_id': 2, 'sales_rep_id': 3, 'notes': 'test'}}}, ...)
# → 201, but the returned resource shows:
#   "customer_id": 2        (posted correctly)
#   "sales_rep_id": null    (silently dropped — posted as 3)
#   "year_month": null
```
`customer_id` — an **ordinary single-column FK** — is accepted as a plain attribute and set correctly. `sales_rep_id` — part of the **composite** relationship's FK — is silently discarded, with no error anywhere. The order is created, but with no sales rep assignment and (consequently, per `_is_foreign_key_null()` above) no `SalesRepTotal` bucket row created either — a second silent no-op, this time from the API layer rather than the ORM/relationship-overlap layer.

**Hypothesis, not confirmed:** SAFRS may special-case columns that participate in a multi-column relationship, deferring them to JSON:API `"relationships"`-section linkage rather than accepting them as flat `"attributes"` — while a single-column FK is accepted either way. Exact code site not pinned down (candidates: `safrs/base.py` `_s_post`/`__init__` attribute-vs-relationship-key parsing around line ~305–331, or `_s_jsonapi_attrs` construction filtering out composite-relationship-owned columns).

**Why the JSON:API-"correct" alternative doesn't actually solve this use case:** the standard JSON:API way to set a relationship is `"relationships": {"sales_rep_total": {"data": {"type": "SalesRepTotal", "id": "<composite-id>"}}}` — but that requires linking to an **already-existing** `SalesRepTotal` resource. `insert_parent`'s entire value proposition is auto-creating that resource on first reference. If the only way to populate the composite FK through JSON:API is to link to a pre-existing resource, `insert_parent` provides no benefit through the API layer even if it works perfectly at the ORM/LogicBank level.

**Not found despite searching:** gold source (`ApiLogicServer-src`), `LogicBank`, and the installed `safrs` package itself were searched for a documented convention, config flag, `column_property`/`synonym` trick, or naming pattern that makes a composite-relationship FK column POST-able as a flat attribute. Val recalled "there might have been some workaround or convention" for the general composite-key/`id` issue — Bug 1's workaround (explicit `?sort=`) is confirmed and real, but nothing was found specifically for Bug 2.

&nbsp;

## Corrected Root Cause (v1.2) — this was a LogicBank bug, not a SAFRS bug

Everything above this point is the original investigation, preserved as-written. It correctly
identified the *symptom* (silent null, no error) but wrongly attributed it to SAFRS's
attribute-vs-relationship parsing on POST. The real bug lives entirely inside LogicBank,
reproduces with **zero SAFRS/Flask involved**, and is fixed as of this version.

**Proof it's not SAFRS:** a pure SQLAlchemy insert — no LogicBank, no SAFRS — does NOT null the
FK:
```python
order = models.Order(customer_id=2, sales_rep_id=4, year_month="2026-09")
session.add(order); session.flush()
# order.sales_rep_id, order.year_month: unchanged, exactly as set
```
A direct-Python insert *with LogicBank activated* (still no SAFRS/Flask) reproduces the exact
`sales_rep_id: null` symptom. That isolates the bug to LogicBank's own rule-execution code.

### The two real bugs, both in `logic_bank/exec_row_logic/logic_row.py` and `logic_bank/rule_type/aggregate.py`

**Bug A — `LogicRow._get_parent_logic_row()` (`logic_row.py`, ~line 289):** when no parent row
exists yet for the child's current FK values, this method does:
```python
parent_row = parent_query.get(parent_key)   # None - no SalesRepTotal exists yet
setattr(row, role_name, parent_row)         # setattr(row, 'sales_rep_total', None)
```
For a **composite/multi-column** relationship, SQLAlchemy's relationship setter treats
`setattr(child, relationship_name, None)` as "detach from this parent" and, as a side effect,
**nulls the child's own FK columns** (`sales_rep_id`, `year_month`) to keep them consistent
with "no parent assigned." A single-column FK relationship doesn't hit this the same way — the
FK column *is* the relationship's only local column, so there's no separate multi-column state
to desync. This silently destroys the child's real, correct FK values before anything else
(including `insert_parent`) gets to use them.

**Bug B — `Aggregate.adjust_from_inserted_child()` (`rule_type/aggregate.py`, ~line 96):** this
is the method that actually runs for a `Rule.sum`/`Rule.count(insert_parent=True)` aggregate
when the child's composite FK only becomes fully non-null *after* `_load_parents_on_insert()`'s
own insert_parent check already ran (see "Why the existing test passed" below — this is the
common case for any FK component set by an `early_row_event`, like a computed date/bucket key).
Before the fix, when this method found no existing parent, it just gave up:
```python
if parent_adjustor.parent_logic_row.row is None:
    parent_adjustor.parent_logic_row = None
    return   # <-- never checked self.insert_parent, never called _is_inserted_parent()
```
This is the actual reason a `SalesRepTotal` bucket was never created at all through this path —
`insert_parent`'s own creation logic (`LogicRow._is_inserted_parent()`) was correctly
implemented, but this call site — the only one still live once the FK is fully known — never
invoked it.

### Why `examples/insert_parent`'s existing test didn't catch this

`examples/insert_parent/tests/test_insert_parent.py` constructs its child like this:
```python
new_child = models.Child(parent_1="auto_inserted", parent_2="parent", summed=2, ...)
```
**Both** composite-key columns (`parent_1` AND `parent_2`) are set directly in the constructor,
before the row is even added to the session. So by the time
`LogicRow._load_parents_on_insert()` runs (the very first check on insert, before any
`early_row_event` fires), `_is_foreign_key_null()` already sees the FK as fully non-null, calls
`_get_parent_logic_row()` right there, finds no parent, and `_is_inserted_parent()` creates one
— all in a single, self-contained pass. By the time `Aggregate.adjust_from_inserted_child()`
(Bug B's location) runs later, the parent already exists, so its `if ... is None: return` early
exit is never reached at all. **The test's own child-construction shape structurally avoids
exercising the exact code path that's broken.**

`genai_demo_sales`'s `Order.year_month` is different: it is *part of the composite FK to
`SalesRepTotal`* but cannot be set at construction time — it's computed from `order_date`,
which itself may be defaulted "now" — so it's set by
`Rule.early_row_event(on_class=Order, calling=set_order_date_and_month)`, same pattern the CE
mandates for any FK-participating column that isn't a raw client input (`never derive an
FK-participating column with Rule.formula` — the general CE rule this project already followed
correctly). `early_row_event`s run *after* `_load_parents_on_insert()`'s first pass (see
`LogicRow.insert()`: `_load_parents_on_insert()` at line ~1346, `_early_row_events()` at line
~1347, in that order). So at `_load_parents_on_insert()` time, `year_month` is still `None`,
`_is_foreign_key_null()` correctly says "nothing to load yet" and skips — and the *only*
remaining code path that could ever create the parent is `Aggregate.adjust_from_inserted_child()`,
which is exactly where Bug B lived.

**The general lesson:** `insert_parent` was only ever exercised, by any existing test, in the
"all composite-key columns known at construction" shape. Any composite parent key with a
component that's legitimately computed rather than client-supplied — which is the normal,
expected shape for a "bucket" pattern keyed by a derived period/bucket value — took a different,
untested code path that had two real bugs in it.

### The fix

- `logic_row.py`, `_get_parent_logic_row()`: when nulling a composite relationship because no
  parent was found, capture the child's real FK values first and restore them immediately after
  the `setattr()` that would otherwise wipe them.
- `logic_row.py`, `_is_inserted_parent()`: same capture-before-`setattr()` pattern, since linking
  the newly-created (still-empty) parent object has the identical side effect.
- `aggregate.py`, `adjust_from_inserted_child()`: when no parent is found AND the aggregate
  declared `insert_parent=True`, call `LogicRow._is_inserted_parent()` to actually create the
  parent, instead of silently giving up.

**Verified:**
- Full LogicBank test suite (`python3 run_tests.py`, org_git/LogicBank) — all 15 example
  directories including the 16+ NW business-logic tests — `ALL PASSED`, no regressions.
- New regression test `examples/insert_parent_late_key` (see below) — fails without the fix
  (confirmed by reverting it and re-running), passes with it.
- `genai_demo_sales` end to end: creating an `Order` with a `sales_rep_id` correctly
  auto-creates the `SalesRepTotal` bucket on first reference and correctly adjusts it (not
  re-creates it) on subsequent orders for the same rep/month; a different rep correctly gets a
  separate bucket. Tested both through the custom `CreateOrderWithItems` endpoint and — as an
  unplanned but confirming side effect — through the **plain JSON:API `POST /api/Order/`** path
  that v1.0/1.1 called "Bug 2." That path now works correctly too, without any SAFRS change,
  which is itself confirmation that SAFRS was never the actual cause.

### New regression test: `examples/insert_parent_late_key`

`org_git/LogicBank/examples/insert_parent_late_key/` — same shape as `examples/insert_parent`
(a composite natural-key `Parent`, a `Child` with `Rule.sum`/`Rule.count(insert_parent=True)`),
but `Child.period` (part of the composite FK) is set by an `early_row_event`
(`set_period()`), not at `Child()` construction — deliberately reproducing the timing gap
described above. Three tests: (1) insert_parent creates the parent and the child's own FK
columns survive; (2) a second child for the same late-set key adjusts the existing parent
rather than re-creating it or losing its FK a second time; (3) a child for a different late-set
key creates a separate parent bucket and leaves the first one untouched. All three fail without
the fix (confirmed) and pass with it. Auto-discovered by `run_tests.py` like every other
`examples/*/tests` directory.

&nbsp;

## Open questions / next steps

**⚠️ Superseded by the v1.2 fix above** — kept for historical record. Item 3's blanket
recommendation ("do not recommend insert_parent + composite PK") no longer applies; the new
Status table at the top of this doc reflects the current, correct guidance.

1. **Bug 2 root cause** — needs a debugger session or closer reading of `safrs/base.py`'s attribute-vs-relationship parsing (`_s_parse_object_id`, `_s_post`, `_s_jsonapi_attrs` construction) to pin down exactly where/why a composite-relationship column is excluded from flat-attribute assignment on create.
2. **Is there a real convention Val is recalling?** — possibilities not yet tried: a custom API endpoint (bypass JSON:API CRUD entirely, plain SQLAlchemy insert with the FK columns set directly — this is known to work, per Part 1); a `jsonapi_attr`-decorated writable property that proxies to the raw columns; exposing the composite FK columns as ordinary (non-relationship) columns to SAFRS somehow while keeping the relationship for LogicBank's `insert_parent` to use.
3. **If no convention exists**, this may be worth filing as two separate upstream issues against SAFRS (Bug 1 is small/clear enough to be a good candidate; Bug 2 needs root-causing first) and, in the interim, documenting in the CE that `insert_parent` with a composite/multi-column primary key is **usable at the LogicBank/ORM level but not currently usable through plain JSON:API POST** — i.e., don't recommend it as a general "no code" CE pattern until Bug 2 is understood, without a custom API endpoint as the practical workaround for real projects.

Do not recommend `insert_parent` + composite PK as a documented, general-purpose CE pattern until at least Bug 2 is resolved or a working convention is confirmed — the failure mode (silent null, no error) is exactly the kind of thing that erodes trust in generated systems.

&nbsp;

## Reproduction

The checked-in [`genai_demo_sales/`](./genai_demo_sales/) is frozen at the exact schema/logic state that reproduces both bugs — no rebuild or schema changes needed, just install and run.

**Setup:**
```bash
cd internal_dev/composite_key_issue/genai_demo_sales
python3 -m venv venv
source venv/bin/activate   # or venv_setup/venv.ps1 on Windows
pip install -r requirements.txt
python api_logic_server_run.py &
sleep 5
```
`database/db.sqlite` already has seed data (`Customer` id 2, `SalesRep` ids 3/4, `Product` ids 3/4 — see `database/test_data/alp_init.py` for how it was seeded; re-run that script against a fresh `db.sqlite` if needed).

**Bug 1 — GET list crash, and its workaround:**
```bash
curl 'http://localhost:5656/api/SalesRepTotal/'
# → 500: no such column: sales_rep_totals.id

curl 'http://localhost:5656/api/SalesRepTotal/?sort=sales_rep_id'
# → 200, works correctly
```

**Bug 2 — POST silently drops the composite-relationship FK column:**
```bash
curl -X POST http://localhost:5656/api/Order/ \
  -H 'Content-Type: application/vnd.api+json' \
  -d '{"data": {"type": "Order", "attributes": {"customer_id": 2, "sales_rep_id": 3, "notes": "order 1"}}}'
# → 201, but the returned resource shows "sales_rep_id": null, "year_month": null
#   (customer_id, an ordinary single-column FK, correctly shows 2)
```
For a real traceback instead of curl's wrapped generic-500 on Bug 1 (before applying the `?sort=` workaround), use Flask's test client in-process rather than a live server + curl — this is how Bug 2's exact symptom (silent null, not an exception) was found:
```python
# run from genai_demo_sales/, venv activated
import os, sys, logging
sys.path.insert(0, '.')
from config import server_setup
from flask import Flask
import config.config as config

app_logger = server_setup.logging_setup(); app_logger.setLevel(logging.INFO)
flask_app = Flask('t')
flask_app.config.from_object(config.Config)
args = server_setup.get_args(flask_app)
server_setup.api_logic_server_setup(flask_app, args)

client = flask_app.test_client()
resp = client.post('/api/Order/', json={'data': {'type': 'Order', 'attributes': {
    'customer_id': 2, 'sales_rep_id': 3, 'notes': 'test'}}},
    headers={'Content-Type': 'application/vnd.api+json'})
print(resp.status_code, resp.get_data(as_text=True))
```
