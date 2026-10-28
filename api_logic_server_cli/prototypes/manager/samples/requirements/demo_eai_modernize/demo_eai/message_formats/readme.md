Message shapes recovered from the legacy system (`samples/native_ai/demo_eai_legacy`).

- `order_b2b.json`: inbound partner order (REST `POST /OrderB2B` and Kafka topic `order_b2b`). Shape from `app/integration.py`; sample values from the legacy tests (1 Widget + 2 Gadgets for Alice, total 390).
- `order_shipping.json`: outbound message on topic `order_shipping`. Shape from `_shipping_message` in `app/logic.py`; sample values are order 1 in `samples/dbs/basic_demo.sqlite`.

`Notes` in the B2B sample is a placeholder; the legacy code accepts it but its tests do not set it.
