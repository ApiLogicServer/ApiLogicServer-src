# basic_demo — Project Provenance

**Created:** 2026-05-23  
**Method:** Method 4 (System Creation Services) — Manager workspace, stay-in-Manager flow  
**Source prompt:** `samples/prompts/genai_demo.prompt`

## Prompt (verbatim)

```
Create a system with customers, orders, items and products.

Include a notes field for orders.

On Placing Orders, Check Credit    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' if the date_shipped is not None.
```

## Tables Created

| Table | Purpose |
|---|---|
| `customer` | Customer with `balance` (derived) and `credit_limit` |
| `product` | Product catalog with `unit_price` |
| `order` | Order header with `amount_total` (derived), `date_shipped`, `notes` |
| `item` | Line item with `unit_price` (copy) and `amount` (derived) |
| `sys_config` | System configuration (from starter.sqlite — retained as pattern) |

## Logic Files

```
logic/logic_discovery/place_order/
  __init__.py
  check_credit.py    — 5 rules: 2 sum, 1 formula, 1 copy, 1 constraint
  app_integration.py — 1 rule: after_flush_row_event (Kafka publish)
```

## Seed Data

3 products, 2 customers, 3 orders, 4 items — loaded via `database/test_data/alp_init.py`.
All derived fields computed correctly by LogicBank on insert.

---

## XRD Workflow (for future use)

Place Executable Requirements sets here, then say **"implement reqs"** to AI.

**Phase 1** (done — in Manager): `genai-logic create` → running API + Admin UI  
**Phase 2** (here): copy a requirements set, say "implement reqs" → AI executes spec, reports ad-libs
