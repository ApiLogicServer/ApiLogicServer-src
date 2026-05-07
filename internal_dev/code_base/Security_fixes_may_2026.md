# Security Vulnerability Fixes — May 2026

## Files Updated

10 requirements files updated across the project:

- `requirements.txt`
- `pyproject.toml`
- `api_logic_server_cli/prototypes/base/venv_setup/requirements-no-cli.txt`
- `api_logic_server_cli/prototypes/manager/samples/basic_demo_eai/venv_setup/requirements-no-cli.txt`
- `api_logic_server_cli/prototypes/manager/samples/demo_customs/venv_setup/requirements-no-cli.txt`
- `api_logic_server_cli/prototypes/manager/samples/basic_demo_sample/venv_setup/requirements-no-cli.txt`
- `api_logic_server_cli/prototypes/manager/samples/allocate_dept_account_demo/venv_setup/requirements-no-cli.txt`
- `api_logic_server_cli/prototypes/manager/samples/basic_demo_ai_rules-supplier/venv_setup/requirements-no-cli.txt`
- `api_logic_server_cli/prototypes/manager/system/app_model_editor/venv_setup/requirements-no-cli.txt`
- `api_logic_server_cli/prototypes/manager/system/genai/examples/genai_demo/genai_demo_docs_logic/venv_setup/requirements-no-cli.txt`

---

## Critical / High CVEs Addressed

| Package | Before | After | CVE(s) / Notes |
|---------|--------|-------|--------|
| Flask | `==2.3.2` | `>=3.1.3` | CVE-2026-27205 |
| Flask-JWT-Extended | `==4.4.4` | `>=4.7.1` | Required for Flask 3.x compat (`<3.0` constraint removed in 4.6.0) |
| Werkzeug | `==2.3.3` | `>=3.0.0` | Required for Flask 3.x compat (Flask 3.x requires Werkzeug 3.x) |
| itsdangerous | `==2.1.2` | `>=2.2.0` | Required for Flask 3.x compat (Flask 3.x requires `>=2.2.0`) |
| Flask-Login | `==0.6.2` | `>=0.6.3` | Required for Flask 3.x compat (0.6.2 pins Werkzeug 2.x) |
| Flask-Cors | `==3.0.10` | `>=6.0.0` | CVE-2024-6844, CVE-2024-6866, CVE-2024-6839, CVE-2024-1681, PYSEC-2024-71 |
| PyJWT | `==2.6.0` | `>=2.12.0` | CVE-2026-32597 |
| cryptography | `>=43.0.0` | `>=46.0.7` (non-ARM) | CVE-2026-34073, CVE-2026-39892 |
| PyMySQL | `==1.0.3` | `>=1.1.1` | CVE-2024-36039 |

## Medium CVEs Addressed

| Package | Before | After | CVE(s) |
|---------|--------|-------|--------|
| Jinja2 | `==3.1.5` | `>=3.1.6` | CVE-2025-27516 |
| requests | `>=2.32.0` | `>=2.33.0` | CVE-2026-25645 |

## Not Addressed (out of scope / not in direct dependencies)

| Package | CVE(s) | Reason |
|---------|--------|--------|
| aiohttp | CVE-2026-34513 through CVE-2026-34525 | Not a direct dependency |
| langchain-core | CVE-2026-40087 | Not a direct dependency |
| Pillow | CVE-2026-25990 | Not a direct dependency |
| Pygments | CVE-2026-4539 | Not a direct dependency |
| pyasn1 | CVE-2026-30922 | Not a direct dependency |

---

## ARM / aarch64 Notes

`cryptography` on `aarch64` is capped at `<47` because 47.x and 48.x crash with `SIGILL`
(Illegal Instruction) on Parallels ARM VMs. Root cause: the Rust-compiled extension in 47+
uses SIMD instructions that the Parallels-virtualized ARM CPU does not expose, even though the
binary is valid aarch64. `cryptography 46.0.7` is the highest version confirmed safe and also
covers CVE-2026-34073 and CVE-2026-39892.

Relevant lines in `pyproject.toml` and `requirements-no-cli.txt` files:

```
cryptography>=46.0.7; platform_machine != 'aarch64'
cryptography>=46.0.7,<47; platform_machine == 'aarch64'
```

The crash manifests as `Illegal instruction (core dumped)` immediately on server start with no
Python output — it happens during `flask_jwt_extended` → `jwt` → `cryptography.hazmat.primitives.asymmetric.ec`
import chain, before logging is initialized. Diagnosed with `python -c "import faulthandler; faulthandler.enable(); exec(...)"`.

**Fix 5 — Ubuntu ARM BLT: cryptography 47+ SIGILL on Parallels aarch64 VM**

---

## Flask-Cors 6.x Runtime Fix (Applied)

Flask-Cors 6.x treats the `resources` dict keys as **regex patterns**, not glob patterns.
The old `r"/api/*"` was silently broken: in regex, `*` means "zero or more of the preceding
character `/`", so it matched `/api` and `/apiii` but **not** `/api/Customer`.

Fixed in all 8 `api_logic_server_run.py` prototype files:
```python
# Before (broken with Flask-Cors 6.x)
CORS(flask_app, resources=[{r"/api/*": {"origins": "*"}}, ...])

# After (correct regex)
CORS(flask_app, resources=[{r"/api/.*": {"origins": "*"}}, ...])
```

### CORS Test Coverage

The behave test suite does **not** explicitly assert CORS headers (no `Origin` request headers,
no `Access-Control-Allow-Origin` response checks). The security tests validate RBAC, not CORS.

Manual verification: start the server and send a preflight from a browser origin:
```bash
curl -s -I -X OPTIONS http://localhost:5656/api/Customer/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" | grep -i "access-control"
```
Expected: `Access-Control-Allow-Origin: *` in response.

## Breaking Change Warnings

### Flask 2.x → 3.x
- `before_first_request` decorator was removed — replace with `with app.app_context()`
- Some `g` and teardown behavior changed
- App factory patterns may need review
- **Action required:** Test full app startup and request cycle after upgrading

### Flask-Cors 3.x → 6.0.0
- CORS configuration API changed significantly
- `origins` parameter behavior updated
- **Action required:** Review CORS setup in the app after upgrading

---

---

## Windows ARM64 BLT Fixes (May 2026)

Two additional bugs surfaced when running the BLT on Windows ARM64 after the security updates.
The `cryptography` package has no Windows ARM64 wheel and cannot be built from source on that platform,
so it remains excluded there (both conditions in `pyproject.toml` exclude `platform_machine == 'ARM64'`
on Windows).

### Fix 1 — BLT fails at `als start` (`check_command` trips on oracledb stderr)

**File:** `api_logic_server_cli/sqlacodegen_wrapper/sqlacodegen_wrapper.py`

**Root cause:** `oracledb` is excluded on Windows ARM64 (no wheel). The `except ImportError` handler
used `log.error(...)`, which writes to stderr. The BLT's `check_command` function raises on
`"not found" in result_stderr`, so every `als start` / `als create` subprocess was flagged as failed.

**Fix:** `log.error` → `log.debug` (missing an optional driver on an unsupported platform is not an error).

### Fix 2 — Server crash after `add-auth` with Keycloak (`RSAAlgorithm` import)

**Files:** All 7 `security/authentication_provider/keycloak/auth_provider.py` files in `prototypes/`:
- `prototypes/base/`
- `prototypes/manager/samples/allocate_dept_account_demo/`
- `prototypes/manager/samples/basic_demo_ai_rules-supplier/`
- `prototypes/manager/samples/basic_demo_eai/`
- `prototypes/manager/samples/basic_demo_sample/`
- `prototypes/manager/samples/demo_customs/`
- `prototypes/manager/system/genai/examples/genai_demo/genai_demo_docs_logic/`

**Root cause:** `from jwt.algorithms import RSAAlgorithm` is a bare top-level import.
`RSAAlgorithm` requires `cryptography`, which is not installable on Windows ARM64.
The import fails at module load time, crashing the server before any request is handled.

**Fix:** Wrapped in `try/except ImportError` with `RSAAlgorithm = None` fallback.
Keycloak JWK verification (`RSAAlgorithm.from_jwk(...)`) will still fail at runtime if Keycloak
auth is actually invoked on Windows ARM64 — but the server starts correctly for SQL auth and
all non-Keycloak workflows.

**Note for existing projects:** Projects already created with `add-auth` before this fix must
have `auth_provider.py` patched manually or be recreated.

### Fix 3 — `rebuild_tests` fails: alembic `upgrade head` crashes on SQLite with views/FKs

**Files:** All 7 `database/alembic/env.py` prototype files:
- `prototypes/base/database/alembic/env.py`
- `prototypes/manager/samples/allocate_dept_account_demo/database/alembic/env.py`
- `prototypes/manager/samples/basic_demo_ai_rules-supplier/database/alembic/env.py`
- `prototypes/manager/samples/basic_demo_eai/database/alembic/env.py`
- `prototypes/manager/samples/basic_demo_sample/database/alembic/env.py`
- `prototypes/manager/samples/demo_customs/database/alembic/env.py`
- `prototypes/manager/system/genai/examples/genai_demo/genai_demo_docs_logic/database/alembic/env.py`

**Root cause:** SQLAlchemy 2.0.49 (pulled in by `>=2.0.48`) detects more schema differences
in autogenerate than earlier 2.0.x releases — specifically NOT NULL constraints, removed
foreign keys, and dropped columns. The generated migration contained `alter_column`,
`drop_column`, and `drop_constraint` ops. These all fail on the NW SQLite database because:
- SQLite has no `ALTER COLUMN`
- SQLite `DROP COLUMN` fails when a view (`ProductDetails_View`) or a self-referential FK
  (`Department.DepartmentId`) references the table being modified
- SQLite cannot drop constraints directly

**Fix:** Added `_filter_unsupported_sqlite_ops` hook via `process_revision_directives` in
`run_migrations_online()`. The hook uses a **whitelist** — for SQLite only, it keeps just
`AddColumnOp`, `CreateIndexOp`, and `DropIndexOp` from `ModifyTableOps`. All other
table-modifying ops (alter, drop column, drop/create constraint, FK changes) are silently
dropped from the generated migration script. `CREATE TABLE` and `DROP TABLE` are top-level
ops and are unaffected. Non-SQLite databases are unaffected.

### Fix 6 — BLT `docker_postgres_auth` fails: port 5656 not released before next server start

**File:** `tests/build_and_test/build_load_and_test.py`

**Root cause:** `stop_server()` sends an HTTP `/stop` signal but does not wait for the OS
to release port 5656. Flask's development reloader holds the port briefly after shutdown.
The `docker_postgres_auth` test runs `add-auth` (~2s) and then immediately starts a new
server — just fast enough to collide with the previous server still holding the port. The new
server exits with "Address already in use", so the 10-second ping gets Connection Refused.

**Fix:** Added a port-free poll (up to 10 seconds, 1s interval) at the top of
`start_api_logic_server()`, just before `subprocess.Popen`. If the port is already free,
there is zero added delay. Only on slow machines (ARM/VM) where port release lags does it
briefly wait.

---

### Fix 4 — `allocation_test` disabled on Windows (`sh test.sh` not available)

**File:** `tests/build_and_test/env_win.py`

**Root cause:** The allocation test validates results by running `sh test.sh` which uses
`curl`. Neither `sh` nor `curl` are natively available on Windows without Git Bash.

**Fix:** `do_allocation_test = False` in `env_win.py`. The Allocation project is still
created and the server is started; only the shell-script verification step is skipped.

---

## Source Reports

- `internal_dev/code_base/Security_report_apr_2026` — original CVE scan
- `internal_dev/code_base/Security_report2_apr_2026` — duplicate/confirmation scan
