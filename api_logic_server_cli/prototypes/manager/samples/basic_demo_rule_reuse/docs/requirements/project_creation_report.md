# Project Creation Report

This project was created by `genai-logic create`.

- **Project name:** basic_demo_rule_reuse
- **Database:** `sqlite:///samples/dbs/basic_demo.sqlite`
- **Created:** November 22, 2026 08:49:56

## Scaffold

Every project starts from a scaffold - the template `create` clones and customizes.
This project's scaffold:

- **Base template:** `/Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/venv/lib/python3.13/site-packages/api_logic_server_cli/prototypes/base` (always the foundation - every project starts here)
- **Overlay:** none - this project is the unmodified base template
- **Overlay (Project Context Engineering):** `/Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/system/project_context_engineering` (training file additions/overrides copied into `docs/training/` - see this project's `docs/training/$readme.md` for the exact overlay timestamp/version)

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
- [basic_demo_rule_reuse](basic_demo_rule_reuse/ad-libs.md) — Check Credit, App Integration (Kafka), Move Order credit check (reuses existing rules, no new rule), 2026-11-22

## Build Details (AI assistant)

- **Source prompt:** `samples/prompts/basic_demo_rule_reuse.prompt` (pasted), copied verbatim to `project_creation_prompt.md`
- **Date / model:** 2026-11-22, claude-opus-5-5 (Claude Code)
- **Creation commands:** `genai-logic create --project_name=basic_demo_rule_reuse --db_url=sqlite:///samples/dbs/basic_demo.sqlite` (Method 1: existing database)
- **Schema decisions:** none — `Order.notes` and every derived column already exist; no DDL, no rebuild.
- **Logic:** `logic/logic_discovery/place_order/check_credit.py`, `place_order/app_integration.py`, `move_order/check_credit.py` (placeholder: `Uses:` only)

### CE/Training Files Read
1. `.github/copilot-instructions.md` (Manager) — session start
2. `.github/copilot-instructions.md` (project) — Executable Requirements section only, ~45 KB of ~250 KB
3. `docs/training/logic_bank_api.md` — loaded via project CLAUDE.md, ~113 KB
4. `docs/training/implement_requirements.md` — ad-libs template section only
