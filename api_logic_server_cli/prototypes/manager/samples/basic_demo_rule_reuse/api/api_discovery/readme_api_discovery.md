# api_discovery: custom API services

Every `.py` file in this folder is loaded at startup by `auto_discovery.py`; there is nothing to register.
Add a file, restart, and its endpoints appear in Swagger. Files here include the MCP discovery endpoint
(`/.well-known/mcp.json`), any custom or B2B API you ask for, and, for each Kafka subscribe pipeline,
a `*_kafka_consume_debug.py` file (below).

## The `*_debug` services: worth using

For each Kafka subscribe pipeline `<topic>`, the AI generates `<topic>_kafka_consume_debug.py`. It is about ten lines;
the engine is `integration/system/EaiDebug.py`. It gives you two endpoints, for development only (no authentication):

| Endpoint | What it does |
|---|---|
| `GET /consume_debug/<topic>?file=...` | Sends a sample message through the pipeline. **Live** through Kafka when a broker answers, otherwise **simulated** (no broker). The reply says which ran. |
| `POST /consume_debug/<topic>/reset` | Purges the pipeline's topics (messages only) so a test starts from an empty queue, no server restart needed. |

Why they matter:
- **No broker, no partner system.** Test the whole path (parse, lookups, rules, rows) in seconds, from a file.
- **Same code as live.** Simulated runs the consumer's own parse-and-save function, so what you see is what a real message does.
  One difference: a simulated rejection leaves no blob row; live leaves the blob with `is_processed = 0` and `error_text`.
- **Repeatable.** Reset the queue and resend as often as you like.

Each debug file's docstring has copy-paste `curl` commands. They are on only while `APILOGICPROJECT_CONSUME_DEBUG` is true
in `config/default.env`; set it to false before anything leaves your machine.

## What to ask the AI

You do not have to remember the steps. Ask in plain words:

| Ask | The AI will |
|---|---|
| "verify message subscriptions" | Empty the topics, send the sample message live through each inbound topic, wait for the blob to be processed (or show its `error_text`), and confirm the domain rows. With no broker it verifies simulated only, and says so. |
| "run the tests" / "run the behave report" | Run the Behave scenarios and report pass/fail counts; the report ties each requirement to its rules and tests. |
| "reset and resend the sample message" | Stop the server, clear the pipeline's tables and topics, restart, send, and show counts. |
| "why is my message stuck?" | Read the blob's `error_text` and `logs/als.log`, and explain the cause. |

How to start clean, how to wait for a live send, and the count query are in `docs/training/eai_subscribe.md`,
section "Verifying a subscribe pipeline".
