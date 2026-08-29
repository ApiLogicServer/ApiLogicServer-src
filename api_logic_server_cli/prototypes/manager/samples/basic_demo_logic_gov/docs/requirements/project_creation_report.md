# Project Creation Report

This project was created via Manager Method 4 (System Creation Services), then implemented
from the domain prompt in `project_creation_prompt.md`.

- **Project name:** basic_demo_logic_gov
- **Database:** `sqlite:///samples/dbs/starter.sqlite`
- **Created:** 2026-05-23
- **Method:** Method 4 (System Creation Services) — Manager workspace, stay-in-Manager flow
- **Source prompt:** `samples/prompts/genai_demo.prompt`

## Domain Implementation

- **Schema:**

  | Table | Purpose |
  |---|---|
  | `customer` | Customer with `balance` (derived) and `credit_limit` |
  | `product` | Product catalog with `unit_price` |
  | `order` | Order header with `amount_total` (derived), `date_shipped`, `notes` |
  | `item` | Line item with `unit_price` (copy) and `amount` (derived) |
  | `sys_config` | System configuration (from starter.sqlite — retained as pattern) |

- **Logic:**

  ```
  logic/logic_discovery/place_order/
    __init__.py
    check_credit.py    — 5 rules: 2 sum, 1 formula, 1 copy, 1 constraint
  logic/logic_discovery/
    app_integration.py — 1 rule: after_flush_row_event (Kafka publish)
  ```

- **Seed data:** 3 products, 2 customers, 3 orders, 4 items — loaded via
  `database/test_data/alp_init.py`. All derived fields computed correctly by LogicBank on
  insert.

## Next steps

See `project_creation_prompt.md` in this folder for the verbatim originating prompt.

You can still add business logic at any time — say **"implement requirements"** (or
"impl req") to an AI assistant, or write rules directly in `logic/logic_discovery/`.

## Use Cases

- [check_credit](check_credit/requirements.md)
- [app_integration](app_integration/requirements.md)

## XRD Workflow (for future use)

Place Executable Requirements sets here, then say **"implement reqs"** to AI.

**Phase 1** (done — in Manager): `genai-logic create` → running API + Admin UI
**Phase 2** (here): copy a requirements set, say "implement reqs" → AI executes spec, reports ad-libs
