# Kafka Integration

Full docs: [Integration-EAI](https://apilogicserver.github.io/Docs/Integration-EAI/)

To see a Sample Integration, [click here](https://apilogicserver.github.io/Docs/Sample-Integration/).

Use AI to describe the Kafka integration you want. The prompt can be plain text or Gherkin-style; this readme takes no position on format.

## What you don't have to ask for

Three things below are built into every Kafka subscriber this platform generates —
structural guarantees of the platform, not decisions left to your prompt. You will
not find them mentioned in the example prompt below, and that's deliberate:

1. **The 2-message pattern is always used.** Every generated subscriber saves the
   raw payload first (Tx 1, always commits), then parses and persists in a second
   transaction (Tx 2). A single-transaction consumer that parses inline is never
   generated, whether or not your prompt mentions "2-message pattern" — it's the
   platform's mandatory design, not an option you opt into. See
   `docs/training/eai_subscribe.md` § Critical Design Decision. This project's own
   `integration/kafka/kafka_subscribe_discovery/order_b2b.py` is a working example.
2. **Failures are never silent.** If Tx 2 fails (a bad lookup, a rejected business
   rule), the blob row is left with `is_processed = False` **and** an `error_text`
   column recording *why* — queryable directly (`SELECT id, error_text FROM
   order_b2b_message WHERE is_processed = 0`), not something you have to dig out of
   a server log. This is as mandatory as the 2-message pattern itself.
3. **Business logic is enforced automatically, on every path.** Whatever
   declarative rules govern your domain (Check Credit, in this project) fire the
   same way whether the triggering write came from this Kafka consumer, a REST
   call, the `OrderB2B` custom API, or the Admin App — LogicBank hooks the database
   commit itself, so there's no way to reach the database without going through the
   rules. Your prompt never needs to say "and enforce the existing rules here too."

## Testing helpers — quick reference

These exist so you can develop and test this pipeline without ever standing up
Kafka, and so live-Kafka testing is repeatable once you do. Details for each are
in the matching section below.

- **No Kafka needed for development.** `/consume_debug/order_b2b` runs the
  identical parse/persist code the live consumer uses — same `OrderB2bMapper`,
  same lookups, same Check Credit rules — just triggered by a curl instead of a
  topic message. Build and verify the whole pipeline before ever touching Docker.
- **The server tolerates Kafka being down.** No broker running is not an error
  condition: the server starts normally (`Kafka mode: FALLBACK` in the log) and a
  publish attempt logs a delivery failure after a short timeout instead of
  crashing the request.
- **Topic setup is one script.** `integration/kafka/order_b2b_reset.sh` both
  *creates* the `order_b2b`/`order_b2b_processed` topics the first time and resets
  them (delete + recreate) every time after — same command either way.

## Example

```text
Subscribe to Kafka topic `order_b2b`.

The inbound message format is in `integration/kafka/message_formats/order_b2b.json`.

Field mappings:
- `Account` -> lookup Customer by name, set customer_id
- `Items.Name` -> lookup Product by name
- `Items.QuantityOrdered` -> Item.quantity

Also create a `/consume_debug/order_b2b` endpoint so the flow can be tested without Kafka.
```

Note what's absent from that prompt: no mention of the 2-message pattern, no
mention of error capture, no mention of enforcing existing business rules — all
three happen regardless, per the section above.

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

**One real difference from the live Kafka path:** on success, the debug endpoint
creates the blob row itself (single transaction, `is_processed=True` from the
start) — there's no separate Tx 1/Tx 2 to observe. On *failure*, this means no blob
row is created at all, so `error_text` has nothing to attach to; the error only
shows up in the HTTP response and the server log. The `error_text` capture is a
property of the live 2-message Kafka path specifically (Tx 1 already committed the
blob before Tx 2 can fail) — to see it in action, use Live Kafka Test below.

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

## Offset Commit — Dev/Demo vs Production

`FlaskKafka.py` ships with `consumer.commit()` **disabled** (`enable.auto.commit=false`).

**Why:** offsets are never committed, so every server restart replays all messages from `earliest`.
This is intentional for demos and debugging — no need to resend messages or reset topics between runs.
The `is_processed` guard on Consumer 2 makes replays a safe no-op: if the blob is already processed, the handler logs one line and returns.

**Production:** uncomment `self.consumer.commit(asynchronous=False)` in `FlaskKafka.py` `_run_handlers()`
for standard at-least-once delivery where offsets advance after each successful handler and restarts do not replay.

---

## Live Kafka Test

### 1. Start the broker

`integration/kafka/dockercompose_start_kafka.yml` starts a single-broker Kafka
(KRaft mode, no Zookeeper needed) as container `broker1`, listening on `9092`
(client) and `9093` (controller).

**Docker:**

```bash
docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d
docker ps   # confirm broker1 is Up, ports 9092-9093
```

**Podman — same compose file, unchanged, plus one-time setup the first time you use
it on a machine:**

```bash
# One-time, if not already set up:
brew install podman
podman machine init      # downloads ~800MB
podman machine start     # do this again after every reboot, unless...
brew install --cask podman-desktop   # ...you install this GUI app, which
                                      # auto-starts the VM at login instead
brew install docker-compose          # Podman uses this as its compose provider
mkdir -p ~/.docker
echo '{"cliPluginsExtraDirs":["/opt/homebrew/lib/docker/cli-plugins"]}' > ~/.docker/config.json

# Then, same as Docker but with podman:
podman compose -f integration/kafka/dockercompose_start_kafka.yml up -d
podman ps   # confirm broker1 is Up, ports 9092-9093
```

Full walkthrough (disk layout, troubleshooting, stopping/starting the VM):
[DevOps-Podman](https://apilogicserver.github.io/Docs/DevOps-Podman/).

### 2. Enable Kafka in the app

In `config/default.env`:

```text
KAFKA_SERVER = localhost:9092
KAFKA_CONSUMER_GROUP = demo-eai-group1
```

Without these, the app runs in debug/fallback mode only — see "What you don't have
to ask for" above; this is expected, not an error, if you haven't set them yet.

### 3. Reset topics, start the server, publish a test message

```bash
bash integration/kafka/order_b2b_reset.sh   # creates the topics first time, resets after
# F5 to start the server (after Kafka is up, so it picks up the env vars above)
```

This project has no `test/send_order_b2b.py` publisher script — publish a test
message directly via the broker's console producer instead (`jq -c .` collapses
the fixture to one line, since the console producer treats each input line as a
separate message):

```bash
jq -c . integration/kafka/message_formats/order_b2b.json | \
  docker exec -i broker1 /opt/kafka/bin/kafka-console-producer.sh \
  --broker-list localhost:9092 --topic order_b2b
```

(Podman: same command, substitute `podman exec` for `docker exec`.)

Runtime reminders:

- Run exactly **one** server process during Kafka consume testing.
- If topics were reset while the server was running, restart the server before publishing.
- Keep the consumer group unique per cloned or renamed project.
- Stop the broker when done: `docker compose -f integration/kafka/dockercompose_start_kafka.yml down`
  (or `podman compose ... down`).