# CE backlog: using a user's role inside a business rule

Status: **proposal, not implemented.** Written 2026-10-29. No CE or sample changed.

## The gap

Requirements often make a rule conditional on who is calling: a manager may override a limit, an approver may exceed a threshold. Example: ERPNext's credit check is skipped for a user holding the `credit_controller` role (see `Modernization/erpnext/erpnext_modernize`, requirements section 4).

The engine already supports this. `Security.current_user_has_role(role_name)` is in `security/system/authorization.py` (line 64), generated into every project. It is used once, inside the security code itself (`is_sa = Security.current_user_has_role('sa')`, line 305).

The CE does not mention it for business rules:
- `docs/training/security.md` teaches `DefaultRolePermission`, `Grant`, `GlobalFilter` (access control) and shows `Security.current_user_id()` only inside a grant filter.
- No sample uses a role check inside a rule. The only use of the current user in logic is the created-by / updated-by stamping handler (`Security.current_user().id`, `logic/logic_discovery/system/all_classes_stamping.py`).
- LogicBank itself knows nothing about users or roles.

Searched: LogicBank, `samples/nw_sample`, all prototype samples, `Docs/docs`.

## Would an AI find it unaided?

Doubtful. It lives in a system file the CE does not send the AI to read, and no doc connects "role" with "business rule". Not verified; see the plan.

## Proposal

A short section in `docs/training/security.md` (and the project CE pointer to it), "Roles inside business rules":
- NL mapping: "users with role X may exceed the limit" maps to a role check in the constraint or event.
- Example using `Security.current_user_has_role(...)`.
- What happens with **no user** (Kafka consumer, batch job, test insert): must be stated after testing.
- Note that such a rule depends on the caller; keep it small and record it in ad-libs.

## Before documenting: verify

1. In a live rule, with the Keycloak provider, the SQL provider, and no user (Kafka or a direct insert): what does the method return, does it raise?
2. Whether it works inside `constraint(calling=...)` and inside events, and whether dependency scanning is affected (the CE warns about literal `row.` tokens in rule bodies).

## Sequence

Do **not** fix the CE before the ERPNext run (`samples/requirements/erpnext_modernize`). The blind run shows whether the AI finds the method unaided. If it does, this is optional polish. If it does not, that run is the evidence. Then verify (above), then change gold source (`org_git/ApiLogicServer-src`, then Docs).

## Result of a first blind test (2026-10-29)

Setup: copy of `samples/demo_emp_types` (`emp_types_role_test`), Keycloak security added, one line added to `department_budget/requirements.md`: "A user with the manager role may exceed the budget; other users may not." A fresh agent, told only to run "implement reqs department_budget" with the project's own CE, built it. ~5 minutes, 36 tool calls.

- **It found `Security.current_user_has_role('manager')` unaided**, by reading `security/system/authorization.py`. By its own report, no CE or training file told it how: `security.md` covers grants and filters only. So the gap is real but the AI can route around it.
- Verified through the API: `u1` rejected (400), `sam` and `u2` (manager) allowed (200), `admin` (role sa) rejected; no user (a script with no request) enforced the budget. I re-read the rule file and the DB is restored.
- Its ad-libs 🔴 items: no user means not a manager (budget enforced); only the literal role `manager` is exempt; the exemption belongs to whoever commits; **after a manager exceeds the budget, a non-manager cannot update that department or its employees until it is back within budget** (the requirement is silent).
- It also reported an optimistic-locking error ("row altered by another user") after a rejected PATCH. Unconfirmed as related; the old rule probably did the same.

Caveats:
- The sample's project CE is **version 3.30 (7/1/26)**, older than the current one; the agent found no "edit an existing requirement" procedure, which the newer CE has. The test is of the older CE.
- My prompt asked the agent to say which file told it how to check the role. That hints that role checks exist; the ERPNext requirement also says "role". Not a fully blind test.

Conclusion so far: the CE fix is still worth making (the agent had to find it by reading system code), but it is lower urgency than I expected.
