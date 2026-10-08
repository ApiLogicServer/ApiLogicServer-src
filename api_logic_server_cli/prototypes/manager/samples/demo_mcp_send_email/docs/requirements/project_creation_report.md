# Project Creation Report

This project was created by `genai-logic create`, then implemented end-to-end from
`samples/prompts/demo_mcp_send_email.prompt.md` via Method 4 (System Creation Services).

- **Project name:** demo_mcp_send_email
- **Database:** `sqlite:///samples/dbs/basic_demo.sqlite`
- **Created:** October 08, 2026 07:41:00
- **Requirements implemented:** October 08, 2026
- **Model:** claude-sonnet-5 (valjhuber@gmail.com)
- **Source prompt:** `samples/prompts/demo_mcp_send_email.prompt.md` — see `project_creation_prompt.md` (verbatim copy)

## Creation Steps

```bash
genai-logic create --project-name=demo_mcp_send_email --db_url=sqlite:///samples/dbs/basic_demo.sqlite
sqlite3 database/db.sqlite "CREATE TABLE sys_email (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL, subject VARCHAR, message VARCHAR, CreatedOn DATE, FOREIGN KEY(customer_id) REFERENCES customer(id));"
genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite
# admin.yaml replaced from admin-merge.yaml (user confirmed)
genai-logic genai-add-mcp-client
```

## Schema Decisions

- Reused `basic_demo.sqlite`'s existing Customer/Order/Item/Product schema unchanged for Check Credit — all referenced columns (`balance`, `credit_limit`, `date_shipped`, `amount_total`, `quantity`, `unit_price`) already existed.
- Added one new table, `sys_email` (child of `customer`), exactly as specified — fire-and-forget pattern, no Request Pattern response/audit columns needed since the caller doesn't read a result back.
- MCP client (`SysMcp`) added via the project's own `genai-logic genai-add-mcp-client` command — a separate `mcp`-bind-key database, generated logic file, and Admin UI entry; no custom schema or rules authored for this section.

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

- [check_credit](check_credit/requirements.md) — balance/credit-limit constraint + sum/formula/copy chain, 2026-10-08
- [send_email](send_email/requirements.md) — SysEmail fire-and-forget event, opt-out check, 2026-10-08
- [mcp_client](mcp_client/requirements.md) — SysMcp natural-language request via `genai-logic genai-add-mcp-client`, 2026-10-08
- [ad-libs](ad-libs.md) — full pre-coding analysis and verification detail for this build, 2026-10-08

## CE/Training Files Read

In order, this build session:
1. `.github/copilot-instructions.md` (project CE) — read at STEP 3
2. `docs/training/logic_bank_api.md` — read at STEP 3
3. `docs/training/implement_requirements.md` — read at STEP 3
4. `docs/training/logic_bank_patterns.md` — read at STEP 3
5. `docs/training/RequestObjectPattern.md` — read at STEP 3
6. `integration/mcp/readme-mcp.md`, `docs/training/MCP_Copilot_Integration.md` — read before implementing the MCP client section
7. Generic (non-sample) CLI source: `api_logic_server_cli/cli.py`, `genai/genai_mcp.py`, `templates/mcp_client_executor_request.py`, `fragments/mcp_admin.yml` — read to confirm `genai-add-mcp-client` was the correct, documented mechanism before running it
