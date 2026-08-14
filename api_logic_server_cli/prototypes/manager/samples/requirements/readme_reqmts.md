<!--
  src: api_logic_server_cli/prototypes/manager/samples/requirements/readme_reqmnts.md
  Added: BLT 16.x (Apr 9, 2026)
  Revised: Aug 13, 2026 — loosened PM/Dev framing (any author can write requirements.md),
    added AI Interview as a way to arrive at requirements.md without one, added
    Manager-vs-project as an explicit either/or for running "implement reqs"
  Propagation: part of proto/manager — present in every Manager workspace after BLT
-->

&nbsp;

# Executable Requirements

**Executable Requirements** means the requirements document IS the build spec — not a handoff artifact that gets "interpreted," but a file the AI reads and executes directly, then writes back an audit trail of what it decided.

These are typically used to iteratively add requirements to an existing project using `implement reqs`.

For full docs, [click here](https://apilogicserver.github.io/Docs/Exec-Reqmts/).

&nbsp;

## How it works

```
docs/requirements/<name>/
    requirements.md      ← the spec
    message_formats/     ← sample messages, DDL, mappings
    ad-libs.md           ← AI writes this after running — audit trail of decisions
```

Say `implement reqs <name>` in Copilot Agent mode. AI reads the spec, builds the system, and writes `ad-libs.md` alongside.

&nbsp;

## Where `requirements.md` comes from

There's no fixed authoring process — `requirements.md` just needs to exist before you say `implement reqs`. Three common ways to get there:

- **Written by a person** — a PM, analyst, or dev drafts it directly from DDL, sample messages, architecture notes, whatever they have on hand.
- **A prompt file, as-is** — the same `.prompt.md` files used to *create* a project (see `samples/prompts/`) are already requirements prose. Drop one into `docs/requirements/<name>/requirements.md` unchanged and it works.
- **AI Interview** — no document at all yet. Say something like "create a new project called `<name>`, and let's discuss the system" instead of handing over a written spec; the AI interviews you conversationally (constants, lookups/FKs, integration/judgment calls, type hierarchies), then synthesizes the transcript into a real `requirements.md` and reads it back for confirmation before anything is built. This is the same mechanism Method 4 uses for new-project creation when you don't have a prompt in hand — it works the same way for an existing project's next iteration. See [RFI/RFI-transcript.md](RFI/RFI-transcript.md) for a real transcript (Customer/Order/Item/Product, credit-limit constraint, Kafka shipping notification).

Whichever path you took, the loop from there is the same: AI builds, writes `ad-libs.md` with 🔴 items needing review and 🟡 FYIs, you update `requirements.md` to resolve them, run again. Each cycle tightens the spec and narrows the AI's decision space.

&nbsp;

## Where to run it: Manager or project

`implement reqs <name>` works from either place — pick based on where you are, not because one is "more correct":

| Where | When |
|-------|------|
| **Inside the project** (`cd <name>` first, or open it as its own workspace) | You're already there — most iteration happens here |
| **From the Manager**, prefixing paths with `<name>/` | You just created the project in this same Manager session (Method 4) and want to keep going without switching workspaces, or you're managing several projects side by side |

Same spec, same AI reasoning, same `ad-libs.md` output either way — only the path prefix changes. See the Manager's own CE for the `<name>/`-prefix convention when operating from Manager root.

&nbsp;

## What belongs in requirements.md

- **What to build** — tables, handlers, APIs, logic rules
- **Message formats** — reference files in `message_formats/`; include field mappings where non-obvious
- **Phases** — what's in scope now vs. deferred
- **Acceptance** — how to verify it worked (test commands, expected DB state)

What to leave out: implementation details, file names, framework choices — let the AI decide those and read the ad-libs to see what it chose.

&nbsp;

## Try it — demo_eai walkthrough

`demo_eai/` — B2B order intake via Kafka, with custom API endpoint and outbound shipping notification. Run it end-to-end in under 10 minutes.

This walkthrough opens the created project in its own VS Code workspace — the more common path. If you'd rather stay in the Manager (e.g. you just created the project this session), skip the "open in VS Code" step and prefix Steps 2–4's paths with `demo_eai_exec_reqmts/` instead, per the Manager's path-prefix convention.

**Step 1 — Create the project** (in the Manager terminal):

```bash
genai-logic create --project_name=demo_eai_exec_reqmts --db_url=sqlite:///samples/dbs/basic_demo.sqlite
```

Open the created project in VS Code.

**Step 2 — Copy the requirements set** (from a terminal inside the created project):

```bash
cp -r ../samples/requirements/demo_eai  docs/requirements/demo_eai
```

> `docs/requirements/` already exists in every created project — no need to create it.

**Step 3 — Load context, then run** in Copilot **Agent** mode (not Ask):

```
Please load `.github/.copilot-instructions.md`.
```

Then:

```
implement reqs demo_eai
```

AI reads `docs/requirements/demo_eai/requirements.md`, builds the system, and writes `docs/requirements/demo_eai/ad-libs.md`.

**Step 4 — Review the audit trail** in `ad-libs.md`:

- **🔴 Review Required** — decisions that need your confirmation
- **🟡 FYI** — standard patterns, no action needed

Update `requirements.md` to clarify anything flagged red, then re-run.

> **What you just did:** a written spec drove a full system build — Kafka consumer, custom API, business logic, test fixtures — with a reviewable audit trail. No ambiguous handoff, no interpretation gap.

**Step 5 — Test:**

- add these to `config/default.env':

```
APILOGICPROJECT_KAFKA_CONSUMER = {"bootstrap.servers": "localhost:9092", "group.id": "demo-eai-order-group"}
APILOGICPROJECT_KAFKA_PRODUCER = {"bootstrap.servers": "localhost:9092"}
```

- start Docker: `demo_eai_exec_reqmts % docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d`
- send order to kafka: curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json"