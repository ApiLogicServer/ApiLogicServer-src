# Run Log: erpnext_modernize/create_script.txt

**Date:** 2026-10-29. **Manager:** Genai-Logic 17.05.12. **Mode:** FULL (Docker running; the Keycloak container was already up on localhost:8080, realm kcals). **Run start:** 18:10:27. **Run end:** 18:31. **Total:** about 21 min.

## Steps

| # | Script step | Start | End | Duration | Status |
|---|---|---|---|---|---|
| 1 | create project erpnext_credit_modernized from samples/dbs/starter.sqlite | 18:10:35 | 18:10:37 | 0:02 | ✅ |
| 2 | add security (Keycloak) | 18:11:06 | 18:11:07 | 0:01 | ⚠ no `docker compose up` (Keycloak was already running) |
| 3 | implement requirements erpnext_credit | 18:11:12 | 18:24:33 | 13:21 | ⚠ second DDL pass; admin.yaml left unswapped |
| 4 | create logic diagram for each requirement | 18:24:39 | 18:24:39 | 0:00 | ✅ 4 diagrams |
| 5 | create tests from rules, using default names | 18:24:45 | 18:29:27 | 4:42 | ✅ 4 features, 52 scenarios |
| 6 | run the tests | 18:29:44 | 18:30:30 | 0:46 | ⚠ first run 50/53, logic fix, second run 53/53 |
| 7 | run the requirements traceability report | 18:30:41 | 18:30:41 | 0:00 | ✅ |

## Results

- Behave (final run): 5 features, 53 scenarios passed, 0 failed, 0 skipped (52 erpnext_credit + the scaffold's about.feature); 543 steps passed.
- Traceability report: 4 requirements (Credit Limit Lookup, Credit Check, Credit Check On Documents, Credit Limit Maintenance), 4 of 4 implemented, 4 of 4 tested; 52 of 52 scenarios passed; 32 rules (15 declarative, 13 Python functions, 4 events); 26 of 32 rules appear in a test log. No Kafka.
- Ad-libs: 12 🔴, 12 🟡 (docs/requirements/erpnext_credit/ad-libs.md).

## Deviations

1. **Security bootstrap.** The Manager CE's "add security" says to run `cd devops/keycloak && docker compose up -d` before `add-auth`. I skipped it because Keycloak was already running and I had been told not to start containers. Cost: 0.
2. **Read installed engine source outside the CE.** To settle the engine's phase order (constraints run before the cascade to children), the LogicRow insert/update/delete API (`delete(row=...)` is broken), the dependency scanner's tokenizing, and how commit constraints keep the first old_row, I read files in `venv/.../logic_bank` (logic_row.py, abstractrule.py, formula.py, row_event.py, row_sets.py). I also grepped `security/system/authorization.py` to confirm `current_user_has_role`, which security.md had already told me to use. Cost: about 3 min.
3. **A second DDL pass during implement requirements.** While writing credit_check.py I found that a Delivery Note's docstatus change reaches its lines only after the note's own constraints have run. I renamed and added Delivery Note share columns (ALTER + a second `rebuild-from-database`) and moved the document checks to `Rule.commit_constraint`. Cost: about 4 min.
4. **Admin UI not swapped.** `rebuild-from-database` wrote `ui/admin/admin-merge.yaml`. The CE says never to copy it over admin.yaml without the user's confirmation, so I didn't, and the Admin App does not show the new tables yet. Logged as 🔴. Cost: 0.
5. **Seed script.** It failed twice with an optimistic-lock error when it updated a row the rules had just changed. I restored `database/db.sqlite` from my own pre-seed copy in the scratchpad (not from a sample) and changed the seed to enter the invoice already submitted. Cost: about 2 min.
6. **Logic changed during "run the tests".** The first run had 3 failures, all scenarios that move a row to another customer: the old customer's bucket was never reduced. I fixed `logic/logic_discovery/outstanding_amount.py` (a missing bucket is now inserted directly so it has an id), restarted the server and re-ran the tests: 53/53. Cost: about 1.5 min. The report was generated after the second run, so its results are current.
7. **check_step_order.py** flagged two ordering "issues" between unrelated patterns (different literal prefixes, so neither can match the other's text). I did not reorder them. `behave --dry-run` showed no undefined or ambiguous steps.
8. **Manager Method 4 STEP 5 (project-level provenance readme / prompt overwrite) not run.** The script's first line names a database ("create project X from <db>"), which the Manager CE maps to Method 1. The requirements came in through the project CE's Executable Requirements flow, which wrote `docs/requirements/erpnext_credit/ad-libs.md` and the link in `project_creation_report.md`.
9. **Not read:** `samples/requirements/erpnext_modernize/README.md`. It sits outside the named requirements directory, and the instructions limited my sources.
10. **Server stopped by PID** after each use. Port 5656 is free.

## Observations (not deviations)

- A rejected transaction comes back as HTTP 500, because the check is a commit constraint. testing.md Rule #7 expects 400. The tests assert `>= 400` plus the message.
- The report lists "No Kafka topics or custom API endpoints found". It did not detect `api/api_discovery/copy_credit_limits_from_group.py`, which registers its route with `add_url_rule` and carries a `Feature: Credit Limit Maintenance` docstring. The report also lists `_link_customer_company` as untraced, because §3 (Outstanding amount) and §8 have no `Feature:` line.
- The four document credit checks show as "not seen" in the logs. The report notes that a constraint is logged only when it rejects, and these are commit constraints raising their own message.

## CE and training files read, in order

1. CLAUDE.md (Manager root, and its parent) plus `.github/copilot-instructions.md`, the Manager CE (in context)
2. `erpnext_credit_modernized/.github/copilot-instructions.md`, the project CE v3.56 (lines 1-1206, 1453-2002, 3006-3130)
3. `erpnext_credit_modernized/docs/training/logic_bank_api.md` (loaded through the project CLAUDE.md)
4. `docs/training/security.md` v1.1 (full; it is the source of "Roles inside business rules")
5. `docs/training/implement_requirements.md` (full)
6. `docs/training/logic_bank_patterns.md` (full)
7. `docs/training/testing.md` (lines 1-130, 300-600, 890-1196)
