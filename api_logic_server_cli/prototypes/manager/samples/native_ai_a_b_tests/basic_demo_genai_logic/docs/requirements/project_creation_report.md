# Project Creation Report

This project was created by `genai-logic create`, following the Manager CE's Method 4
(System Creation Services) workflow.

- **Project name:** basic_demo_genai_logic
- **Database:** `sqlite:///samples/dbs/basic_demo.sqlite` (pre-existing schema + seed data —
  user named this database explicitly; no DDL changes were needed, since `basic_demo.sqlite`
  already contains the exact columns the requirement needs: `customer.balance`,
  `customer.credit_limit`, `order.amount_total`, `item.amount`, `item.unit_price`,
  `item.quantity`, `product.unit_price`)
- **Created:** September 21, 2026 17:36:52
- **Model:** claude-sonnet-5 (valjhuber@gmail.com)

## Creation Steps

1. `genai-logic create --project-name=basic_demo_genai_logic --db_url=sqlite:///samples/dbs/basic_demo.sqlite`
2. Read project CE (`.github/copilot-instructions.md`) and `docs/training/logic_bank_api.md` (via CLAUDE.md `@` includes)
3. Wrote `logic/logic_discovery/place_order/check_credit.py` (5 rules — see Use Cases below)
4. Backfilled pre-existing `customer.balance` rows via one-time SQL, since the seed data's
   balances reflected an unrelated prior formula (unshipped-orders-only) rather than this
   project's rule (sum of all orders) — see `docs/requirements/check_credit/ad-libs.md`
5. Started the server (`python api_logic_server_run.py --port=5657`, since the default 5656
   was occupied by an unrelated, pre-existing local process) and verified live:
   - a valid order (Diana, product Widget x2) correctly derived Item.amount → Order.amount_total → Customer.balance
   - an over-limit order (Silent, product Thingamajig x1) was correctly rejected with the constraint's error message, and left no partial state behind
   - test rows were deleted afterward and `customer.balance` re-backfilled to the clean seed state

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

- **check_credit** — order-entry credit check. See
  [`docs/requirements/check_credit/requirements.md`](check_credit/requirements.md) and
  [`docs/requirements/check_credit/ad-libs.md`](check_credit/ad-libs.md).
  Rules in `logic/logic_discovery/place_order/check_credit.py`:
  `Item.unit_price` (copy from `Product.unit_price`), `Item.amount` (formula:
  `quantity * unit_price`), `Order.amount_total` (sum of `Item.amount`),
  `Customer.balance` (sum of `Order.amount_total`), and a constraint rejecting
  `Customer.balance > Customer.credit_limit`.

*(each `impl req` run appends a link here to its `docs/requirements/<use_case>/ad-libs.md`)*

## CE/Training Files Read

- `.github/copilot-instructions.md` (project CE) — read at STEP 3, ~68 KB (Manager CE + project CE concatenated via file)
- `docs/training/logic_bank_api.md` — read at STEP 3 (via CLAUDE.md `@` include)
- `database/models.py` — read at STEP 4, to confirm existing schema matched the requirement before writing rules (no DDL needed)
