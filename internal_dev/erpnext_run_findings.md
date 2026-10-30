# CE / engine findings from the ERPNext credit rebuild (2026-10-29)

Source: blind run of `samples/requirements/erpnext_modernize/create_script.txt` into `erpnext_credit_modernized` (18:10 to 18:31, 53 of 53 scenarios passing). Run log: `erpnext_credit_modernized/docs/requirements/run_log.md`. Master notes: `marketing/Modernization/erpnext/`. **Nothing here is fixed; status of each item says how well it is verified.**

## Worked

- **Roles inside business rules.** The agent found `Security.current_user_has_role(...)` through the new `security.md` section "Roles inside business rules" (reached from the project CE's Security section). Second blind run to do so (`ce_roles_in_business_rules.md`).

## Findings

| # | Finding | Evidence | Status |
|---|---|---|---|
| 1 | **A rejected document returns HTTP 500**, not 400. The credit rules are `Rule.commit_constraint(calling=...)` raising `ConstraintException`; `testing.md` (Rule #7) expects 400. The generated test asserts `status_code >= 400`, not `== 400`. | agent report; `features/steps/erpnext_credit_steps.py:497` | Reported by the agent, **not re-checked**. Open: does `commit_constraint` map to 500 by design, or is it a gap in the CE's test guidance? |
| 2 | **Traceability report: copy-from-group endpoint missing** from "custom API endpoints" although its file carries a `Feature:` line. | agent report | Reported, not re-checked |
| 3 | **Traceability report: a rule marked untraced** (`_link_customer_company`) because requirement sections 3 and 8 had no `Feature:` line; the CE's Executable Requirements guidance covers `Feature:` for logic files, not for helper rules serving an unnamed section. | agent report | Reported, not re-checked |
| 4 | **Four document checks shown as "not seen in a test log"**, although scenarios exercise them. Commit constraints may not be named in the engine's log the way the report expects. | agent report | Reported, not re-checked |
| 5 | **The agent read LogicBank source** (phase order, LogicRow API, dependency scanner, commit constraints), about 3 minutes, outside the CE. The CE does not explain when to use `commit_constraint` versus `constraint` or what phase a commit constraint sees. | run_log.md, deviation 2 | Candidate CE section; check `logic_bank_api.md` first |
| 6 | **Second DDL pass.** The pre-coding schema analysis missed Delivery Note share columns the credit rule needed; one extra ALTER and rebuild (about 4 minutes). | run_log.md, deviation 3 | Observation only |
| 7 | **Optimistic-locking error in the seed script** twice (also seen in the `emp_types` run after a rejected PATCH). The agent restored the database and changed the seed. | run_log.md; `ce_roles_in_business_rules.md` | **Seen twice, unexplained.** Worth a look at `api/system/opt_locking/opt_locking.py` |
| 8 | **`admin.yaml` swap needs a human each time.** Both runs stopped there. Intended by the CE, but a script cannot finish unattended. | both runs | Design question, not a bug |
| 9 | **TEXT column default keeps its quote marks** (LogicBank `get_default_for_type`). | `org_git/logic_bank_bugs.md` entry 1 | Reproduced |
| 10 | **My script treated "create ... from starter.sqlite" as Method 1**, so the Manager's Method 4 provenance step (STEP 5) did not run. | run_log.md, deviation 8 | Script design; fix in `create_script.txt` if provenance files are wanted |

## Suggested order

1 (is it by design?), 7 (seen in two runs), then 5 (a CE section on commit constraints), then the report items 2 to 4.

## Added after the audit CE test (2026-10-29)

| # | Finding | Evidence | Status |
|---|---|---|---|
| 11 | **Stamping handler under Keycloak stores `DotMapX()`.** `all_classes_stamping.py` reads `Security.current_user().id`; a Keycloak user (DotMap from the token) has `name` and no `id`, and a DotMap returns an empty DotMap for a missing key, so no exception and the value is garbage. Stamping is off by default, so it is latent. | blind audit run, section 6 | **Not fixed.** Template: `prototypes/base/logic/logic_discovery/system/all_classes_stamping.py` (and the copies in `nw_sample` and the other samples) |
| 12 | **Grants cannot make a table append-only.** `DefaultRolePermission` turns access on and a `Grant` only adds; denying insert would also block the engine's own audit inserts. | read of `security/system/authorization.py` (`exec_grants`: `can_x = can_x or ...`) and the audit run | CE text corrected (PATTERN 3c). Real fix would be a different mechanism, if wanted |
| 13 | `implement_requirements.md` "Valid Event Uses #1" showed audit as a `Sys*Req` table written from an `early_row_event`. | audit run | Replaced with a pointer to PATTERN 3c |
