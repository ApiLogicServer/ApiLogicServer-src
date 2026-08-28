# CodeQL Trial Report

**Date:** 2026-08-28
**Source:** Workflow (`codeQL.yml`) provided by a partner organization, based on their internal GHAS reusable workflow config. Not kept in this repo — it's unused (calls a reusable workflow that only runs inside that organization's GitHub org) and carries organization-specific details, so it was removed rather than checked in.
**What was tried:** A local, interactive CodeQL scan using the CodeQL CLI + VS Code extension, run directly against a genned ApiLogicServer project — not that GitHub Actions workflow itself (see "Not yet done" below for why).

---

## TL;DR

- We ran GitHub's standard CodeQL Python security scan against a representative generated project and it worked cleanly — no tooling issues.
- It found 14 findings, all in code we auto-generate for every customer project (not in a customer's own business logic). Two were genuine, confirmed-exploitable bugs — an unauthenticated path allowed reading arbitrary files off the server's filesystem (e.g. `/etc/passwd`) through two admin/image endpoints. The other twelve were log-forging weaknesses — an attacker-controlled value could plant a fake-looking line into the application log, undermining its use as an audit trail.
- All 14 are now fixed at the source template level, so every project generated going forward already has the fix — nothing customers need to do. We verified each fix live (reproduced the exploit, confirmed it's blocked, confirmed normal functionality still works).
- Fixing the log-forging issue briefly broke one of our own internal test suites, due to a naming collision between our code and a same-named file in our own test harness — unrelated to CodeQL or the vulnerability itself. Caught and fixed same day; full regression suite is back to green.
- **Net result:** CodeQL scanning is viable for our codebase and surfaced two real, worthwhile fixes. The remaining gap is wiring it into our own GitHub CI (see "Not yet done") — to match enteprise CI procedures.

---

## Setup

1. Installed the CodeQL CLI: `brew install --cask codeql` (v2.26.4). The VS Code `github.vscode-codeql` extension (already installed) provides the UI/IntelliSense but does not bundle the CLI on its own.
2. Downloaded the official query pack: `codeql pack download codeql/python-queries` (v1.8.9).
3. Built a CodeQL database from a genned project:
   ```
   codeql database create <db-path> --language=python --source-root=basic_demo
   ```
   Target: `basic_demo`, the Manager's own "best for first-time users" sample project — genned via `genai-logic create`, representative of what a real customer runs.
4. Ran the standard suite:
   ```
   codeql database analyze <db-path> codeql/python-queries:codeql-suites/python-security-extended.qls \
     --format=sarif-latest --output=results.sarif
   ```

**Result:** Database built cleanly — 192 modules extracted, 86 Python files scanned, all 52 queries in the suite ran without error.

---

## Findings (14 total)

| Rule | Count | Files |
|---|---|---|
| `py/path-injection` | 2 | `ui/admin/admin_loader.py` (lines 122, 175) |
| `py/log-injection` | 12 | `ui/admin/admin_loader.py`, `api/system/api_utils.py`, `security/authentication_provider/sql/auth_provider.py`, `api/customize_api.py`, `api/api_discovery/mcp_discovery.py`, `api/api_discovery/new_service.py`, `api/api_discovery/newer_service.py` |

All 14 findings are in **generated scaffolding** (the `prototypes/base/...` template every genned project ships with) — none are in user-authored business logic (`logic/logic_discovery/...`) or in DDL/model code.

### Fixed: path-injection (2) — CWE-22

- **`ui/admin/admin_loader.py:175` (`get_image`)** — `path` came directly from the URL (`/ui/images/<path:path>`) and was f-string-concatenated into `send_file(f'ui/images/{path}', ...)`. Flask's `<path:path>` converter allows `/` in the segment, enabling `../` traversal — confirmed as a real unauthenticated arbitrary-file-read exploit (this route requires no login), not a false positive.
- **`ui/admin/admin_loader.py:122` (`admin_yaml`)** — same shape: `open(f'ui/admin/{path}', "r")`.

**Exploit confirmed live before the fix:**
```
GET /ui/admin/../../../../../../etc/passwd  →  200, file contents returned
GET /ui/images/../../../../../../etc/passwd →  200, file contents returned
```

**Fix applied** (`werkzeug.utils.safe_join` / `flask.send_from_directory`, which reject any resolved path that escapes the base directory):
```python
# get_image — was: send_file(f'ui/images/{path}', mimetype='image/jpeg')
response = send_from_directory("ui/images", path, mimetype='image/jpeg')

# admin_yaml — was: open(f'ui/admin/{path}', "r")
safe_path = safe_join('ui/admin', path)
if safe_path is None:
    abort(404)
with open(safe_path, "r") as f:
    content = f.read()
```

**Verified after fix** (both local `basic_demo` test copy and gold source):
```
GET /ui/admin/../../../../../../etc/passwd  →  404
GET /ui/images/../../../../../../etc/passwd →  404
GET /ui/admin/admin.yaml                    →  200 (legit route unaffected)
GET /ui/images/Product/diary.gif            →  200 (legit route unaffected)
```

**Ported to gold source:** `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/ui/admin/admin_loader.py` — every future `genai-logic create` inherits the fix. Diffed byte-for-byte identical to the tested `basic_demo` copy.

### Fixed: log-injection (12 found by CodeQL + 1 more found by inspection) — CWE-117

**What it is:** e.g. `app_logger.info(f'... {log_dir}')` where `log_dir` can contain attacker-chosen text. If that value has an embedded newline plus something shaped like a log line, the attacker can plant a fabricated line in the log — indistinguishable from a real entry to anyone reading it later — or desync a downstream log parser/SIEM that expects one clean line per entry. Not code-execution/data-exposure, but corrupts the audit trail.

**Fix applied:** added `safe_log(value)` to `api/system/api_utils.py` (strips `\r`/`\n`), imported and applied at every call site that logs an externally-derived value — `ui/admin/admin_loader.py`, `api/customize_api.py`, `api/api_discovery/{mcp_discovery,new_service,newer_service}.py`, and both `security/authentication_provider/{sql,keycloak}/auth_provider.py`. The Keycloak provider wasn't in CodeQL's original 12 (basic_demo's active scan path uses the SQL provider), but has the identical pattern — found by inspection while fixing the SQL one, and fixed too.

**Verified live** (`basic_demo`, `/hello_service?user=attacker%0A...FAKE LOG LINE`): before the fix this splits into two log lines, the second indistinguishable from a real entry; after the fix it lands as one line (`attacker 2026-08-28 ... FAKE LOG LINE`) with the newline replaced by a space — no fabricated line possible.

**Ported to gold source + all 8 samples** under `prototypes/manager/samples/`, same process as the path-injection fix. `devops/keycloak/unused/auth_provider.py` (dated Feb 2025, named `unused/`, not copied into projects) was left as-is — genuinely dead reference code.

### Regression: log-injection fix broke BLT's behave tests — fixed

**Symptom:** After porting the `safe_log` fix, `tests/build_and_test/build_load_and_test.py`'s `validate_nw` step (behave run against the generated `ApiLogicProject`/Northwind sample) started failing immediately, with an empty `test/api_logic_server_behave/logs/behave.log`.

**Root cause:** `security/authentication_provider/{sql,keycloak}/auth_provider.py` added `from api.system.api_utils import safe_log` (see above). That import resolves fine when the server runs normally (project root is on `sys.path`, `api/` is a real package there). But when behave loads step definitions, it puts `test/api_logic_server_behave/features/steps/` at the **front** of `sys.path` for the duration — and that directory contains its own `api.py`, a behave step-definitions file matching `features/api.feature`. Python resolves `api` to that shadowing file instead of the project's `api/` package, so `from api.system.api_utils import safe_log` fails with `ModuleNotFoundError: No module named 'api.system'; 'api' is not a package`. This aborts `config/config.py` at import time (it imports `auth_provider.py`), which behave's `test_utils.py` imports before any scenario can run — hence the empty log file.

This is a latent naming collision between the project's `api/` package and behave's own `steps/api.py`, dormant until the CodeQL fix added the first `api.*` import reachable from behave's test-collection path.

**Fix applied:** removed the `from api.system.api_utils import safe_log` import from both `auth_provider.py` files and gave each a local copy of the same one-line `safe_log` function instead (it has no dependencies, so duplication is cheap and avoids the fragile cross-package import). Applied to gold source and all 8 samples (16 files total).

**Verified:** direct `behave_run.py` invocation against the built `ApiLogicProject` — 7 features / 26 scenarios / 83 steps, all passing, exit code 0. Full BLT re-run: 17/18 tests passing (the 1 remaining failure, `docker_creation_tests`, is a `docker run -it` TTY requirement unrelated to this fix — fails only when BLT is run from a non-interactive shell).

---

## Assessment

- CodeQL setup and Python scanning **works** end-to-end on ApiLogicServer-genned projects, locally, with no GitHub Actions dependency.
- The 2 path-injection findings were genuine, confirmed-exploitable bugs (unauthenticated arbitrary file read) and are now fixed in gold source — see above.
- All 12 log-injection findings (plus 1 more of the same shape found by inspection) are fixed in gold source — see above.

## Not yet done

- The provided `codeQL.yml` calls a **private, organization-internal reusable workflow** (via a `uses:` reference to a private repo, plus `secrets: inherit`). It only runs inside that organization's GitHub org against their private reusable workflow repo — it will not run as-is on our own GitHub repos (ApiLogicServer-src, Docs, etc.).
- If we want CodeQL running in our own CI, that needs a standalone workflow built on GitHub's public `github/codeql-action` instead of a private reusable one. Not started yet.
