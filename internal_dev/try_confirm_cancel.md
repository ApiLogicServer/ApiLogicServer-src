# Try / Confirm / Cancel (TCC) and the Ready-Flag Pattern

Status: design discussion, Nov 4 2026. Nothing implemented. Companion to
`muti_constraint_what_if.md` (what-if is a Try with no reservation; TCC makes it a reservation).

## The pattern

From distributed transactions (Pat Helland, "Life Beyond Distributed Transactions": tentative
operations; formalized for microservices, e.g. Seata, Alibaba payments). Each participant offers:

- **Try**: reserve resources tentatively (a hold, not a commit); return a token, usually with an expiry.
- **Confirm(token)**: make the reservation real. Idempotent; should nearly always succeed, because
  Try already validated.
- **Cancel(token)**: release the reservation. Idempotent; must tolerate arriving before Try, or
  with no Try.

Versus a saga: a saga commits each step and compensates afterward, so intermediate states are
visible. TCC keeps intermediate state in a reserved form that other transactions already account for.

## Why it matters for agents

What-if is a *prediction*, not a reservation: by commit time the answer can be stale. An agentic
flow has a human-approval pause between plan and commit, which is exactly the window TCC exists for.
Try holds the resources, the user approves, Confirm commits.

## The ready-flag pattern (what we already have)

`nw_sample` (see `samples/nw_sample/review.md`, "Origin Story: Min-Cardinality Constraints and
Why `Ready` Exists"):

- `Order.Ready` is a plain boolean, set by the user. It gates *inclusion in aggregates*:
  `Customer.Balance = sum(Order.AmountTotal where ShippedDate is None and Ready == True)`
  (`declare_logic.py:110-112`). An unready order exists, but the credit check does not see it.
- It gates *completeness checks to an explicit transition*: `do_not_ship_empty_orders`
  (`declare_logic.py:187-195`) fires when the user marks an order Ready or ships it, not at insert.
  By then `OrderDetailCount` (a `Rule.count`) is trustworthy.
- It is defaulted explicitly (`order_defaults`, `declare_logic.py:216-222`), since `None` silently
  breaks `== True` / `== False` in `where=` and constraints.

So the flag is already a draft state: the row is real and stored, but its effects are held back
until the transition.

## Rich Dankoellner's use: staged migration of a large system

Rich uses the same idea to migrate a LARGE system. Rows that have been *tried* carry a flag.
While flagged, the rows do not trigger various side-effects (the ready-flag pattern). When all
goes well, the flag is cleared (Confirm). Mapping to TCC:

| TCC | Rich's migration |
|---|---|
| Try | insert/transform rows with the flag set; rules run, validation happens, side-effects held back |
| Confirm | clear the flag; the transition releases the held effects |
| Cancel | remove the flagged rows (or never clear the flag) |
| Token | the flag itself, or a batch id on the flagged rows |

Note the polarity: in `nw_sample`, `Ready = True` means *counted*; in Rich's use the flag is a
*tried* marker, set means *held*, cleared means *live*. Same mechanism, inverted sense. Name it
for whichever reads naturally in the domain.

### Two variants (which rules see the flagged rows is the design choice)

1. **Excluded variant (nw_sample style).** Aggregates and events carry `where=not flagged`.
   Cancel is trivial (nothing was counted, nothing to unwind). Confirm does the work: every row's
   transition fires its cascade. For a large migration, Confirm cost is one engine run per row.
2. **Included variant (reservation style).** Flagged rows count in aggregates, so constraints see
   the hold and a second transaction cannot oversubscribe (credit, stock). Confirm is cheap (flag
   only; sums unchanged). Cancel does the work, and every aggregate unwinds by its delta with no
   unwind code. Side-effects (Kafka, email) fire on the transition to confirmed, using the usual
   guard (`old_row is None or changed`), not at Try.

Which one Rich uses is not stated here. Reservation semantics (agents, concurrent users) want the
included variant; bulk load with a verify-then-release step fits the excluded one.

## Rules make the hard part nearly free

The usual TCC difficulty is reservation accounting and clean unwind. With declarative rules,
the aggregates adjust by delta on flag change, insert and delete, so Confirm and Cancel are plain
updates and deletes. The only code is the transition guard for side-effects.

## Caveats

- **Expiry is the absence-of-event problem.** A Try never confirmed or cancelled writes nothing,
  so no rule fires. Timeout-cancel needs a companion sweeper (see "Absence of an Event" in
  `docs/training/logic_bank_api.md`, option (a)): a scheduled job or agent.
- **Operation-name vocabulary.** Versata's per-call operation name could grow from
  `commit`/`whatif` to include `try`. Confirm and Cancel stay plain status updates.
- **Flag defaults.** Default the flag explicitly (never `None`), as `order_defaults` does.
- **Large batches.** Confirm of N rows is N engine runs in the excluded variant; consider batch
  size and commit boundaries for LARGE migrations.

## Open questions (to confirm with Rich)

- Does his flag suppress aggregation, events, or both (excluded vs included variant)?
- Is Cancel a delete, or does the flag stay set indefinitely?
- Is there a batch id, or is the flag alone the marker?
