# Bug: `add-auth --provider-type=sql --db-url=sqlite:///database/db.sqlite` always crashes

**Status:** Fixed in gold source (docs only — no code change), copied to venv + all 9
sample snapshots that had the bad example + the two published Docs Eval exports.
**Not yet committed or pushed.**

**Found:** 2026-09-05, while empirically verifying that the SQL auth provider is NOT
affected by the sibling bug in this same folder ([[keycloak-login-bug-2026-09-05]]) —
Val asked "so sql auth is broken?" and the honest way to answer was to actually run it,
not just read the code.

**Related but distinct:** this is a **documentation** bug, not a code bug — unlike the
Keycloak fix next door. No `.py` file changed. The CLI's own behavior is correct; the
CE's own example told users to invoke it in a way that reliably breaks it.

---

## When this actually manifests

Any time someone follows this project's own documented example for enabling SQL-based
auth:
```bash
genai-logic add-auth --provider-type=sql --db-url=sqlite:///database/db.sqlite
```
This is not an obscure edge case — it was the literal example in `docs/training/security.md`
and the "Security - RBAC" section of `.github/copilot-instructions.md` (the Project CE every
created project ships), so it's what an AI assistant or a developer following the docs would
naturally type. **100% reproducible, every time, on every fresh project** — confirmed on a
brand-new project created seconds earlier with nothing else touched.

It does **not** affect:
- `genai-logic add-auth --provider-type=sql` (no `--db-url` at all) — works correctly.
- `genai-logic add-auth --provider-type=sql --db-url=postgresql://postgres:p@localhost/authdb`
  (a genuinely separate database) — works correctly; this pattern is already documented
  correctly elsewhere (`security/readme_security.md`, `Security-Activation.md`).
- Keycloak provider — unrelated code path entirely.

## Root cause

`--db-url` on `add-auth` means **"where is the separate auth database"** — it is *not*
"which project database should this project use." Confirmed directly from the CLI source
(`cli.py`, `add_auth_cmd`): the flag is passed straight into `auth_db_url`, while the
project's own `db_url` is hardcoded to `""` for this command. `add_auth_model()` then
performs a non-recursive `create_project()` call against `auth_db_url` specifically to
generate `database/database_discovery/authentication_models.py` — the file that must define
`User`/`Role`/`UserRole` classes so the login endpoint can be spliced in.

Passing `sqlite:///database/db.sqlite` — the project's own domain database — makes
`add_auth_model()` faithfully introspect *that* database instead of the auth one. Since a
plain domain database (e.g. built from `basic_demo.sqlite`: Customer/Order/Item/...) has no
`User`/`Role`/`UserRole` tables, sqlacodegen correctly generates a domain-shaped
`authentication_models.py` — and, worse, **overwrites the correct pre-built
`database/authentication_db.sqlite`** (which every project already has, created automatically
by `genai-logic create`, containing `Apis`/`Role`/`User`/`UserRole`) with a copy of the domain
database. The next step then searches the newly-corrupted file for the marker
`UserRoleList : Mapped[List["UserRole"]] = relationship(back_populates="user")` to know where
to splice the login endpoint — finds nothing (correctly — there is no such relationship in a
domain-only schema) — and raises:
```
Exception: Internal error - unable to find insert:
.. seeking UserRoleList : Mapped[List["UserRole"]] = relationship(back_populates="user")
.. in .../database/database_discovery/authentication_models.py
```

Confirmed the corruption happens **during `add-auth`**, not at project creation: a freshly
created project's `database/authentication_db.sqlite` correctly contains
`Apis`/`Role`/`User`/`UserRole` *before* `add-auth` runs; only after running `add-auth` with
the bad `--db-url` does it get overwritten with the domain schema.

## The fix

Doc-only. Every occurrence of the misleading example was changed from:
```bash
genai-logic add-auth --provider-type=sql --db-url=sqlite:///database/db.sqlite
```
to:
```bash
genai-logic add-auth --provider-type=sql
```
with an explicit warning added against ever pointing `--db-url` at the project's own
database, and a note that a real separate auth database (e.g. Postgres `authdb`) is the only
valid use of that flag for the SQL provider.

## Verification (live)

- Fresh project, `genai-logic add-auth --provider-type=sql` (no `--db-url`): succeeded
  cleanly; `authentication_models.py` correctly contains `class User`, `UserRoleList`, etc.
- `POST /api/auth/login` with a seeded user (`admin`/`p`) → `200` with a real, locally-minted
  HS256 JWT.
- Same endpoint with a wrong password → `401 "Wrong username or password"`.
- This confirms the SQL provider's own code (`get_user()`, `check_password()` in
  `security/authentication_provider/sql/auth_provider.py`) was never broken — the crash was
  entirely in the documented invocation, before any provider-specific code ever ran.

## Where this has been applied

- Gold: `api_logic_server_cli/prototypes/base/docs/training/security.md` and
  `.github/copilot-instructions.md`
- Propagated to the 8 sample snapshots that had the bad example: `demo_customs_clvs`,
  `demo_customs_surtax`, `demo_emp_types`, `allocate_dept_account_demo`, `basic_demo_eai`,
  `basic_demo_sample`, `basic_demo_logic_gov`, `library_rfi`
- **Not applied** to `basic_demo_ai_rules-supplier` and `allocate_dept_account_demo`'s
  `.github/copilot-instructions.md` — checked directly, these two already had the *correct*
  two-line pattern (bare + real Postgres example), not the buggy one. Nothing to fix there.
- Propagated to venv (immediate effect) and this session's live `basic_demo_eai` copy
- Propagated to the two published Docs Eval exports (`Eval-security.md`,
  `Eval-copilot-instructions.md`) in `org_git/Docs`
- **Not applied** to `prototypes/manager/system/genai/examples/*` (uses a different,
  non-literal placeholder pattern — `--db-url={database config}` — not actually wrong) or to
  `genai_demo_docs_logic` (already-divergent reference copy, same reasoning as the sibling
  Keycloak bug report)
- **Not committed, not pushed** in either repo — pending review.
