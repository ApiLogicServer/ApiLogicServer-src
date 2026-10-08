# Project Creation Report

This project was created via Manager CE Method 4 (System Creation Services), from the
business prompt at `samples/prompts/demo_mcp_send_email.prompt.md` — see
`project_creation_prompt.md` for the verbatim text.

- **Project name:** demo_mcp_send_email
- **Database:** `sqlite:///samples/dbs/basic_demo.sqlite` (named explicitly in the prompt —
  already has the Customer/Order/Item/Product schema the Check Credit clause needs)
- **Created:** October 07, 2026 18:42:19
- **Model:** claude-sonnet-5 (valjhuber@gmail.com)

## Creation commands

```bash
genai-logic create --project-name=demo_mcp_send_email --db_url=sqlite:///samples/dbs/basic_demo.sqlite
sqlite3 demo_mcp_send_email/database/db.sqlite "CREATE TABLE sys_email (id, customer_id FK, subject, message, CreatedOn)"
genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite
genai-logic genai-add-mcp-client
```

## Schema decisions

- No `SysConfig`/`sys_config` table — project created from `basic_demo.sqlite`, not
  `starter.sqlite`, per the prompt's explicit db_url; no rate/threshold constants appeared in
  the prompt to warrant one.
- `SysEmail(id, customer_id FK → customer, subject, message, CreatedOn)` — child of Customer,
  per the prompt. `Customer.email_opt_out` already existed in `basic_demo.sqlite`.
- `SysMcp` table and Admin UI wiring added via `genai-logic genai-add-mcp-client` (not manual
  DDL) — generates its own bound mini-database (`database/mcp_db.sqlite`) and the generic
  `integration/mcp/mcp_client_executor.py` / `logic/logic_discovery/mcp_client_executor_request.py`.

See `docs/requirements/ad-libs.md` for every assumption made beyond the literal prompt, and
`docs/requirements/check_credit/requirements.md` / `docs/requirements/send_email/requirements.md`
for the per-use-case verbatim excerpts.

## CE/Training Files Read

- `.github/copilot-instructions.md` — project CE, read at STEP 3 (full file, ~3300 lines)
- `docs/training/logic_bank_api.md` — read at STEP 3 (auto-loaded via project `CLAUDE.md` @-include)
- `docs/training/implement_requirements.md` — referenced for schema/naming conventions (System
  Creation Services workflow section, within the project CE itself)

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

- [check_credit](check_credit/requirements.md) — balance/credit-limit constraint + sum/formula/copy cascade
- [send_email](send_email/requirements.md) — SysEmail child table + commit event, opt-out aware

See [ad-libs.md](ad-libs.md) for assumptions made and live verification performed.

*(each `impl req` run appends a link here to its `docs/requirements/<use_case>/ad-libs.md`)*
