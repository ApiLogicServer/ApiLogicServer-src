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

`cryptography` on `aarch64` is kept at `>=43.0.0` (not bumped to `>=46.0.7`) due to known
build issues on ARM machines. All other platforms use `>=46.0.7`.

Relevant lines in `pyproject.toml` and `requirements-no-cli.txt` files:

```
cryptography>=46.0.7; platform_machine != 'aarch64'
cryptography>=43.0.0; platform_machine == 'aarch64'
```

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

## Source Reports

- `internal_dev/code_base/Security_report_apr_2026` — original CVE scan
- `internal_dev/code_base/Security_report2_apr_2026` — duplicate/confirmation scan
