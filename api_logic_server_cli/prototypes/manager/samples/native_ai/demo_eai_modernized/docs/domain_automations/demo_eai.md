# Demo EAI — Check Credit, B2B API, Kafka Subscribe/Publish, and Row-Level Security

**Created:** 2026-10-27
**Tables:** Customer, Order, Item, Product, OrderB2bMessage
**Rules:** 7 rules: 1 copy, 1 formula, 2 sum, 1 constraint, 2 after_flush_row_event

## Prompt

implement requirements samples/requirements/demo_eai/docs/requirements/demo_eai

## Notes

- 2-message EAI consume pattern implemented for `order_b2b` using `OrderB2bMessage` (`is_processed` + `error_text`).
- By-example EAI publish implemented for `order_shipping` on `Order.date_shipped` transition.
- Sales role row-level security implemented via two OR'd `Grant` declarations (`credit_limit >= 3000` or `balance > 0`).

