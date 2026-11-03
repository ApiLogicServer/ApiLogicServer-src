# Project Creation Report

This project was created by `genai-logic create`.

- **Project name:** demo_eai_modernized
- **Database:** `sqlite:///samples/dbs/basic_demo.sqlite`
- **Created:** October 27, 2026 21:48:53

## Scaffold

Every project starts from a scaffold - the template `create` clones and customizes.
This project's scaffold:

- **Base template:** `/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/venv/lib/python3.13/site-packages/api_logic_server_cli/prototypes/base` (always the foundation - every project starts here)
- **Overlay:** none - this project is the unmodified base template
- **Overlay (Project Context Engineering):** `/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/system/project_context_engineering` (training file additions/overrides copied into `docs/training/` - see this project's `docs/training/$readme.md` for the exact overlay timestamp/version)

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

- [demo_eai](demo_eai/ad-libs.md) — modernized EAI demo: credit rules, order_shipping publish, order_b2b consume + REST, Keycloak RLS, REST contract guard; live Kafka not verified, 2026-10-27

## CE/Training Files Read

Files loaded during this run (approximate sizes where known):

- `.github/copilot-instructions.md` (project CE, ~217 KB) — read by section: Verify Message Subscriptions, Run Tests, Logic Diagram, Executable Requirements, Security, B2B API pattern, EAI publish step
- `docs/training/eai_subscribe.md` (~46 KB) — read in full
- `docs/training/implement_requirements.md` (~67 KB) — head, ad-libs template and linking rule
- `docs/training/security.md` (~10 KB) — read in full
- `docs/training/testing.md` (~52 KB) — Running Tests, Step 1c/1d, Rules #0/#5/#6, logic-log section
- Not read: `logic_bank_api.md`, `logic_bank_patterns.md`, `RequestObjectPattern.md`
