# Removing Ontimize Support — Analysis

**Status:** Executed on branch `remove-ont` (uncommitted working tree). The analysis below is
the pre-decision record; see **Execution** at the end for what was actually removed — the real
footprint turned out to be substantially larger than this analysis scoped.

## What "Ontimize support" actually is

Ontimize is a third-party Angular component framework (`ontimize-web-ngx`). API Logic Server
generates an Ontimize-based Angular admin/CRUD app as an alternative "Front Office App" to the
React-based Admin App — positioned in the docs as complementary, not a replacement. It has never
left preview: the only user-facing doc page, `Docs/docs/App-Custom-Ontimize-Overview.md`, is
marked **"Under Construction - Beta"** and says outright: *"currently in preview state - not
ready for production... contact us if you would like to try it."* The last dated activity
anywhere in the docs changelog is **06/11/2024** ("Ontimize Rich Client Tech Preview") — over two
years stale as of this writing.

## Footprint

**Core generator code** (the two entry points named in the request, both confirmed):
- `api_logic_server_cli/create_from_model/ont_build.py` — 1,370 lines, `OntBuilder`
- `api_logic_server_cli/create_from_model/ont_create.py` — 362 lines, `OntCreator`
- Total: **1,732 lines** of dedicated generator code.

**CLI surface** — two commands in `api_logic_server_cli/cli.py`:
- `app-create` (line 447) → `OntCreator.create_application()` — docstring literally says
  "Creates Ontomize app model" (typo: "Ontomize").
- `app-build` (line ~493–518) → `OntBuilder`.

**Auto-invocation inside the normal create/rebuild flow** — this is the part worth flagging
specifically: `api_logic_server.py:1677` calls `create_and_build_ontimize_app(...)` during
*every* `ApiLogicServer create` / rebuild run, gated by `get_ontimize_apps()`
(`api_logic_server_utils.py:414`) scanning the target project for an existing ontimize app
directory. For ordinary projects (no ontimize app present) this is a no-op scan, but it means
Ontimize is wired into the mainline creation path, not cleanly siolated behind its own command.

**`app_model_editor`** (the second entry point named in the request):
`api_logic_server_cli/prototypes/manager/system/app_model_editor` is **441 files / ~100,686
lines**, but it is *not* an Ontimize-specific tree — it's a general project prototype/manager
scaffold. Only a small subset inside it is Ontimize-specific:
- `api/api_discovery/ontimize_api.py`
- `devops/docker-image-ont/`
- `ui/yaml/src/assets/{images,icons}/ontimize*.png` (8 icon sizes)
- one mention in `.devcontainer-option/devcontainer.json`
- one template snippet in `ui/templates/content.html`

So `app_model_editor` as a whole is **not** on the chopping block if the goal is "remove
Ontimize" — only ~13 files inside it are. Deleting the whole directory would be a much larger,
unrelated cut.  
Val's view - cut it.

**Full seed app:** `api_logic_server_cli/prototypes/ont_app/` — a complete 161-file Angular
project (`ontimize_seed/`), including its own `README.md`, `package-lock.json` (pulling
`ontimize-web-ngx` from npm), a `docker-compose-ontimize.yml`, and image assets. This is the
actual template cloned when `app-create` runs.

**Other copies of `ontimize_api.py`** (per-project template, not imported by the CLI itself):
`prototypes/base/`, `prototypes/nw/`, `prototypes/manager/samples/allocate_dept_account_demo/`.
Plus `docker-compose-ontimize.yml` in two more sample dirs (`allocate_dept_account_demo`,
`demo_customs_surtax`).

**Dependencies:** `requirements.txt:63-65` — `translate==3.6.1` and `libretranslatepy==2.1.1`,
labeled "Ontimize translation service." No other code references these packages, so they are
removable along with the rest. The Angular seed app pulls its own npm dependency
(`ontimize-web-ngx`) via a separate Node toolchain — not part of the Python package install, no
overlap with the rest of the framework's dependency surface.

**Tests:** None. No `test_ont*.py`, no behave features exercise `app-create`, `app-build`,
`OntBuilder`, or `OntCreator`. This is unmaintained/unverified code today — a removal isn't at
risk of breaking a test suite that currently proves it works, because nothing does.

**Blast radius (call graph):** Narrow. Only `api_logic_server.py`, `cli.py`, and one comment in
`model_creation_services.py:81` reference the ont_build/ont_create symbols. No other framework
module imports from them. The `ontimize_api.py` template copies only matter if a generated
project actually contains an ontimize app dir — they're inert otherwise.

## What removal would concretely touch

1. Delete `ont_build.py`, `ont_create.py` (1,732 lines).
2. Delete `prototypes/ont_app/` (161 files, the Angular seed).
3. Remove `app-create` / `app-build` commands from `cli.py`, and the
   `create_and_build_ontimize_app` call + `get_ontimize_apps` gate from `api_logic_server.py`
   (~6 call sites across 2 files).
4. Remove the ~13 Ontimize-specific files inside `app_model_editor/` (icons, `ontimize_api.py`,
   `docker-image-ont/`, the devcontainer/template mentions) — leaving the rest of
   `app_model_editor` untouched.
5. Remove the 4 other scattered `ontimize_api.py` copies and 2 `docker-compose-ontimize.yml`
   sample files.
6. Remove `translate` / `libretranslatepy` from `requirements.txt`.
7. Docs repo (separate `org_git/Docs` sibling, not touched by this analysis's search scope for
   editing, only for reference): retire or clearly mark-removed
   `App-Custom-Ontimize-Overview.md`, drop its `mkdocs.yml` nav entry, and update the handful of
   pages that link to it (`App-Custom.md`, `App-Model-Editor.md`,
   `Architecture-Internals-CLI.md`, `WebGenAI.md`, `Tech-Training.md`,
   `Tech-Training-WG-Dev.md`, `Eval-health_check.md`).

## Considerations

- **Nothing here is load-bearing for the rest of the framework.** The call graph is narrow and
  one-directional (framework → ontimize code, never the reverse), so removal doesn't risk
  destabilizing unrelated features.
- **It was never released as a real capability** — "Beta," "preview," "not ready for
  production," "contact us if you would like to try it" is the doc's own framing, and it's been
  stale for 2+ years. This reads as a shipped experiment that didn't get traction, not a feature
  with a live user base to consider.
- **The mainline-flow coupling is the one piece worth being careful about**, not because it's
  large, but because `create_and_build_ontimize_app` runs on every project creation today (as a
  cheap no-op scan for normal projects). Removing it is simple, but it's the one place where
  "Ontimize code" and "code every user's `create` command passes through" overlap — worth a
  quick regression pass on plain `ApiLogicServer create` after removal, even though the change
  itself is a deletion, not a logic change.
- **`app_model_editor` should NOT be conflated with Ontimize removal** — it's a general-purpose
  441-file scaffold that happens to contain a small Ontimize-specific subset. Scope any removal
  PR to just that subset; don't let "remove ont_build.py" become "also delete
  app_model_editor," which would remove unrelated functionality.
- **No test debt is retired by this removal** (there wasn't any), and no test debt is created
  (nothing currently exercises this code as passing/verified).

## Execution

Done on branch `remove-ont`. Everything removed was archived first, mirroring original repo
paths, to `/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/ontimize-archive/` (2157 files).
Nothing was committed — working tree only (2088 deletions, 75 edits).

**Scope grew well beyond this analysis.** Two decisions changed scope from what's written above:

1. **`app_model_editor` — removed in full** (441 files), not just the ~13-file Ontimize subset
   this analysis recommended (§ "Considerations" above literally warned against this). Val's
   call, recorded inline at the time: "Val's view - cut it."
2. **A second, deeper Ontimize integration layer was found during execution**, not visible to
   the original grep-based analysis because it wasn't named `ont_*` or `*ontimize*` in an
   obvious way. This analysis's "Blast radius" section (narrow, only `api_logic_server.py`/
   `cli.py`/one comment) was **wrong** — it only covered the CLI-command entry points, not the
   runtime integration baked into the base project prototype itself:
   - `api/system/custom_endpoint.py` — docstring says "Internal system services for Ontimize";
     `__init__` unconditionally imported the now-deleted `ontimize_api.py`. Entirely
     Ontimize-dependent, not general customization machinery with an Ontimize corner.
   - `api/system/expression_parser.py` — implements Ontimize's `@basic_expression`/
     `@filter_expression` advanced-filter payload format (`ONTIMIZE_OPERATORS`). Its only
     wiring into `SAFRSBaseX.py`'s `jsonapi_filter` was dead code, gated by
     `if do_enable_ont_advanced_filters := False:` (never `True`) — confirms it was already
     inert, not a live feature.
   - `api/system/gen_csv_report.py`, `gen_pdf_report.py` — both entirely dependent on
     `CustomEndpoint` and `expression_parser.parsePayload`; `gen_pdf_report.py`'s own docstring
     documents the "Ontimize Payload" shape. Neither had any caller elsewhere in the prototype.
   - `config/config.py` — `ONTIMIZE_SERVICE_TYPE`/`service_type` and (once its only consumers
     were gone) `BACKTIC_AS_QUOTE`/`backtic_as_quote`, both now fully dead.
   - `security/system/authentication.py` — two extra `@flask_app.route` decorators
     (`/ontimizeweb/services/rest/{auth,users}/login`) stacked on the same `login()` also
     serving `/api/auth/login`.
   - `api_logic_server_run.py` — `/ontimizeweb/.*` CORS resource entry.
   - `ui/admin/admin_loader.py` — a `try/except` block setting `X-Auth-Token` response header,
     comment: "required for Ontimize (kludge alert)".
   - `.vscode/launch.json` (all copies) — "Install/Start Ontimize (npm)" and "Rebuild app from
     altered model" (`als app-build`) launch configs; root Manager `.vscode/launch.json` also had
     debug configs for `app-create`/`app-build`/`app-build JSONAPI`.
   - 9 samples' `ui/app/` — the full *generated* Ontimize Angular app instances (not just
     `ontimize_api.py`/`docker-compose-ontimize.yml` as this analysis's §"Other copies" listed —
     the entire `angular.json`/`package.json`/`src/` tree, 100–260 files each).
   - Stray doc/example references: `docs/training/health_check.md` baseline-LOC table row for
     `ontimize_api.py`; `genai_demo_docs_logic/ui/admin/admin.yaml`'s `serviceType: OntimizeEE`;
     `prototypes/nw/ui/app_model_custom.yaml` (the nw sample's Ontimize app model, orphaned once
     its only consumer — the deleted `create_and_build_ontimize_app` — was gone);
     `time_tracking_billing/readme.md`'s "Add Ontimize Application" section.

   All of the above were **repeated per-project-prototype copies** (base + up to 9 samples +
   `genai_demo_docs_logic` + `mini_skel` + one test fixture), so each item above is really
   ~10 files touched, not one.

**Confirmed dead, not just unused:** the `SAFRSBaseX.py` / `expression_parser.py` advanced-filter
hook was already switched off in source (`:= False`) before this removal — i.e. some of what
this analysis called "no test coverage" was actually "no coverage because already disabled."

**Verification:** ran `genai-logic create` from source (classicmodels.sqlite), then started the
generated project's server — booted clean, rules loaded, `/api/Customer` returned real data, zero
`ontimize` matches anywhere in the generated project. Also re-ran a repo-wide
case-insensitive grep for `ontimize` afterward (excluding `build/`, `venv/`, logs, and this
analysis doc itself) — zero remaining matches in live source.

**Not touched:** the Docs repo (`org_git/Docs`, separate sibling — item 7 above, still open),
and stale runtime log/output snapshots (`logs/als.log`, test failure `.txt` fixtures) that
happen to mention Ontimize from past runs — those are historical records, not source.

## BLT verification (post-removal)

Ran the full BLT suite (`tests/build_and_test/blt.sh`, which does `python setup.py sdist
bdist_wheel` + `pip install` from this working tree, then creates and exercises several
generated projects) against the branch as described above — **passed**. Confirmed the mainline
`create`/rebuild flow (the one piece flagged in the original analysis as worth a regression
pass, since `create_and_build_ontimize_app` ran on every `create`) is unaffected by the removal.

Side effect noted as a useful confirmation the removed weight was real, not just line count:
installed venv size dropped from **493MB to 360MB (−27%)**.

## Dependency security check (separate from, but folded into, this same branch)

Trigger: a Dependabot alert on `GenAI-Logic` for
[GHSA-xrxm-cp7j-8xf6](https://github.com/advisories/GHSA-xrxm-cp7j-8xf6) (`@angular/
platform-server`, SSRF via URL-parser differential, CVSS 8.2 high). Looked this up directly
(`gh api advisories/GHSA-xrxm-cp7j-8xf6`) rather than assume: the vulnerable range is `>=
19.0.0-next.0` and up through 22.x pre-releases; the version actually pinned in the (now-deleted)
`ontimize_seed/package-lock.json` was **15.2.10**, technically outside GitHub's stated vulnerable
range. Doesn't matter for the outcome — Dependabot flags the package's mere presence in the
dependency graph, and that whole `package-lock.json` lineage (seed app + all its generated sample
copies) is now gone from source, confirmed by grep (zero `ontimize` matches in any
`package.json`/`package-lock.json` in the tree). This alert should clear once the branch reaches
the default branch and Dependabot re-scans.

Val: won't close the Dependabot alerts until a re-release happens with some testing first — this
section is the record of what was checked in the meantime, not a claim that GitHub's alert list
is already clear.

**Broader dependency scan run while at it** (not Ontimize-specific, but same branch/session):
- `pip-audit` against the installed venv (post-BLT-install): clean. Only `pip` itself had listed
  advisories (PYSEC-2026-196/1795/1796/2875/2876), all fixed by a `pip` upgrade — no
  vulnerabilities in any actual framework runtime dependency (Flask, SQLAlchemy, LogicBank, etc).
- `npm audit` against every `package-lock.json` remaining in the source tree. First pass only
  covered 5 copies of the React admin template (`prototypes/basic_demo/ui/my-react-app{,-cards}`,
  `prototypes/basic_demo/customizations/ui/reference_react_app`,
  `prototypes/nw/ui/reference_react_app`,
  `prototypes/manager/system/genai/app_templates/react-admin-template`) — missed that the same
  template is also replicated into 3 more samples
  (`basic_demo_ai_rules-supplier`, `basic_demo_logic_gov`, `basic_demo_sample`, 3 lockfile copies
  each = 9 more), caught on a follow-up "check the whole repo" pass rather than the first one.
  **14 of 15 total lockfiles in the tree started at 59 advisories each (3 critical, 29 high, 14
  moderate, 13 low)** — stale transitive deps under the `react-scripts`/CRA toolchain
  (`form-data`, `shell-quote`, `websocket-driver` were the 3 critical each time).
  `internal_dev/react-admin/package-lock.json` was the only one already clean, confirming this
  was specifically the CRA-template copies that had drifted.

  Fixed with plain `npm audit fix` (no `--force`) on all 14 affected copies: **59 → 32 advisories
  each, 0 critical** (all three cleared, every copy). `package.json` came out byte-identical in
  every copy — only `package-lock.json` moved to compatible transitive versions, no direct
  dependency bumps, no application code touched. Verified every one of the 14 rebuilds
  successfully (`npm install && npm run build` → "The build folder is ready to be deployed")
  before and after the fix, so this isn't just "advisory count went down," it's confirmed
  non-breaking. Final repo-wide re-scan after both passes: **all 15 package-lock.json files in
  the tree show `critical: 0`.**

  Remaining 32 advisories per lockfile all require `npm audit fix --force`, which attempted to
  downgrade `react-scripts` to `0.0.0` (npm's resolver giving up, not a real version) — declined
  to pursue; this is deep dev/build-tooling risk (webpack-dev-server, workbox), not code shipped
  to end users in a deployed app, and forcing it risked breaking the build for marginal gain.
  Left as known/accepted residual for now.
