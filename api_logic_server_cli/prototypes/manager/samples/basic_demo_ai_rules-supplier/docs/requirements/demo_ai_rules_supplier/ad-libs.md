# Ad-libs: demo_ai_rules_supplier

**Headline: 2 items need review (🔴), 5 FYI (🟡).**

## 🔴 Review Required
| # | Judgment call | Action |
|---|---|---|
| 1 | (Updated: re-run with an OpenAI key; the live AI call chose Sheets for Less of NJ, fallback_used false, and the tests then ran with live AI calls.) The first build ran with no LLM, so its AI calls used the minimum-cost fallback (`fallback_used = true`). The prompt, validation and audit are in place but were never exercised against a live model. | Set `APILOGICSERVER_LLM_BASE_URL` / `_MODEL` / `_API_KEY` and re-run the server; no code change. |
| 2 | Kafka was simulated (no `KAFKA_SERVER`): the publish is verified from the logic log only, not delivered to a broker. Docker was running but the script did not say to start Kafka. | Set `KAFKA_SERVER` in config/default.env and restart to publish live. |

## 🟡 FYI
| # | Judgment call |
|---|---|
| 1 | "If the date_shipped is not None" read as publish once, when date_shipped becomes set or changes (not on every later edit of a shipped order). The message carries the primary key only (no mapper). |
| 2 | A product with no suppliers copies `Product.unit_price` to `Item.unit_price` (the requirement is silent). Only Egyptian Cotton Sheets has suppliers in this database. |
| 3 | "balance is less than the credit limit" implemented as `<=` (the standing boundary convention). |
| 4 | Created table `sys_supplier_req` (audit: request, reason, created_on, fallback_used, item_id, product_id, chosen_supplier_id, chosen_unit_price); the FKs are nullable. Admin UI replaced with the rebuilt one (old: admin.yaml.bak). |
| 5 | Optimization goal in the prompt ("fastest reliable delivery while keeping costs reasonable") and temperature 0.7 are my choices; world conditions come from config/ai_test_context.yaml. Supplier count uses a query in the Item event; `Product.count_suppliers` is a Rule.count. |
