# Locking Strategy: Client Opt-Locking vs. LogicBank Cascaded Aggregate Adjustments

**Date:** 2026-08-21 (Option D added same day, following up on Val's "what if we added opt locking for parent reads?")
**Context:** Val's working hypothesis going in was that LogicBank's own cascaded updates (e.g. a Rule.sum adjusting `Customer.balance` from an `Order` insert) are multi-user safe in the sense that "they may abort with an opt-locking error, but are safe if they succeed." Code inspection across `ApiLogicServer-src` and `LogicBank` shows this is **not** what happens. The client-facing PATCH path is opt-lock protected. LogicBank's own cascaded aggregate adjustments are not protected by that mechanism *or* by anything else — they are a genuine, silent lost-update race under concurrent writers, on any RDBMS with the (typical) default READ COMMITTED isolation. This doc documents the mechanism precisely, gives a concrete business-critical failure scenario using the framework's own flagship example, and proposes fix options at the LogicBank engine level.

## TL;DR

- **Original assumption was wrong.** LogicBank's cascaded aggregate adjustments (`Rule.sum`/`Rule.count`, e.g. `Customer.balance`) are **not** protected today — not by the existing client-facing opt-lock (scoped to `nest_level == 0` only), and not automatically by SQLAlchemy (which offers locking primitives but applies none of them by default). It's a silent lost-update race, not a safe abort.
- **Proposing:** a new `TRANS_UPDATE_LOCKING` env var (`ignored` default / `pessimistic`) — parallel to, and independent of, the existing client-facing `OPT_LOCKING`. Named deliberately unlike `OPT_LOCKING`: `TRANS_` marks it as transaction-internal (not client-facing), `UPDATE_` names the moment it applies — LogicBank's own cascaded parent *updates* mid-transaction, not the original client write. If the env var is unset, behavior is `ignored` (today's behavior, unchanged) — same fallback convention as `OPT_LOCKING` itself. `pessimistic` wires `with_for_update()` into the single internal LogicBank method every aggregate adjustment already passes through. This is a transaction-internal lock; it does not apply to, and does not change, client-side opt-locking.
- **Also designed, deferred:** an optimistic (`trans-optimistic`) alternative. Its bare form makes every caller pay a permanent tax (a write can fail on a row it never touched); a server-side auto-retry variant removes that tax but introduces an unresolved risk of side-effecting rules (Kafka, email) double-firing on retry. Not building either until a real, measured need appears.
- **Why LogicBank fixes this, not SQLAlchemy:** `with_for_update()` is a per-call-site discipline with no completeness guarantee — someone eventually adds a new write path and misses it, silently. Same structural weakness procedural business logic has vs. declarative rules; same fix applies (enforce once, at the one place all paths already funnel through). See Appendix B.

## Summary

| Write path | Protected? | Mechanism | Failure mode if unprotected |
|---|---|---|---|
| Client PATCH (the row the API caller directly submitted) | ✅ Yes | Custom checksum compare (`opt_lock_patch`), gated to `nest_level == 0` | `409` — visible, safe |
| LogicBank cascaded parent adjustment (Rule.sum / Rule.count, `nest_level > 0`) | ❌ No | None — Python read-modify-write, blind SQL `UPDATE` | Silent lost update; can silently violate a same-transaction constraint (e.g. credit limit) |
| Rule.copy (child snapshot of parent value) | ⚠️ Lower risk | Reads parent's current session/DB value into a new child column | Read-skew (stale copy), not corruption of a shared value |

## 1. What actually protects the client PATCH path

[`all_classes_stamping.py`](../api_logic_server_cli/prototypes/base/logic/logic_discovery/system/all_classes_stamping.py) wires a single cross-cutting handler for every class:

```python
if logic_row.is_updated() and logic_row.old_row is not None and logic_row.nest_level == 0:
    opt_locking.opt_lock_patch(logic_row=logic_row)
```

[`opt_lock_patch`](../api_logic_server_cli/prototypes/base/api/system/opt_locking/opt_locking.py#L146) compares:
- `as_read_checksum` — the `S_CheckSum` the client got on its original GET and echoed back on PATCH
- `old_row_checksum` — a SHA-256 hash of every column's current on-disk value (`checksum_old_row`, called against LogicBank's `old_row`, i.e. what's actually in the DB right now)

Mismatch → `ALSError("Sorry, row altered by another user...")`, a clean `409`. This is entirely custom (SHA-256 over all columns), not SQLAlchemy's built-in `version_id_col` mechanism — confirmed via `grep -rn "version_id_col"` across the whole `api_logic_server_cli` tree: zero hits. SQLAlchemy provides no independent safety net here; this hand-rolled check is the *only* protection in the system, and it is explicitly gated to `nest_level == 0`.

**Why the gate exists, and why it can't simply be removed:** the client only has a checksum for the row(s) it actually fetched and is patching. A cascaded row (e.g. the `Customer` behind the `Order` being patched) was never fetched by this client in this exchange — there is no `S_CheckSum` to compare against. The gate isn't an oversight; it's a structural consequence of the checksum being client-supplied.

## 2. Where cascaded adjustment happens, and why it's unprotected

`LogicRow._get_parent_logic_row` ([`logic_row.py:248`](../../LogicBank/logic_bank/exec_row_logic/logic_row.py#L248)) is the single choke point every `Rule.sum`/`Rule.count` adjustment routes through to fetch the parent row being adjusted:

```python
parent_row = self.session.query(parent_class).get(parent_key)
...
parent_logic_row = LogicRow(row=parent_row, old_row=old_parent, ins_upd_dlt="*",
                             nest_level=1 + self.nest_level, ...)
```

Two things to note:
1. **Plain `Query.get()`** — no `with_for_update()`, no locking read. Under default READ COMMITTED (Postgres, MySQL, SQL Server, Oracle defaults) this is a completely unlocked read; another transaction can freely read or write the same row concurrently.
2. **`nest_level = 1 + self.nest_level`** — always ≥ 1. This is *why* `all_classes_stamping.py`'s `nest_level == 0` gate never fires for a cascaded parent: it isn't being skipped by a bug, it structurally cannot be a client-supplied checksum target.

The adjustment itself, in [`aggregate.py`](../../LogicBank/logic_bank/rule_type/aggregate.py) (shared by both `Sum` and `Count` — both subclass `Aggregate`), e.g. `adjust_from_inserted_child`:

```python
curr_value = getattr(parent_adjustor.parent_logic_row.row, self._column)
if curr_value is None:
    curr_value = 0
setattr(parent_adjustor.parent_logic_row.row, self._column, curr_value + delta)
```

This is a **Python-side read-modify-write**, not a SQL-side arithmetic expression. When the session eventually flushes, SQLAlchemy issues a blind `UPDATE customer SET balance = :computed_value WHERE id = :id` — not `SET balance = balance + :delta`. There is no `WHERE balance = :old_value` guard, no `version_id_col`, nothing that would cause the DB to reject this write if `balance` changed underneath it since it was read.

This is the same delta-adjustment mechanism documented (correctly, on its own performance terms) in `docs/training/logic_bank_api.md`'s "ADJUSTMENT ASSUMES THE STARTING VALUE IS ALREADY CORRECT" section and the project CE's "how does this perform at scale?" answer — O(1) per change instead of `SELECT SUM(...)`. That performance property and the concurrency gap below are the same mechanism, looked at from two different angles: an adjustment that trusts its Python-side starting value is fast, and an adjustment that trusts its Python-side starting value is also exactly what a concurrent writer can invalidate without either side knowing.

## 3. Concrete failure scenario — the framework's own flagship example

This isn't a theoretical edge case; it's the exact rule pair used everywhere as the canonical LogicBank demonstration:

```python
Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit)
```

Customer `ALFKI`: `balance = 900`, `credit_limit = 1000`. Two browser tabs / two API clients concurrently place an order of `80` each (each individually well under the remaining headroom):

| Time | T1 (order A, amount=80) | T2 (order B, amount=80) |
|---|---|---|
| t0 | `Query.get()` reads `balance=900` | — |
| t1 | — | `Query.get()` reads `balance=900` (T1 hasn't written yet — unlocked read) |
| t2 | computes `980`, constraint `980 <= 1000` passes, flush `UPDATE customer SET balance=980`, commit | — |
| t3 | — | computes `980` (from its own stale `900` read), constraint `980 <= 1000` **passes against stale data**, flush `UPDATE customer SET balance=980`, commit |

Final stored `balance = 980`. Correct value is `1060` — **over the credit limit**, and the constraint that exists specifically to prevent this never saw the true combined total, because it evaluated against each transaction's own private, unlocked, Python-side read. No error is raised anywhere. No `409`. No log signal beyond the normal rule-fire trace, which looks identical to two legitimate independent updates. The order that *should* have been rejected commits successfully, and the aggregate silently loses $80 of the true total on top of that.

This is a strictly different (and more serious) claim than "aborts safely" — it's silent constraint bypass plus silent aggregate corruption, both in one race.

## 4. Rule.copy — a lower-risk, different failure category

[`copy.py:execute`](../../LogicBank/logic_bank/rule_type/copy.py#L58):
```python
each_column_value = getattr(parent_logic_row.row, self._from_column)
setattr(child_logic_row.row, self._column, each_column_value)
```

This reads the parent's current value into a **newly-touched child row's own column** — there is no shared mutable counter being raced. If `Product.unit_price` changes concurrently with an `Item` insert copying it, the worst case is the child gets a slightly stale price (ordinary read-skew, the same class of thing any RDBMS transaction can exhibit) — not corruption of a value other transactions also depend on. Two different users editing the *same* child row is covered by the normal client-facing opt-lock (that child row would be `nest_level == 0` for whichever request is patching it directly). Out of scope for the fix below; noted here only to draw the boundary precisely.

## 5. Severity is DB-engine dependent

- **Postgres / MySQL (InnoDB, default REPEATABLE READ or READ COMMITTED) / SQL Server / Oracle** — all vulnerable as described. Plain `UPDATE` statements take a row lock only at write time, not at the earlier unlocked read; the Python-computed value is unaffected by that lock.
- **SQLite** — accidentally, partially mitigated. SQLite's whole-database/file-level locking (rollback-journal mode) or single-writer semantics (WAL mode) can cause a second writer to hit `SQLITE_BUSY`/snapshot conflict rather than silently succeeding, depending on exact timing and journal mode. This is **not relied upon anywhere in the code, not documented, and not something any deployment should treat as a substitute for a real fix** — most production ApiLogicServer deployments target Postgres/MySQL, where this protection doesn't exist at all.

## 6. Fix options (LogicBank engine level)

All cascaded aggregate adjustments route through the single choke point identified in §2 (`LogicRow._get_parent_logic_row`, consumed uniformly by `Sum` and `Count` via `Aggregate.adjust_parent_aggregate`), which means a fix applied there covers every `Rule.sum`/`Rule.count` in the engine without touching call sites in generated projects.

### Option A — Pessimistic: lock the aggregate root at fetch time (recommended primary)

Change the parent fetch to a locking read:
```python
parent_row = self.session.query(parent_class).with_for_update().populate_existing().get(parent_key)
```
(`populate_existing()` matters if the parent was already loaded earlier in the same request via relationship navigation — a plain re-`get()` would otherwise return the already-cached, possibly stale, Python object without re-reading the DB row.)

**Why this is the most surgical fit for the existing architecture:** it closes the race at the exact moment of risk, and — critically — it keeps the *in-memory* `row.balance` value correct for the same-transaction `Rule.constraint` check (§3's scenario). T2's `with_for_update()` read simply blocks until T1 commits, then reads the true post-T1 value (`980`), correctly computes `1060`, and the constraint correctly rejects it. No schema change, no retry loop, no change to how downstream rules read `row.<attr>`.

**Cost:** row-lock contention on hot aggregate roots (a popular `Customer`, a frequently-updated `Order`) for the duration of the transaction — this is precisely the contention the O(1) delta-adjustment design was chosen to avoid, so this is a real tradeoff, not a free fix. For most applications (aggregate roots are not typically hot-spot rows under heavy concurrent write load) this is very likely the right default; it should be validated under a realistic concurrency profile before treating it as a blanket change, not assumed from first principles.

**SQLite caveat:** `with_for_update()` is a no-op (or unsupported, dialect-dependent) under SQLite — no regression, since SQLite's own file-level locking already provides the accidental mitigation described in §5, but also no improvement there either. The real value of this fix is for Postgres/MySQL/SQL Server/Oracle deployments.

### Option B — DB-side atomic arithmetic

Replace the Python read-modify-write with a bulk-update SQL expression:
```python
self.session.query(parent_class).filter_by(**parent_key).update(
    {self._column: parent_class.__table__.c[self._column] + delta},
    synchronize_session=False)
```
This generates `UPDATE customer SET balance = balance + :delta WHERE id = :id` — atomic and correct *for the persisted value*, regardless of what any concurrent transaction is doing, with no added lock hold time beyond the UPDATE itself.

**What this does NOT fix:** the in-memory `row.balance` used by the *same-transaction* `Rule.constraint` check still reflects only this transaction's own delta on top of its own stale read — the credit-limit constraint in §3 would still pass incorrectly in-flight, even though the persisted total eventually settles at the true `1060`. Closing that requires either combining this with a post-update re-read + re-check (effectively reintroducing a lock or a retry), or accepting that constraints over aggregates are enforced against an eventually-consistent value, not a real-time-consistent one — a materially weaker correctness guarantee than what LogicBank's constraint story currently implies.

### Option C — Optimistic: `version_id_col` + retry

Add a version column to aggregate-root tables and wire SQLAlchemy's built-in `mapper_args={"version_id_col": ...}`, so **any** update — including cascaded ones — automatically gets `WHERE version_id = :old_version` and raises `StaleDataError` on conflict. Wrap the whole request/transaction in a retry loop that recomputes deltas against fresh state on conflict.

This is the closest match to Val's original hypothesis ("may abort, but safe if it succeeds") — it converts the silent corruption into a detectable, retryable abort. But it's the most invasive option: a schema change on every table that's ever an aggregate root, plus a generic retry wrapper that has to be threaded through the request lifecycle (not just the rules engine), plus retry-storm risk on genuinely hot rows under sustained contention.

### Option D — Optimistic: column-scoped compare-and-swap at flush (documented for completeness — not being built, see Recommendation)

A refinement of B and C, prompted by Val: instead of a blind arithmetic `UPDATE` (B) or a whole-row version column (C), guard the write with the *specific column's* read-time value, checked atomically by the UPDATE itself:

```sql
UPDATE customer SET balance = :new_value WHERE id = :id AND balance = :curr_value_read_earlier
```

`curr_value_read_earlier` is exactly the value `aggregate.py` already reads into `curr_value` before computing `curr_value + delta` — no new read, just carry it through to the write. Check `rowcount`: `0` means another transaction wrote `balance` between this read and this write — a real conflict, detected atomically (the compare and the write are one statement; there's no separate re-check step that could itself race).

**⚠️ The tax — spelled out explicitly, because it's easy to under-read from a one-line summary.** "D only costs something when there's a collision" sounds like a rare, contained cost. It is not. The tax is architectural and permanent, paid by every deployment that enables this mode, whether or not a collision ever occurs:

- **Every caller of every endpoint that can trigger a `Rule.sum`/`Rule.count` cascade is now exposed to a new failure mode it did not have before** — not just power users doing high-concurrency writes. A client PATCHing `Order` has no visible reason to expect a failure tied to `Customer`; it never touched `Customer`. The coupling is invisible from the caller's side of the API contract.
- **This is not a tax the caller can decline.** Client-facing opt-locking (§1) is at least *legible*: the client sent a checksum for a row it fetched, and a `409` on that row is self-explanatory. A conflict surfaced from D is a `409` on a row the caller never fetched and may not know exists in the schema at all.
- **It will very likely pass all pre-production testing and then appear for the first time under real concurrent load in production.** Almost all manual/QA testing is single-user. The failure mode requires two genuinely concurrent writers hitting the same aggregate root within the same narrow window — a condition dev/QA environments rarely produce by accident. So the tax is *hidden* precisely when someone is deciding whether their client needs retry handling, and only *charged* after the client is already built and deployed without it.
- **Concretely, without retry handling built in, D does not actually deliver "safe if it succeeds, and it eventually succeeds."** It delivers: business operations that should succeed intermittently fail, for reasons invisible to the end user, correlated with load rather than with anything the user did — which reads to that user as the product being flaky, not as a concurrency-safety feature working as designed.

**Why this is sharper than C:** it's column-scoped, not row-scoped. Two rules adjusting *different* independent columns on the same parent in the same window (`Customer.balance` via one Sum, `Customer.order_count` via an unrelated Count) don't spuriously conflict each other the way a single row-level `version_id_col` would — only a genuine second writer to the *same* column trips it.

**The catch — detection timing vs. correctness timing.** `Rule.constraint` (the credit-limit check) evaluates against the in-memory Python value during Row Logic, *before* flush. A flush-time compare-and-swap only discovers the read was stale *after* the constraint already ran and already passed against the stale value — detecting the conflict doesn't retroactively fix that verdict. Closing §3's scenario fully (not just protecting the persisted number) requires the conflict to abort the transaction and force a genuinely fresh Row Logic pass, not just a retried SQL statement.

**The simplification that makes this cheap, not just correct:** that "abort and force a fresh pass" does **not** require building a new automatic retry loop inside LogicBank or ApiLogicServer — it can piggyback on the retry-on-409 handling a client already needs for the `nest_level == 0` case. But getting there needs a change on **both** sides of the LB/ApiLogicServer boundary, not one:

- **LB side (`aggregate.py`, same method as Option A):** on `rowcount == 0`, raise a new, generic, framework-agnostic exception — e.g. `LBOptimisticLockException(SystemError)`, sibling to the existing `ConstraintException` in `logic_bank/util.py`. LB must **not** raise `ALSError` directly: `ALSError` subclasses `safrs.errors.JsonapiError` ([opt_locking.py:138](../api_logic_server_cli/prototypes/base/api/system/opt_locking/opt_locking.py#L138)), and LB has no dependency on SAFRS/Flask anywhere else — that boundary is exactly why `all_classes_stamping.py` supports `APILOGICPROJECT_NO_FLASK` (LB rules must also run standalone, e.g. test-data loading). Importing a SAFRS exception into `aggregate.py` would break that.
- **ApiLogicServer-src side (new, small):** catch the new LB exception where opt-locking already lives and re-raise it as `ALSError`, to get the polished `409` with precise status code and message.

**This second step doesn't exist for `ConstraintException` today either — worth flagging as a related, pre-existing gap.** I checked how a plain `ConstraintException` (already a bare `SystemError`, same framework-agnostic pattern proposed above) actually surfaces now: SAFRS's request handler (`safrs_api.py`) has a precise `except JsonapiError as exc:` path — the one `ALSError` is designed for — and a generic fallback `except Exception as exc:` for everything else, including `ConstraintException`. So a constraint violation today does **not** get the same polished treatment as an opt-lock conflict; it falls into SAFRS's generic handling. Adding the catch-and-translate step for the new optimistic-lock exception would fix that for this new error, but wouldn't retroactively fix `ConstraintException`'s existing generic handling — a separate, smaller cleanup Val may want to fold in at the same time rather than leave as an inconsistency between two conceptually similar "the transaction was correctly rejected" errors.

**Cost model, contrasted with A:** A pays a small tax on *every* adjustment (row lock held for the transaction's duration, even when nothing else touches the row) in exchange for *never* surfacing a user-visible failure due to contention — a concurrent request just waits. D pays *nothing* on the non-colliding path (no lock ever acquired) but a genuine collision surfaces as a failed request the client must retry — same UX shape as today's client-facing opt-lock 409 once the catch-and-translate step above exists, extended to a case (cascaded aggregate root) the client didn't directly touch, which may read as a confusing error ("why did my Order fail — I didn't change the Customer") unless the error message is adjusted to name the actual conflicted table/column rather than reusing the generic client-facing wording verbatim.

### Option F — Hybrid: optimistic write + bounded server-side retry of the whole Row Logic pass (documented for completeness — not being built)

Theoretically the best of A and D: D's cheap, non-blocking compare-and-swap write at the SQL level, but instead of raising the conflict all the way out to the API caller, catch it internally and retry — invisibly to the caller in the common case.

**Mechanism:**
1. Same column-scoped compare-and-swap as Option D (`UPDATE ... SET balance = :new WHERE id = :id AND balance = :curr_value_read_earlier`).
2. On `rowcount == 0`, instead of propagating D's new exception to the caller, catch it and re-run the **entire Row Logic pass** for the original triggering event from a fresh read — not a retried SQL statement, a re-entry into LogicBank so `Rule.constraint` re-evaluates against real, current data (a stale-value retry of just the SQL write would leave the same wrong-verdict problem Option D has, per §6's "detection timing vs. correctness timing" note).
3. Bounded attempts (e.g. 3) with backoff. Only after exhausting them does it fall back to D's behavior — raise to the caller. So F degrades to D under sustained contention, and to a fast happy path under light/no contention.

**Where the retry boundary has to live — not where it looks like it should.** It cannot live inside `aggregate.py`/`_get_parent_logic_row` (where A and D's changes live) — by the time a conflict is detected there, the SQLAlchemy session may already have other rows dirtied mid-cascade; there's no clean way to "start over" from inside one adjustor call without discarding the whole session. The retry has to wrap the request handler itself — around wherever `session.commit()` is ultimately called (SAFRS's commit path / the Flask request lifecycle in `api_logic_server_run.py`) — catch the conflict there, roll back the entire session, obtain a fresh transaction, and **replay the original inbound request payload** (the JSON:API PATCH/POST body) against fresh reads. That's a materially bigger ApiLogicServer-src change than D's catch-and-translate step: it needs safe request replay at the SAFRS layer, not just an exception mapping.

**A real, unresolved correctness hazard this option introduces that neither A nor D has:** side-effect idempotency across a retried pass. `Rule.after_flush_row_event` (Kafka publish, email send, external API call — Phase 3c, per `docs/training/logic_bank_api.md`'s 3-phase model) fires after a successful flush. If Phase 3c already fired for part of a cascade in an earlier flush *within the same overall transaction attempt*, and a *later* flush in that same attempt then hits a conflict forcing a full retry-from-scratch, the retry's fresh pass could fire that same `after_flush_row_event` again — a genuine double-Kafka-message / double-email risk. A DB rollback undoes the database writes; it does not un-send a Kafka message already published to an external broker. **I have not traced exactly how many times `after_flush` can fire per logical transaction in this engine** (whether LogicBank's cascade processing can trigger more than one flush before final commit) — that has to be confirmed against actual LB flush-cycle behavior before Option F could be built safely. Flagging this as an open unknown, not asserting a fix.

**Contention behavior is not strictly better than A, either.** Under *sustained* heavy contention on the same row (not just occasional collision), A serializes cleanly through the DB's own lock queue — each waiter proceeds in turn. F's competing retries can all fail against each other repeatedly (a retry storm), each round doing real work that gets discarded — worse throughput than A's simple queueing under genuinely hot rows, even though F is cheaper than A on the *uncontended* path. "Hybrid" doesn't mean "dominates A in every regime."

**Why not recommended for v1:** it's the most expensive option to build correctly (LB change reusing D's compare-and-swap, *plus* a request-replay-capable retry wrapper at the ApiLogicServer/SAFRS layer, *plus* resolving the Phase-3c idempotency hazard above before it's safe to ship) — for a benefit (marginally less lock hold time than A under light/moderate contention) that hasn't been shown to matter yet, since no concurrency benchmark has been run against any option. Worth prototyping later specifically if a benchmark shows A's blocking cost is a real problem for some deployment and D's client-visible-failure UX is unacceptable for that same deployment — the narrow intersection where neither simpler option is good enough.

### Option E — config-driven switch between IGNORED (today) and PESSIMISTIC (A only)

Not a fourth technical mechanism — a delivery decision, following a precedent already in this codebase. `config.py` already governs the client-facing check via an enum + env var:

```python
class OptLocking(ExtendedEnum):
    IGNORED = "ignored"
    OPTIONAL = "optional"
    REQUIRED = "required"
```
(`OPT_LOCKING` env var, read once into `Args.opt_locking`.) A new, parallel setting — `TRANS_UPDATE_LOCKING` with values `ignored` / `pessimistic` — is the same shape in the same file, not a new mechanism. Deliberately not named `CASCADE_OPT_LOCKING` or any `*_OPT_LOCKING` variant — that family reads as "another flavor of the client-facing check" when this is the opposite: an engine-internal, transaction-scoped lock the client never sees or configures. `TRANS_` signals transaction-internal; `UPDATE_` names the moment (LogicBank's own cascaded parent updates mid-transaction, not the client's original write).

**Scoped down from the original 3-way proposal to 2 values, per the Recommendation below: `optimistic` (Option D) is documented above but not being built.** No `optimistic` value ships until a specific customer produces a measured need for it — see Recommendation.

Plumbing into LB: `LogicBank.activate()` already takes extensible mode kwargs (`aggregate_defaults`, `all_defaults`) alongside `session`/`activator`/`constraint_event` — a `trans_update_locking=` kwarg fits directly. `RuleBank` (`rule_bank/rule_bank.py`) is already a singleton LB uses for engine-wide state; `activate()` stashing the mode there, and `aggregate.py`'s `adjust_from_*` methods branching on it before each adjustment, needs no new plumbing concept:
- `ignored` → today's plain `setattr` (§2, current behavior, unchanged)
- `pessimistic` → Option A's `with_for_update()`

**If `TRANS_UPDATE_LOCKING` is unset (not present in the environment at all), behavior is `ignored`** — same fallback convention `OPT_LOCKING` already uses (`os.getenv('OPT_LOCKING')` only overrides when actually set; otherwise the Python-side default in `config.py` stands). Default `ignored` preserves today's behavior and performance for every existing deployment that doesn't opt in — no surprise regression on upgrade.

**`default.env` placement:** unlike `OPT_LOCKING` (which has no line at all in `prototypes/base/config/default.env` — its default lives silently in `config.py` only), `TRANS_UPDATE_LOCKING` should get an explicit, *uncommented* line in `default.env` stating the active default outright — not a commented-out placeholder like `AGGREGATE_DEFAULTS`/`ALL_DEFAULTS` (lines 7–8 of that file), since commented-out reads as "an option you could enable" whereas this should read as "this is the behavior in effect right now" for a setting that changes locking/failure behavior:
```
# TRANS_UPDATE_LOCKING controls locking for LogicBank's own cascaded aggregate adjustments
# (Rule.sum/Rule.count parent updates) during a transaction - distinct from OPT_LOCKING above,
# which only covers the client's own PATCH. See internal_dev/locking_strategy.md.
# ignored (default): today's behavior, no locking
# pessimistic: locks the aggregate root row for the transaction duration (with_for_update)
TRANS_UPDATE_LOCKING = ignored
```
This is a deliberate departure from `OPT_LOCKING`'s own precedent, not an oversight — a project author should be able to discover this knob by opening `default.env`, not only by reading `config.py` source.

### Recommendation

**Build `ignored` and `pessimistic` (Option A) only. Do not build `optimistic` (Option D) or `optimistic`+retry (Option F) in v1 — not even as an opt-in.**

This is a correction from an earlier draft of this doc, which proposed D as a "narrow opt-in for advanced use cases." Pushed on directly: that framing understated D's tax (see the callout in §6 Option D) and overstated how likely this framework's actual usage is to need it. Two things have to both be true to justify building D at all: (1) A's blocking cost is a real, measured bottleneck for some deployment, and (2) that deployment specifically prefers D's tax (permanent exposure to a new caller-visible failure mode, on every caller, forever) over that blocking cost. Neither has been shown — no concurrency benchmark has been run against any option, and this framework's demonstrated use cases (Customer/Order credit checks, department/charge/GL allocation, customs classification) are moderate-volume line-of-business transactions, not the internet-scale hot-counter workloads (flash-sale inventory, real-time leaderboards) where A's per-adjustment lock hold time would plausibly matter. Building D speculatively, against a need that hasn't materialized, is exactly the kind of premature complexity worth refusing — it also isn't free: the new LB exception, the ApiLogicServer-src catch-and-translate step, the reworked error message, and the CE/training-doc guidance callers would need to actually implement retry correctly are all real, non-trivial engineering and documentation cost (see the Appendix for the fuller breakdown), paid up front for a benefit that's currently hypothetical.

A's failure mode is latency: bounded, measurable, degrades gracefully, and requires nothing from the API caller — it protects every deployment automatically, without anyone needing to know this problem exists. That fits the product's own "correct by construction" claim directly: a silent, unsurfaced constraint bypass under load (§3) is exactly the kind of finding that would undermine it, and A closes it unconditionally.

**Does the recommendation depend on target market? No — it doesn't change which option to build, only how urgently:**
- **Enterprise/regulated** (the FedEx-class audience already referenced elsewhere in this repo's internal docs) — correctness and auditability outrank throughput; "occasionally blocks under load" is trivial to explain to a reviewer, "can silently violate a declared constraint under a specific interleaving" is not. A is the only real candidate.
- **Self-serve / rapid-prototyping** — the intuitive guess is D wins here on "move fast," but it's the opposite: this audience is *least* likely to have hand-built correct retry handling in a generated client, so D's tax lands hardest here, not lightest. A protects them without asking them to think about it.

If a specific customer later produces a measured case where A's blocking is a real bottleneck on a specific hot row, build D (or F) then, informed by that customer's actual profile — that will produce a better-fitted design than one built speculatively now, and by then there's a real cost/benefit to weigh instead of a hypothetical one.

**SQLite makes the choice moot regardless.** `with_for_update()` is a no-op under SQLite, so A gives zero improvement there over today's `ignored` state — this includes `basic_demo` and most sample/tutorial projects. Whichever default ships, SQLite deployments remain on the accidental file-locking behavior in §5, unchanged. State this plainly wherever the setting is documented, so nobody assumes flipping the env var protects a SQLite-backed project.

**Noted for the record, not recommended now:** Option F (above) is the theoretically better long-term answer — D's cheap write with A's "caller never sees a failure" property — but it's the most expensive to build correctly and introduces a real, unresolved side-effect-idempotency hazard under retry that A and D don't have. Worth prototyping later only if a benchmark shows A's blocking cost is a real problem *and* D's client-visible failure is unacceptable for the same deployment — not a day-one pick.

**Before shipping any of this:** write a concurrency regression test reproducing §3's scenario directly (two threads/sessions racing a shared `Customer.balance` against a `credit_limit` constraint) against at least Postgres (the common production target) — confirm the race exists today, then confirm Option A (as default) closes it. `LogicBank`'s existing `examples/multi_relns/` suite (Jun 2026 multi-relationship fix) is a reasonable model for how to structure a new `examples/concurrent_adjust/` fixture for this.

## 7. Open questions for Val

- Confirm `ignored` as the shipped default (preserves current behavior on upgrade) with `pessimistic` as the recommended opt-in, per the Recommendation above — or does Val want `pessimistic` as the out-of-the-box default for new projects, accepting the small risk of surprising an existing low-contention deployment that upgrades LB and inherits new blocking behavior?
- Does this warrant a LogicBank release note / migration guide entry, given `TRANS_UPDATE_LOCKING` changes locking or failure behavior for every existing `Rule.sum`/`Rule.count` once a project opts in?
- Should the opt-locking training doc (`docs/training/logic_bank_api.md`) get a short callout that same-transaction constraint checks over aggregates are only as safe as `TRANS_UPDATE_LOCKING`'s setting — so a project author reading the credit-limit example doesn't assume a same-transaction guarantee the engine doesn't provide under the default `ignored` setting?
- Option F's Phase-3c idempotency hazard (side-effecting events potentially double-firing across a retried pass) needs tracing against LB's actual flush-cycle behavior before F is even a safe option to prototype, independent of whether F is ever built — worth a dedicated investigation if F is ever revisited.

## Appendix A: Cost/Risk Assessment — Option A vs. Option D

Requested directly, since the Recommendation above rests on this comparison. D is scoped out of v1, but the comparison is worth having on record precisely, not just asserted.

### Option A (pessimistic `with_for_update()`)

| Dimension | Assessment |
|---|---|
| **Footprint** | One repo (LogicBank), one method (`LogicRow._get_parent_logic_row`). No schema change, no new exception type, no ApiLogicServer-src change beyond wiring the config value through. |
| **Mechanism risk** | Low. `with_for_update()` is a first-class, long-established SQLAlchemy/Query feature — not a novel or experimental technique. The write path itself (ORM `setattr` → normal flush) is completely unchanged; only the *read* becomes a locking read. |
| **Correctness confirmed by inspection?** | Yes, for the single-aggregate-root case in §3 — the constraint re-evaluates against a lock-guaranteed-current value. |

**Real risks, not hand-waved:**
- **Deadlock potential in multi-root cascades.** If a single transaction's cascade acquires locks on two or more different aggregate roots (e.g. an event that adjusts both `Customer.balance` and a `Department.total_something`), and a *concurrent* transaction's cascade acquires the same two roots in the *opposite* order, classic lock-ordering deadlock results. Most RDBMSs detect this and abort one participant automatically — which means A is not literally "never fails visibly" in every scenario, only in the common single-root-adjustment case verified in §3. **Not yet verified:** whether LogicBank's cascade processing visits parent roots in a consistent, deterministic order across different triggering paths. This needs to be checked before claiming A is deadlock-free in general, not just in the flagship example.
- **Lock hold duration extends to the rest of the transaction, not just the adjustment.** The lock is acquired at first parent-fetch and held until the *whole* transaction commits — including any slower work that happens afterward in the same request (further cascades, other constraint checks, a Request Pattern AI call if one happens to run inside the same transaction). A transaction that's slow for reasons unrelated to the lock itself will hold that lock for its entire remaining duration. This means the real-world cost of A depends on the *slowest* thing in the transaction, not just the adjustment step — worth measuring against a realistic transaction, not a synthetic one.
- **Operational/perception risk on activation.** Turning this on for an existing deployment converts an invisible correctness bug into visible latency for the first time. An unprepared ops team could read new blocking/timeouts under load as "the framework got slower" rather than "the framework started paying a cost the bug was previously hiding." Worth a clear release note framing this explicitly as trading a correctness bug for a measurable, bounded latency cost — not a performance regression.
- **Zero effect on SQLite** (no-op dialect behavior) — not a risk, but a coverage gap: activating this setting on a SQLite-backed project changes nothing, silently.

**Net:** Val's guess is right — A is focused and low implementation risk. It is not zero-risk: the multi-root deadlock question is a real unknown requiring verification, and the "cost is bounded to the adjustment" intuition is only true if nothing slow happens later in the same transaction.

### Option D (optimistic column-scoped compare-and-swap)

| Dimension | Assessment |
|---|---|
| **Footprint** | Two repos. LogicBank: new exception class + rewritten write path in `aggregate.py`. ApiLogicServer-src: new catch-and-translate step. Plus real, non-code cost: error-message design work, and CE/training-doc guidance so generated clients actually implement retry (§6's tax callout) — without that guidance, the protection is unlikely to be exercised by real callers at all. |
| **Mechanism risk** | Materially higher than A. |

**Real risks, not hand-waved:**
- **The write mechanism itself has to change, and that interacts with the ORM's own bookkeeping.** A leaves the normal ORM `setattr` → flush path completely alone. D replaces it with a raw guarded `UPDATE` for the adjusted column. But LogicBank's downstream rules still need to read the *correct new value* off the Python object in the same transaction (for further cascades/constraints) — so the Python attribute also has to be set. If it's set via normal `setattr`, SQLAlchemy's own dirty-tracking will schedule *its own* unguarded `UPDATE` for that column at the next flush, silently defeating the guard the whole option exists to add. Avoiding this needs careful handling (e.g. expiring/refreshing the attribute after the guarded raw write, or excluding the column from the ORM's normal dirty-flush for that instance) — real, non-obvious implementation complexity A does not have at all.
- **Numeric precision — a risk this exact codebase has already been bitten by once.** The guard compares `WHERE balance = :curr_value_read_earlier`. If `balance` is `Decimal`/`Numeric` and the Python-side value read via the ORM doesn't round-trip byte-identically into the bound parameter compared against the DB's stored representation, the guard can false-negative (spurious conflict) or, worse, false-positive (miss a real conflict). This is the *same class* of bug already found and fixed once in this codebase — see `dev-architecture.md`'s "Optimistic Locking — Decimal/float checksum mismatch" entry (Jul 2026), where `Decimal('300')` vs `300.0` hashed differently despite being equal. That fix was for the Python-side checksum comparison specifically; D's raw SQL comparison is evaluated DB-side with native numeric equality, which is plausibly *more* robust than the Python `repr()`-based checksum — but this needs explicit verification against the actual numeric type mapping in use, not an assumption either way, given the precedent.
- **Multiple aggregates on the same parent in one transaction.** A transaction adjusting both `Customer.balance` (Sum) and `Customer.order_count` (Count) needs two independent per-column guarded UPDATEs, not one. This composes correctly under normal DB transaction atomicity (any raised conflict rolls back the whole transaction, so there's no partial-application hazard) — flagged here because it looked like a risk on first pass and is worth recording as *checked, not a problem*, rather than leaving it as an open question.
- **The protection may go unexercised in practice** — not a code risk, a product risk, but a real one: if callers aren't built with retry handling (§6's tax), D's nominal safety guarantee is not actually delivered in the field, while still having been paid for in engineering effort.

**Net:** Val's implicit comparison holds — D is not "a bit more expensive," it's categorically riskier: it changes the write mechanism itself (interacting with ORM internals A never touches), reintroduces a numeric-precision risk class already seen once in this codebase, and its safety guarantee is conditional on caller behavior the framework doesn't control. A's risks are narrower and more thoroughly boundable (verify cascade lock ordering, measure transaction duration); D's risks are more numerous and some are inherently outside the framework's control even after the code is correct.

## Appendix B: Same Hole, One Layer Down — Why LogicBank Closes This, Not SQLAlchemy

SQLAlchemy isn't missing a feature — `with_for_update()` and `version_id_col` both exist and both work. What it's missing is a way to know *where* those features need to be applied: it has no concept of "this column is a derived aggregate, adjusted by exactly this code path," because that's a domain concept LogicBank owns, not something an ORM can infer.

The two primitives sit on opposite sides of a real reliability line, though:
- **`version_id_col`** is declared once, at the mapper, and SQLAlchemy applies its guard to *every* UPDATE of that class automatically, forever. Nothing to miss.
- **`with_for_update()`** is a per-query decision with zero structural enforcement. If a codebase has several places that read-then-write the same aggregate column, each needs its own explicit `.with_for_update()`. Add a sixth call site later — a new custom endpoint, a bug fix — and forget it, and SQLAlchemy gives no warning. The vulnerability returns silently.

That's not a hypothetical failure mode; it's structurally the same one that motivates declarative rules over procedural code in the first place. Procedural business logic requires a developer to remember to invoke the right logic at every relevant path, and breaks silently the moment someone adds a new path without matching treatment. `Rule.sum` fixes that by being declared once and enforced on every path by the engine. `with_for_update()`-by-convention has exactly the weakness `Rule.sum` was invented to eliminate, one layer down — at the concurrency-control level instead of the business-logic level.

Which is why the fix belongs inside LogicBank, not as guidance for project authors to remember `with_for_update()` in their own code — that would just relocate SQLAlchemy's hole into the project layer. Putting it once inside `LogicRow._get_parent_logic_row` — the one method every `Rule.sum`/`Rule.count` adjustment is structurally guaranteed to pass through — converts a discipline that decays over time into a completeness guarantee, the same way the rules engine itself does for business logic.

**The boundary is consistent, not a new gap:** hand-written procedural code inside a project that bypasses LogicBank rules entirely (a custom API endpoint doing a raw `session.execute(update(...))` against an aggregate column) isn't covered by this fix — but it was never covered by the rules engine's correctness guarantees either. Same shape of limitation, same reason.
