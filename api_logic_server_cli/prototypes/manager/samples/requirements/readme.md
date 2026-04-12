<!--
  src: api_logic_server_cli/prototypes/manager/samples/requirements/readme.md
  Added: BLT 16.x (Apr 9, 2026)
  Propagation: part of proto/manager — present in every Manager workspace after BLT
-->

&nbsp;

# Executable Requirements

**Executable Requirements** means the requirements document IS the build spec — not a handoff artifact that gets "interpreted," but a file the AI reads and executes directly, then writes back an audit trail of what it decided.

For full docs, [click here](api_logic_server_cli/prototypes/manager/samples/requirements/readme.md).

## How it works

```
docs/requirements/<name>/
    requirements.md      ← the spec  (PM writes this)
    message_formats/     ← sample messages, DDL, mappings (PM gathers these)
    ad-libs.md           ← AI writes this after running — audit trail of decisions
```

Say `implement reqs <name>` in Copilot Agent mode. AI reads the spec, builds the system, and writes `ad-libs.md` alongside.

## PM / Dev scenario

| Who | Does what |
|-----|-----------|
| **PM** | Gathers raw artifacts (DDL, sample messages, architecture notes) — in iCloud, SharePoint, wherever they work |
| **PM** | Writes `requirements.md` — structured prose: what tables, what logic, what integrations |
| **Dev** | Creates `docs/requirements/<name>/` in the project repo, drops in `requirements.md` + supporting files |
| **Dev** | Types `implement reqs <name>` |
| **AI** | Builds the system, writes `ad-libs.md` with 🔴 items needing review and 🟡 FYIs |
| **PM/Dev** | Reviews `ad-libs.md`, updates `requirements.md`, runs again |

The rinse-and-repeat loop is the point — each cycle tightens the spec and narrows the AI's decision space.

## What belongs in requirements.md

- **What to build** — tables, handlers, APIs, logic rules
- **Message formats** — reference files in `message_formats/`; include field mappings where non-obvious
- **Phases** — what's in scope now vs. deferred
- **Acceptance** — how to verify it worked (test commands, expected DB state)

What to leave out: implementation details, file names, framework choices — let the AI decide those and read the ad-libs to see what it chose.

## Try it — Order-EAI walkthrough

`Order-EAI/` — B2B order intake via Kafka, with custom API endpoint and outbound shipping notification. Run it end-to-end in under 10 minutes.

**Step 1 — Create the project** (in the Manager terminal):

```bash
genai-logic create --project_name=demo_eai_exec_reqmts --db_url=sqlite:///samples/dbs/basic_demo.sqlite
```

Open the created project in VS Code.

**Step 2 — Copy the requirements set** (from a terminal inside the created project):

```bash
cp -r ../samples/requirements/Order-EAI  docs/requirements/Order-EAI
```

> `docs/requirements/` already exists in every created project — no need to create it.

**Step 3 — Load context, then run** in Copilot **Agent** mode (not Ask):

```
Please load `.github/.copilot-instructions.md`.
```

Then:

```
implement reqs Order-EAI
```

AI reads `docs/requirements/Order-EAI/requirements.md`, builds the system, and writes `docs/requirements/Order-EAI/ad-libs.md`.

**Step 4 — Review the audit trail** in `ad-libs.md`:

- **🔴 Review Required** — decisions that need your confirmation
- **🟡 FYI** — standard patterns, no action needed

Update `requirements.md` to clarify anything flagged red, then re-run.

> **What you just did:** a PM-authored spec drove a full system build — Kafka consumer, custom API, business logic, test fixtures — with a reviewable audit trail. No ambiguous handoff, no interpretation gap.

**Step 5 — Test:**

- add these to `config/default.env':

```
APILOGICPROJECT_KAFKA_CONSUMER = {"bootstrap.servers": "localhost:9092", "group.id": "demo-eai-order-group"}
APILOGICPROJECT_KAFKA_PRODUCER = {"bootstrap.servers": "localhost:9092"}
```

- start Docker: `demo_eai_exec_reqmts % docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d`
- send order to kafka: curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/Order-EAI/message_formats/order_b2b.json"