This is the Project Context Engineering.  It directs AI to create *rules not code*, as well as a (large) number of generation directives (EAI, test creation, etc.)

It is created by the base scaffold, and can be extended by overlays in the manager or github.

Any file placed in this directory (`system/project_context_engineering/`, at the Manager root)
is copied into every newly created project's `docs/training/` — training file additions or
overrides, applied on top of `prototypes/base` and any `--from_git` overlay. Same overlay
mechanism as `--from_git`, but unconditional (no CLI flag needed), sourced from the Manager
checkout rather than the pip-installed package, and scoped to `docs/training/` rather than the
whole project. This means a CE-only tweak here reaches new projects via a Manager sync
(`create_codespaces_mgr.py --push`/`--release`) without requiring a Docker image rebuild+push.
See `project_overlay.py`'s `create_project_and_overlay_prototypes()` for the implementation.

When applied, the overlay appends a timestamped note to the *new project's own* copy of this
file (`docs/training/$readme.md`, below this line) recording the overlay source, genai-logic
version, and when it happened — so a project's actual CE provenance is always inspectable from
the project itself, not just from this source file. Also recorded in that project's
`docs/requirements/project_creation_report.md`.
