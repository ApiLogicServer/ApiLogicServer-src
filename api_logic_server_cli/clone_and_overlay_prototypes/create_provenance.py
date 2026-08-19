"""
create_provenance() - writes the baseline docs/requirements/ files for every
genai-logic create, regardless of method (existing db, new db, --from_git).

This is the CLI-guaranteed floor: works with zero AI involved. When an AI
assistant later runs "impl req" against this project, it enriches these same
files (real prompt text) and adds one docs/requirements/<use_case>/ad-libs.md
per use case implemented - each linked from project_creation_report.md's
"Use Cases" section (see docs/training/implement_requirements.md STEP 7) -
rather than replacing this file.

Called from create_project_and_overlay_prototypes() in project_overlay.py,
right after create_readme.create_readme() (same call site, every method).
"""

import datetime
import logging
from pathlib import Path

log = logging.getLogger('create_from_model.model_creation_services')


def _scaffold_source_lines(project, api_logic_server_dir_str: str) -> str:
    """ describes where the project's scaffold came from - base, --from_git overlay,
        and Project Context Engineering overlay, if used """
    base_dir = Path(api_logic_server_dir_str).joinpath('prototypes/base')
    lines = [f"- **Base template:** `{base_dir}` (always the foundation - every project starts here)"]
    if project.from_git:
        lines.append(f"- **Overlay (`--from_git`):** `{project.from_git}` "
                      f"(your files, applied on top of base - same mechanism as the built-in "
                      f"nw/allocation/BudgetApp sample overlays)")
    else:
        lines.append("- **Overlay:** none - this project is the unmodified base template")
    pce_source_dir = Path.cwd() / 'system' / 'project_context_engineering'
    if pce_source_dir.is_dir() and any(pce_source_dir.iterdir()):
        lines.append(f"- **Overlay (Project Context Engineering):** `{pce_source_dir}` "
                      f"(training file additions/overrides copied into `docs/training/` - see "
                      f"this project's `docs/training/$readme.md` for the exact overlay "
                      f"timestamp/version)")
    return "\n".join(lines)


def _inferred_prompt(project) -> str:
    """ Methods 1/3 (no impl req prompt exists) - a short, framework-authored description
        of what was effectively requested, derived from data already in hand at create time.
    """
    lines = [
        f"Create a project providing an admin app and JSON:API for database `{project.db_url}`."
    ]
    if project.from_git:
        lines.append(f"\nScaffold overlay requested via `--from_git={project.from_git}`.")
    return "\n".join(lines)


def create_provenance(project, api_logic_server_dir_str: str):
    """
    Writes docs/requirements/project_creation_prompt.md and docs/requirements/project_creation_report.md
    for every created project (all methods) - the baseline provenance record.

    Does NOT overwrite project_creation_prompt.md if it already exists (e.g. Method 4 has already
    copied the real originating prompt verbatim before this runs) - the CLI floor
    only fills in what's missing, never clobbers a real prompt with an inferred one.

    Does NOT touch project_creation_report.md if it already exists - once an AI
    assistant has appended Use Cases entries (see implement_requirements.md STEP 7),
    this CLI writer must never re-run and wipe them (e.g. on a rebuild-from-database call).
    """
    requirements_dir = project.project_directory_path.joinpath('docs/requirements')
    requirements_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = requirements_dir.joinpath('project_creation_prompt.md')
    if not prompt_path.exists():
        log.debug(f".. ..Writing inferred {prompt_path}")
        prompt_path.write_text(_inferred_prompt(project) + "\n")

    report_path = requirements_dir.joinpath('project_creation_report.md')
    if report_path.exists():
        log.debug(f".. ..{report_path} already exists, not overwriting")
        return

    scaffold_section = _scaffold_source_lines(project, api_logic_server_dir_str)
    created_date = str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S"))

    report_content = f"""# Project Creation Report

This project was created by `genai-logic create`.

- **Project name:** {project.project_name_last_node}
- **Database:** `{project.db_url}`
- **Created:** {created_date}

## Scaffold

Every project starts from a scaffold - the template `create` clones and customizes.
This project's scaffold:

{scaffold_section}

The scaffold provides, out of the box:

* SQLAlchemy ORM models
* Admin Web App
* JSON:API endpoints, MCP Support, and Swagger docs
* LogicBank rules engine
* Framework wiring for security/RBAC, Kafka Message Integration, and AI Rules

See this project's root readme (`readme.md`, or `readme_standard.md` for
demo-named projects where a demo-specific readme replaces it) for what was
actually generated.

The scaffold is extensible: `--from_git=<git-url-or-directory>` overlays your own files
on top of base at creation time - see
[github.com/ApiLogicServer/scaffold-sample](https://github.com/ApiLogicServer/scaffold-sample)
for a minimal example you can clone and extend.

## Next steps

See `project_creation_prompt.md` in this folder for what was requested (inferred from
the create command, unless a real requirements prompt was supplied).

You can still add business logic at any time - say **"implement requirements"** (or
"impl req") to an AI assistant, or write rules directly in `logic/logic_discovery/`.

## Use Cases

*(each `impl req` run appends a link here to its `docs/requirements/<use_case>/ad-libs.md`)*
"""
    log.debug(f".. ..Writing {report_path}")
    report_path.write_text(report_content)
