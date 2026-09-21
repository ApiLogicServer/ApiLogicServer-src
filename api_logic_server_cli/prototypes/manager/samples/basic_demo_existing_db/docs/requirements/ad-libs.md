# Ad-Libs — basic_demo_existing_db

Every assumption or guess made beyond the prompt spec (`project_creation_prompt.md`).

1. **`//`-prefixed lines treated as comments, not spec.** The prompt file's first three
   lines (`// Exectuable Reqirements...`, `// Paste this entire text...`, `// Or, paste
   just this: Create basic_demo_existing_db from samples/prompts/basic_demo_new_db.prompt`)
   are human-facing documentation about how to invoke the prompt, not instructions to
   execute. Per Manager CE STEP 0, these were read for context but not acted on — the
   project was created from `samples/dbs/basic_demo.sqlite` exactly as line 6 of the
   prompt (the first non-comment line) specifies, not from the alternate `basic_demo_new_db.prompt`
   path the comment mentions.

2. **No DDL/schema design step.** Because the source database (`basic_demo.sqlite`)
   already contained all required tables/columns (customer.balance, customer.credit_limit,
   order.notes, order.date_shipped, order.amount_total, item.quantity, item.unit_price,
   item.amount, product.unit_price), Method 4 STEP 4's constant-extraction / FK-inventory /
   Request Pattern schema-design sub-steps (4a-4d) were not applicable — there was no new
   schema being designed. This is the standard "existing database" path, not a gap.

3. **No seed data added.** The prompt's source database already contained sample rows.
   Per project CE guidance ("only if the source db had no data... leave it as-is"), no
   seeding script was written or run — the existing sample data was used as-is and verified
   via live API testing (see project_creation_report.md step 8), then any test-created rows
   were deleted afterward to leave the original seed data unchanged.

4. **Kafka topic name and trigger condition taken literally from the prompt.** "Publish the
   Order to Kafka topic 'order_shipping' when the date_shipped becomes not None" was
   implemented as an `after_flush_row_event` firing when `date_shipped is not None and
   (old_row is None or date_shipped changed)` — the standard project-CE pattern for this
   exact phrasing, including the on-insert-with-value edge case the prompt doesn't
   explicitly call out but which is a known real failure mode if omitted (see
   `docs/training/` project CE guidance). No Kafka broker is configured in this environment
   (`KAFKA_SERVER` not set) — publishing runs in documented fallback/debug mode (logs the
   would-be message; verified via `logs/als.log`), not an ad-lib, just the environment's
   default state.

5. **Constraint boundary: "less than" interpreted as `<=`.** Per the project CE's
   documented boundary-operator convention (business-rule "less than X" almost always means
   "don't exceed X," and the prompt gives no exact boundary value), `Customer.balance <
   credit_limit` in the prompt text was implemented as `row.balance <= row.credit_limit` —
   the CE's standing, deliberate convention, not a one-off guess for this project.

6. **Use case grouping / file naming inferred from prompt structure.** "On Placing Orders,
   Check Credit" produced `logic/logic_discovery/place_order/check_credit.py` (context
   phrase → directory, colon-terminated phrase → file) per the standard Directory
   Structure = Requirements Traceability convention; "Use case: App Integration" (no
   further context-phrase nesting) produced the flat `logic/logic_discovery/app_integration.py`.
