# Removing Ontimize Support — Analysis

**Status:** Analysis only — no code changes made. Written to inform a decision, not to record one.

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
