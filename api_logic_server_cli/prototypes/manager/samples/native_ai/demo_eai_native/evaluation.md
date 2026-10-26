# Evaluation: demo_eai_native (plain Python) vs demo_eai_docker (GenAI-Logic)

Same requirements (`samples/requirements/demo_eai/docs/requirements/demo_eai`), same database (`basic_demo.sqlite`), same containers (Keycloak realm `kcals`, Kafka `broker1`), both FULL runs. Sources: `demo_eai_native/docs/requirements/project_summary.md` and `demo_eai_native/docs/requirements/demo_eai_native/transcript.md`; `demo_eai_docker/docs/requirements/` (ad-libs, traceability report, transcript) and its code.

**Read this first: the two runs are not like for like.** The native script is smaller by design (no Admin App, no diagrams, no traceability report, no "tests from rules"), and the two test suites were written independently. Numbers are indicative, not a benchmark.

## At a glance

| | demo_eai_native | demo_eai_docker |
|---|---|---|
| Stack | Flask, SQLAlchemy, confluent-kafka, behave | GenAI-Logic project (LogicBank rules, JSON:API, Admin App) |
| Mode | FULL (Keycloak, live Kafka) | FULL (Keycloak, live Kafka) |
| Elapsed | 4 min 45 s (11:33:41 to 11:38:26), timed per step | Not timed per step. Its transcript shows a final turn of 9 min 11 s, so the whole build took at least that |
| Test scenarios | 5 passed, 0 failed, 0 skipped (25 steps) | 15 passed, 0 failed (the last report; a rerun on 24 Oct passed 12 of 12) |
| Requirements covered | 5 of 5 | 5 of 5 |
| Code the AI wrote (non-blank, non-comment) | 383 lines in `app/`, plus 72 in `scripts/verify_kafka.py` | About 320 lines across logic, API, Kafka and security files (wc of the files; the mapper and generated templates not counted) |
| Credit logic only | `app/logic.py`: 98 lines (shared with the shipping publish) | `check_credit.py`: 21 lines, 5 declarative rules |
| Traceability | `project_summary.md` (hand-written table) | Generated report: requirement, rules, tests, last result |
| Judgment calls | 13 items, all in one flat list | 3 flagged 🔴 for review, 6 🟡 FYI |
| Error loops | 2 inside the live-Kafka step, about 55 s | 2 loops, about 5 min (replayed topics; cold-start timeout) |

## What each side got right

**Native**
- It finished fast: under 5 minutes, with security, Kafka and tests all working.
- It read the real Keycloak realm before coding and found there is no `sales` user. It handled that with a `SALES_USERS` setting rather than altering Keycloak.
- It put the logic on the SQLAlchemy session (`before_flush`/`after_flush`), so REST, the B2B API and Kafka all pass through it. That is the same idea as the rule engine, built by hand.
- It was candid in its summary about what it did not build: no SQL fallback, no traceability report.

**GenAI-Logic**
- The credit requirement became five declarations that mirror its sentence order. Every change path is covered by the engine rather than enumerated.
- Judgment calls were triaged: three needed a human decision (read-only role for sales, Order/Item rows not filtered, stamping `CreatedOn`), and the rest were FYIs.
- It also delivered what the native baseline was not asked for: Admin App, JSON:API with filtering and relationships, 15 scenarios, a generated report, and diagrams.

## Where the difference shows

1. **Change paths.** The native summary lists what it had to handle by hand: item insert/update/delete, item moved between orders, order moved between customers, order shipped, order deleted, credit limit lowered. It handled them correctly, but each is code someone must keep correct. In the docker project, none of these appears in the code; the engine derives them from the five rules. This is the strongest point of contrast, and it appears in the native run's own words.
2. **Totals.** Native recomputes totals with SQL aggregates on each flush. The rule engine adjusts incrementally. That is a design difference with a cost at scale, not a correctness difference here.
3. **Where the effort goes.** Native spent its time writing and debugging the plumbing: REST, auth, session hooks, consumer. The docker run spent its time on the CE reading list, the two correction loops, and the extras (report, diagrams, 15 tests).
4. **Review burden.** Native: scan 383 lines plus a 13-item list. Docker: scan 21 lines of rules plus three 🔴 items. The docker items are specific enough to answer yes or no. The native items are mixed in with FYIs.
5. **Test depth.** 15 scenarios vs 5. Native's tests are the minimum the script asked for (one per requirement scenario), so this gap is partly by design.
6. **Security surface.** Native left `/consume_debug`, `/health` and `/kafka_log` unauthenticated to match the documented curl, and said so. It is not a production default. Docker's comparable debug endpoint is a project default too, so this is not a point against native alone.
7. **Both made the same calls** on the ambiguous points: "unpaid" means `date_shipped IS NULL`; a balance equal to the limit is accepted; the shipping message goes out only when `date_shipped` is first set. That suggests these readings follow from the requirements, not from either tool.

## API surface

The native script asked for "a REST API over its tables (JSON, filter by attribute, create/update/delete)", and that is what it got. The generated API is documented at https://apilogicserver.github.io/Docs/API/. The native column below is from reading `app/api.py`; the GenAI-Logic column is from that documentation page and was **not exercised** on `demo_eai_docker`, so treat it as documented capability.

| Capability | demo_eai_native | GenAI-Logic (documented) |
|---|---|---|
| CRUD per table | Yes, generic routes over every table | Yes, an endpoint per table |
| Multi-row retrieval | List endpoint, default 100 rows; no fetch of several ids in one call | Yes, via filtering and pagination |
| Filtering | Equality only (`?customer_id=3`); unknown column returns 400 | Yes (syntax not given on the page) |
| Sorting | None; always ordered by `id` | Yes |
| Pagination | `limit` / `offset`; no total count, no links, no cap on `limit` | Yes |
| Related data access (e.g. customer + orders) | No. `to_dict` returns the table's own columns, the models define no relationships, so a customer plus its orders is two calls, and each order's items one more call per order | Yes, "related data access" (filtering, sorting and pagination "including access to related data"), following the relationships in the models |
| Optimistic locking | None. `PATCH`/`PUT` is last-write-wins; no version column, ETag, `If-Match` or checksum | Yes, a checksum scheme (a separate page; the API page itself doesn't describe it). An `S_CheckSum` attribute appeared in a live API response from a generated project during the Kafka verification |
| Swagger / API discovery | None | Generated automatically at `localhost:5656` |
| Business logic on update APIs | Yes, via the session hooks | Yes, enforced for every update API |
| Security | Keycloak token check, row filter on list, by-id, and writes | Enforced by the declared security |
| Custom endpoints | Hand-written Flask routes (`/OrderB2B`, `/consume_debug`) | Added in `api/customize_api.py` with Flask and SQLAlchemy |

Two points about fairness:
- The native run did what its script asked. The script did not mention related data access, sorting, locking or Swagger, so their absence is a property of the script as much as of plain Python. A script that asked for them would have produced more code, and the line counts above would grow.
- Optimistic locking is the one that carries real risk. Without it, two clients editing the same customer or order both succeed and the later write wins silently. The derived columns (`balance`, `amount_total`, `amount`) are read-only and recomputed on every flush, so a stale write cannot corrupt them, but ordinary fields such as `credit_limit` or `quantity` can be overwritten.

## Messaging: the two-message pattern

The subscribe requirement says only: map `Account` to Customer by name, `Items.Name` to Product by name, `QuantityOrdered` to Item.quantity. It says nothing about keeping the raw message or about what happens to a bad one. The two-message pattern comes from the GenAI-Logic project context (`eai_subscribe.md`), which the native script forbids reading.

| | demo_eai_native | demo_eai_docker |
|---|---|---|
| Raw payload kept | No. There is no blob table; the database has the original six tables | Yes. The blob table `order_b2b_message` holds each payload, `received_at`, `is_processed` and `error_text` |
| Transactions per message | One. Parse, map and commit in a single handler (`integration.consume`) | Two. Consumer 1 saves the blob and commits; a row event publishes to `order_b2b_processed`; Consumer 2 parses it into an Order in a clean transaction |
| Bad message (unknown account or product, bad quantity) | Logged as "rejected" and dropped; the payload and the reason are gone | The blob stays, with the reason in `error_text`; a live scenario checks this |
| Credit failure on an inbound order | Rolls back everything, including any record that the message arrived | Rolls back only the second transaction; the blob and its error remain |
| Offsets | Auto-commit on, so a restart does not replay; a rejected message is still consumed | Never committed, with `earliest`, so every start replays the topic; topics must be reset first (a requirement of the verification step) |
| Debug path | `/consume_debug`, same function as the consumer | `/consume_debug`, same parse logic, with live and simulated modes |
| Subscribe scenarios | 1 | 4 (accept, reject unknown account, keep blob with error, live-only) |

What this shows:
- The native run satisfied the requirement as written. The difference is in the case the requirement does not mention: a message that cannot be processed. Native loses it silently; the docker project keeps it where an operator can see why.
- The two designs trade differently on restart. The native consumer avoids replaying old messages and may lose a bad one. The docker consumer replays everything on each start, which cost a correction loop in its run (3 junk orders from earlier projects' messages), but nothing is lost.
- The native summary's judgment-call list mentions the `earliest` setting and the topic reset. It does not mention that rejected messages are dropped.
- Whether the pattern is "right" depends on the system. For a partner feed where a rejected order must be traceable, the blob is the stronger design. For a fire-and-forget feed, the native one is simpler and has fewer moving parts (one consumer, one table fewer, no second topic).

## Caveats

- The elapsed times are not comparable: native was timed per step; docker was not, and it did more.
- The docker line count is my `wc` over the files that hold the requirement logic, not an official figure. The native count is the AI's own, reported in its summary.
- Native tested the sales row filter with a stand-in user (`u1`), because the realm has no sales user. The docker project's security scenario runs against the same realm; I did not check how it maps the role.
- The API comparison for GenAI-Logic comes from its documentation, not from calls against `demo_eai_docker`. Exact parameter syntax for filtering, sorting, includes and the checksum was not verified.
- A probe of the native app found no foreign-key reparenting bugs (the two from `declarative-vs-procedural-comparison.md` are absent), because it recomputes touched parents from scratch on every flush. It did find that an item can be pointed at an order that does not exist. The script wording that produced the recompute design is also in question: the script was rewritten before this run and added "create/update/delete", which may have made that design more likely than in earlier native runs.
- Neither run was repeated, so run-to-run variance is unknown. The earlier docker runs showed the AI skipping or paraphrasing steps, so one run each is thin evidence.

## Trust: an enterprise standard by architecture, not discipline

Here "trust" means the system is held to an enterprise standard because of how it is built, not because the prompt, the developer or the reviewer remembered to ask. Not every developer remembers the details of APIs, optimistic locking, or every path that can change a value, and they should not have to.

What this pair shows:
- **The prompt decides what plain AI code includes.** The native run avoided the foreign-key reparenting bugs after the script said "create/update/delete"; the same gap appears in [Tech-Standard-Reqs](https://apilogicserver.github.io/Docs/Tech-Standard-Reqs/), where a procedural spec produced no update or delete path. The native app also has no optimistic locking, no related data access, and drops a message it cannot process, because the script named none of them.
- **In the generated stack, those behaviors do not depend on the prompt.** Rules are declared on the data, so every path to it is covered, and the generated API provides filtering, sorting, pagination, related data access and the optimistic-locking checksum (documented; not exercised here).
- **Native code can be correct.** This run's reparenting was. The claim is about where the guarantee lives: in the platform for the generated stack, in whatever the prompt happened to say for plain code.

Two limits on the claim:
- **The messaging default is platform-supplied, and delivered by instruction.** The two-message pattern reached `demo_eai_docker` through the project context that ships with every project, not through anything the developer wrote or remembered: the script says "implement requirements", and the context turns the Kafka-subscribe wording into the blob table, the second consumer and the reject record. For the developer that is architecture. It differs from the rule engine in how it is enforced: an instruction can be skipped by the model that reads it (the verbatim hand-off line was skipped in two blind runs of this same project), while the engine cannot skip a change path. The pattern was followed here; the report is how a reader checks that it was.
- **Trust needs evidence, not only construction.** The traceability report shows each requirement, its rules, its tests and the last result, so the standard can be checked without probing the code. The native run's only trace is a hand-written summary, and I found its one bug (an item pointing at a missing order) by probing it.

One native run cannot show how often the prompt changes the outcome. A few repeats of the original and the rewritten script would give counts.

## Bottom line

For this scope, plain Python got to a working, tested system in under five minutes, and it was honest about its gaps. GenAI-Logic took longer here but delivered more (UI, 3x the scenarios, a report) and expressed the core requirement in a fifth of the code, with change-path coverage that the native run had to reason about case by case. The API gap points the same way: the native REST layer is what the script asked for (flat CRUD, equality filters, limit/offset), while the generated one adds related data access, sorting, Swagger and optimistic locking without being asked. The messaging gap is the same kind: the native app does what the requirement says, and the docker project also handles the case it does not say (a message that cannot be processed). The right claim from this pair is **trust** (an enterprise standard held by architecture, not discipline) and **maintenance and review cost**, not build speed. To test build speed fairly, repeat the native run with the same extras (tests per rule, report) or strip the docker script to the same five steps.
