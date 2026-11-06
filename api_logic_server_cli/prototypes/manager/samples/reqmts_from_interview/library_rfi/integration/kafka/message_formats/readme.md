# integration/kafka/message_formats/

Store JSON (or XML) message format specs here — one file per Kafka topic.

These files serve **two purposes**:

1. **AI prompt input** — paste or reference when asking AI to generate a subscriber or publisher mapper
2. **Test fixtures** — the `consume_debug` endpoint reads them directly; no running Kafka needed

## Naming convention

Use the topic name: `order_b2b.json`, `order_shipping.json`, etc.

## Example

```json title="order_b2b.json — inbound subscribe message"
{
  "Account": "Alice",
  "Notes": "Kafka order from sales",
  "Items": [
    { "Name": "Widget",  "QuantityOrdered": 1 },
    { "Name": "Gadget",  "QuantityOrdered": 2 }
  ]
}
```

```json title="order_shipping.json — outbound publish message (desired shape)"
{
  "order_id": 1,
  "order_date": "2026-04-06",
  "customer_name": "Alfreds Futterkiste",
  "total": 100.00,
  "items": [
    { "quantity": 2, "product_name": "Chai", "unit_price": 25.00 }
  ]
}
```

See [kafka_subscribe_discovery/](../kafka_subscribe_discovery/) and [kafka_publish_discovery/](../kafka_publish_discovery/) for the generated mappers that use these formats.
