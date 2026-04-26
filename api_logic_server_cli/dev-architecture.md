# api_logic_server_cli — Developer Architecture

Internal reference for developers and AI assistants working on framework internals.

---

## Project Creation: How It Works

Entry point: `api_logic_server.py` → `create_project_and_overlay_prototypes()` (now delegated to `clone_and_overlay_prototypes/project_overlay.py`).

**Pattern: base clone + conditional overlays**

1. **Clone `prototypes/base`** → new project directory (`shutil.copytree`)  
   Every project gets this — it contains the universal foundation: api/, logic/, database/, .github/.copilot-instructions.md, docs/training/, .vscode/, devops/, etc.

2. **Overlay sample-specific prototypes** (`recursive_overwrite` on top of base):

   | Condition | Prototype overlaid |
   |---|---|
   | `nw_db_status == "nw+"` | `prototypes/nw_plus` |
   | `nw_db_status == "nw-"` | `prototypes/nw_no_cust` |
   | `db_url == "allocation"` | `prototypes/allocation` |
   | `db_url == "BudgetApp"` | `prototypes/BudgetApp` |
   | `db_url in shipping` | `prototypes/shipping` |
   | `oracle in db_url` | `prototypes/oracle` |
   | `sqlite in db_url` | `prototypes/sqlite` |
   | `is_genai_demo` | `prototypes/genai_demo` |
   | classicmodels url | `prototypes/classicmodels` |
   | postgres url | `prototypes/postgres` |

3. **README routing** via `clone_and_overlay_prototypes/create_readme.py`:
   - Reads front-matter from `Docs/docs/Manager-readme.md` (fetched from GitHub, falls back to local)
   - Front-matter maps demo name → Docs source file, e.g. `demo_eai: Sample-Basic-EAI`
   - Sorted longest-first to avoid prefix collisions (`basic_demo_mcp` before `basic_demo`)
   - Calls `copy_md()` to fetch the source `.md` from the Docs repo, scrub mkdocs-specific syntax, and write as `readme.md` in the new project
   - Also overlays `prototypes/demo_eai` and `prototypes/basic_demo` when project name matches

   **Why scrubbing is needed — mkdocs vs standard markdown:**  
   The Docs repo is a [MkDocs](https://www.mkdocs.org/) site. Its `.md` files use syntax that renders correctly on the docs site but breaks in VS Code / GitHub:

   | mkdocs syntax | scrubbed to |
   |---|---|
   | Relative image paths `images/foo.png` | Absolute GitHub raw URLs `https://raw.githubusercontent.com/.../foo.png` |
   | Admonitions `!!! note "Title"` / `!!! pied-piper` | `>` blockquotes or plain text |
   | Link attributes `[text](url){:target="_blank"}` | `[text](url)` (attribute stripped) |

   `copy_md()` in `create_from_model/api_logic_server_utils.py` handles all three transformations.  
   **Edit rule:** Always make README changes in `org_git/Docs/docs/` using mkdocs syntax — never edit a generated `readme.md` directly, it is overwritten on every project creation.

4. **SQLite db copy** — strips `sqlite:///` prefix, copies db file to `database/db.sqlite`, writes relative URI `sqlite:///{db_path}` into `config/config.py`

5. **String substitutions** — replaces placeholders in `readme.md`, `config/config.py`, `alembic.ini`, `opt_locking.py`: version, creation date, db url, api name, template path, etc.

---

## clone_and_overlay_prototypes/ — What Each File Does

| File | Purpose |
|---|---|
| `project_overlay.py` | `create_project_and_overlay_prototypes()` — extracted from `api_logic_server.py` for maintainability. The full implementation lives here; `api_logic_server.py` has a 4-line stub. |
| `create_readme.py` | README routing: reads Manager-readme.md front-matter from GitHub/local Docs, maps demo name → readme doc, calls `copy_md()`. Also overlays basic_demo and demo_eai prototypes. |
| `add_cust.py` | Two roles: (1) `add-cust` tutor utility — copies pre-built customizations into basic_demo during guided tour; (2) `add-auth` support — called from `cli.py` and `genai.py`. |

**Circular import avoidance:** `project_overlay.py` imports from `api_logic_server.py` (utilities like `delete_dir`, `recursive_overwrite`, `__version__`) using local imports *inside* the function, not at module load time.

---

## Manager Workspace: How `als start` Works

Entry point: `cli.py` → `create_manager()` in `manager.py`.

**Key behavior — existing manager short-circuit:**

```python
if to_dir_check.exists() and not clean:   # .vscode already exists → manager exists
    manager_exists = True
    # ONLY refreshes .env — copytree is NOT run
else:
    shutil.copytree(src=from_dir_proto_mgr, dst=to_dir, dirs_exist_ok=True)
```

**Implication:** On a normal BLT re-run, the manager workspace is considered "existing" (`.vscode` is present) and `copytree` is **skipped**. Files added to `prototypes/manager/` (including `.claude/settings.json`) are **only copied on a clean/first install**.

**Workaround for existing installs:** After updating `prototypes/manager/.claude/settings.json`, manually copy it to the live BLT manager workspace. BLT will not do it automatically unless run with `--clean`.

---

## Key Files to Edit for Common Tasks

| Task | File to edit |
|---|---|
| New sample type / prototype overlay | `clone_and_overlay_prototypes/project_overlay.py` |
| New demo readme mapping | `Docs/docs/Manager-readme.md` front-matter (gold: Docs repo) |
| Manager workspace defaults (`.claude/`, `.vscode/`, etc.) | `prototypes/manager/` (takes effect on clean install only — see above) |
| Project CE / copilot instructions | `prototypes/base/.github/.copilot-instructions.md` |
| basic_demo-specific CE | `prototypes/basic_demo/.github/.copilot-instructions.md` |
| Training materials (all projects) | `prototypes/base/docs/training/` |
| add-cust tutor content | `prototypes/manager/samples/basic_demo_sample/` |

---

## venv vs Gold Source

- **Edit in venv** for fast iteration — changes take effect immediately with no BLT required  
  Path: `build_and_test/genai-logic/venv/lib/python3.13/site-packages/api_logic_server_cli/`
- **Propagate to gold source** before running BLT — venv is wiped on reinstall  
  Path: `org_git/ApiLogicServer-src/api_logic_server_cli/`
- **Always sync both** when making changes: edit gold source → copy to venv (or vice versa)
