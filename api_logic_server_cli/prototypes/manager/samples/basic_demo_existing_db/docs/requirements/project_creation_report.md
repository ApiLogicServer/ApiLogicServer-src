# Project Creation Report

This project was created by `genai-logic create`, then implemented end-to-end (Method 4,
System Creation Services) from `samples/prompts/basic_demo_existing_db.prompt` — the
"existing database" variant of `samples/prompts/basic_demo_new_db.prompt`, using the
already-populated `samples/dbs/basic_demo.sqlite` instead of building the schema from DDL.

- **Project name:** basic_demo_existing_db
- **Database:** `sqlite:///samples/dbs/basic_demo.sqlite`
- **Created:** September 19, 2026 11:09:54
- **Requirements implemented:** September 19, 2026, by claude-sonnet-5 (valjhuber@gmail.com)
- **Source prompt:** `samples/prompts/basic_demo_existing_db.prompt` (see `project_creation_prompt.md`, copied verbatim)

## Creation Steps

1. `genai-logic create --project-name=basic_demo_existing_db --db_url=sqlite:///samples/dbs/basic_demo.sqlite`
2. Inspected existing schema (`sqlite3 database/db.sqlite ".schema"`) — customer, order, item,
   product tables and columns already matched the prompt's requirements; no DDL/rebuild needed
   (existing-db path — unlike the new-db prompt, which builds schema from scratch).
3. Wrote `logic/logic_discovery/place_order/check_credit.py` (Rule.sum, Rule.formula, Rule.copy,
   Rule.constraint — 5 rules per prompt clauses 1-5)
4. Wrote `logic/logic_discovery/app_integration.py` (Rule.after_flush_row_event — Kafka publish
   to `order_shipping` on date_shipped transition to not-None)
5. Wrote per-use-case `docs/requirements/check_credit/requirements.md` and
   `docs/requirements/app_integration/requirements.md` (verbatim prompt excerpts)
6. Existing seed data in `samples/dbs/basic_demo.sqlite` was left as-is (already had sample
   rows — no seeding step run, per project CE guidance for existing-db creation)
7. Started server (`python api_logic_server_run.py`), confirmed clean startup, no rule-load
   errors
8. Verified end-to-end via API: inserted a test Order + Item for Customer "Alice" — confirmed
   unit_price copied from Product, Item.amount = quantity * unit_price, Order.amount_total
   summed correctly, Customer.balance adjusted (90.0 -> 390.0); shipped the order
   (date_shipped set) — confirmed Kafka publish fired exactly once (order_shipping topic,
   Kafka fallback mode since KAFKA_SERVER not configured) and Customer.balance reverted to
   90.0 (shipped orders excluded from the balance sum). Test Order/Item deleted afterward to
   restore original seed data.

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

- [check_credit](check_credit/requirements.md) — Check Credit rules (5 rules: sum, formula, copy, constraint)
- [app_integration](app_integration/requirements.md) — Kafka publish to `order_shipping` on shipment

## CE/Training Files Read

- Manager CE: `.github/.copilot-instructions.md` (Manager root) — read at session start
- Project CE: `basic_demo_existing_db/.github/.copilot-instructions.md` — read at STEP 3, full file
- `basic_demo_existing_db/docs/training/logic_bank_api.md` — read at STEP 3, ~31 KB (partial —
  first ~1028 lines of ~1508 total; contained the Rule.* API reference and examples needed)
