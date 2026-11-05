# Multi-Constraints and What-If for Agents (MCP)

Status: design discussion, Nov 4 2026. Nothing implemented.

## Why

General-purpose agents act on systems of record. The weak spot is acting without corrupting
state. MCP gives agents the way in; rules make it safe (constraints and derivations run at
commit, on every path). Two capabilities would make that safety *useful* to an agent, not just
protective: **what-if** (plan before commit) and **multi-constraints** (see all errors at once).
Both were built at Versata.

## What-if

**Versata precedent:** an *operation name* (just a name, no args) passed as a per-call option on
updates, in the API. Nothing on the session. Side-effect handling is not remembered (likely
messaging was deferred to commit, so rollback dropped it).

**Proposed here**
- **API:** per-call `meta.operation = "whatif"` in the JSON:API request body (survives proxies,
  logged with the payload). Default is commit.
- **Engine:** LogicBank hooks SQLAlchemy commit events, so it never sees call arguments. A
  per-request carrier (`session.info`, session is per-request in SAFRS) moves the value from the
  handler to the hooks. Internal detail, not exposed as session API. Behavior: flush, then roll back.
- **MCP:** a separate generic `what_if` tool taking a *batch* of JSON:API operations (real
  scenarios are multi-row), not a `dry_run` flag on each write tool. Reasons:
  - `readOnlyHint` lets hosts auto-approve it; a flag on a write tool gets the write approval gate.
  - It cannot commit by construction, so the read-only promise is enforceable.
  - Commit tool takes the same payload and same engine, so what-if and real results agree.

**How the MCP executor knows the mode:** it holds none. Mode going in = which tool was chosen.
Mode coming back = every response carries `meta: {operation: "whatif", committed: false}`, and the
tool description says "simulates through the rules and rolls back; nothing saved or sent."
Executor flow: what_if, show diff to user, on approval replay the same payload to the commit tool
(the payload is the only state). Do not chain on hypotheticals (e.g. IDs from a what-if result).

**Response contents and difficulty**

| Piece | Source | Difficulty |
|---|---|---|
| Before/after diff | session state, `old_row` vs `row` for cascade rows, read before rollback | Easy |
| Violations | see multi-constraints below | Needs engine change |
| Suppressed messages | publish guard records what it skipped | Easy |
| Rule trace | the log today | Not trivial |

**Trace caveat:** the rule trace is `als.log`, a single global debug stream. The Behave/traceability
reports work only because tests run sequentially. Concurrent agent calls interleave. Options:
(a) best-effort now: per-call log handler filtered by thread/contextvar, text, labeled debug;
(b) right answer: LogicBank appends a structured record per firing (rule, row, attr, old to new)
to a per-transaction list; the log becomes one consumer. Also a cleaner source for Behave reports.

**Side effects (this stack only):** `after_flush_row_event` runs *before* commit, so Kafka
publishes, emails and AI calls escape a rollback. Fix: one central guard in
`publish_kafka_message` and Request Pattern handlers that checks the operation and records the
skip. Cleaner end state: defer publishes to a post-commit hook (also fixes the latent
published-then-commit-failed bug), but it changes `after_flush_row_event` semantics for existing
projects. Guard is the smaller change.

**Other caveats:** autoincrement IDs and timestamps are not stable between what-if and commit;
what-if is a prediction, not a reservation (optimistic locking still rejects a stale commit);
what-if needs its own session. Probabilistic (AI) rules in what-if are a policy choice: call the
model, or return a simulated/last value.

## Multi-constraints (Versata feature)

A constraint flagged "keep going, fail when I get to commit": a violation is recorded and
processing continues; at commit all collected violations are raised together, so a UI (or agent)
gets a list of errors to fix.

**Why it is sound:** continuing past a failed *derivation* would leave later rules reading values
never computed. A constraint derives nothing, it only reads, so skipping the raise changes no
state. Collecting is safe for constraints specifically.

**Sketch**
- `Rule.constraint(..., multi=True)` (name TBD; consider the same option on `commit_constraint`).
- Failure appends `{rule, row, message, error_attributes}` to the per-transaction list and continues.
- At commit, if non-empty, raise once with all of them. JSON:API already has an `errors` array.
  `error_attributes` already exists for field highlighting.
- Unflagged constraints stay fail-fast (no change for existing projects).
- Exceptions *inside* a constraint function still raise immediately (bugs, not violations).

**Two uses:** (1) normal commit: an agent gets all N violations in one rejection and repairs in
one round trip (self-correcting rejection), same for the Admin UI; (2) what-if: since collecting is
safe for any constraint, what-if mode treats every constraint as multi, so the full list comes free.

**Caveat:** a list does not show relationships (fixing A may clear B). Small cost versus one at a time.

## Backlog order

1. Multi-constraint flag + per-transaction collector (smallest; needed for what-if and for
   better rejections).
2. What-if v1: `meta.operation`, rollback, diff from session state, violations, suppressed-message
   guard, best-effort thread-scoped trace, `what_if` MCP tool with `readOnlyHint`.
3. Structured per-firing trace in LogicBank (replaces log scraping; helps Behave reports).
4. Optional: post-commit deferral of publishes.

Not yet checked: `integration/mcp/mcp_client_executor.py` dispatch (where plan-then-confirm fits).
