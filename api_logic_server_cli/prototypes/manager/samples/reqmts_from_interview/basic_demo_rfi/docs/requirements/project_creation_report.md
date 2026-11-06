# Project Creation Report

This project was created by `genai-logic create`.

- **Project name:** basic_demo_rfi
- **Database:** `sqlite:///samples/dbs/starter.sqlite`
- **Created:** November 05, 2026 21:12:41

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

- [basic_demo_rfi](ad-libs.md) — check credit + green-product discount + order_shipping publish, 2026-11-05

## Method 4 provenance (Manager STEP 5)

- **Source prompt:** pasted into the AI assistant, preserved verbatim in [project_creation_prompt.md](project_creation_prompt.md). It contained an interview clause (STEP 1b); the Q&A is in [basic_demo_rfi-transcript.md](basic_demo_rfi-transcript.md).
- **Date / model:** 2026-11-05, claude-sonnet-5-5.
- **Commands:** `genai-logic create --project-name=basic_demo_rfi --db_url=sqlite:///samples/dbs/starter.sqlite`; DDL via `sqlite3`; `genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite`; seed via `database/test_data/alp_init.py`.
- **Schema decisions:** `sys_config.green_discount_pct` (global flat percentage); `product.green` (TEXT flag); `item.green` (snapshot) and `item.discount_amount` (derived); `item.amount` extended by the discount (interview option A); money columns `DECIMAL(15,2)`.
- **Use-case requirements:** [check_credit](check_credit/requirements.md), [green_discount](green_discount/requirements.md), [app_integration](app_integration/requirements.md).
- **Judgment calls:** see [ad-libs.md](ad-libs.md).

## CE/Training Files Read

In order: `.github/rfi_transcript_format.md` (right after project creation, before the interview); project `.github/copilot-instructions.md` (via `CLAUDE.md`) and `docs/training/logic_bank_api.md` (loaded with the project); `docs/training/implement_requirements.md`; `docs/training/logic_bank_patterns.md` (first 400 of 788 lines). Not read: `RequestObjectPattern.md` (no integration service with a returned result), `eai_subscribe.md` (no inbound consume), `allocate.md`, `testing.md`.
