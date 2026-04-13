# Kafka Integration

Full docs: [Integration-EAI](https://apilogicserver.github.io/Docs/Integration-EAI/)

To see a Sample Integration, [click here](https://apilogicserver.github.io/Docs/Sample-Integration/).

Use AI to describe the Kafka integration you want. The prompt can be plain text or Gherkin-style; this readme takes no position on format.

## Example

```text
Subscribe to Kafka topic `order_b2b` using the 2-message pattern.

The inbound message format is in `integration/kafka/message_formats/order_b2b.json`.

Save the raw payload first, then parse and persist the order in a second transaction.

Field mappings:
- `Account` -> lookup Customer by name, set customer_id
- `Items.Name` -> lookup Product by name
- `Items.QuantityOrdered` -> Item.quantity

Also create a `/consume_debug/order_b2b` endpoint so the flow can be tested without Kafka.
```

Typical generated artifacts include:

- a subscribe handler in `integration/kafka/kafka_subscribe_discovery/`
- a mapper in `integration/`
- a debug endpoint in `api/api_discovery/`
- optional reset/test helpers for repeatable runs

---

## Debug Endpoint (no Kafka required)

`APILOGICPROJECT_CONSUME_DEBUG=true` must be set in `config/default.env`.

The debug endpoint should run the same parse and persist flow as the Kafka consumer, but against a local fixture file instead of a live topic.

```bash
curl 'http://localhost:5656/consume_debug/<topic>?file=integration/kafka/message_formats/<topic>.json'
```

Expected response shape:

```json
{"success": true, "topic": "<topic>", "blob_id": 1}
```

---

## Reset Helpers

Run reset helpers from the **project root** between test reruns.

Typical helpers:

| Script | Purpose |
|---|---|
| `bash integration/kafka/<topic>_reset_db.sh` | Clears domain/blob tables for repeatable reruns |
| `bash integration/kafka/<topic>_reset.sh` | Deletes and recreates Kafka topics for live-Kafka reruns |

Typical reset sequence:

```bash
bash integration/kafka/<topic>_reset_db.sh
bash integration/kafka/<topic>_reset.sh   # only needed for live-Kafka runs
```

---

## Live Kafka Test

Enable in `config/default.env`:

```text
KAFKA_SERVER = localhost:9092
KAFKA_CONSUMER_GROUP = <project>-group1   # keep unique per project clone
```

Typical live test flow:

```bash
docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d
# F5 to start the server
python test/send_<topic>.py
```

Runtime reminders:

- Run exactly **one** server process during Kafka consume testing.
- If topics were reset while the server was running, restart the server before publishing.
- Keep the consumer group unique per cloned or renamed project.