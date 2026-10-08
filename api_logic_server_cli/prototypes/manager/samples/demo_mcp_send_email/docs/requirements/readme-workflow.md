# docs/requirements/

Place your **Executable Requirements (XRD)** here, then say **"implement reqs"** to AI.

**See `project_creation_report.md`** (generated at `genai-logic create` time) for this
project's own record: where its scaffold came from, and a running index of every use
case implemented so far (each linked to its `ad-libs.md`).

## Structure

```
docs/requirements/
  readme-workflow.md               ← this file (narrative, not executed)
  project_creation_report.md        ← generated: this project's record + Use Cases index
  project_creation_prompt.md        ← generated: what was requested (real or inferred)
  <use_case>/
    requirements.md       ← executable spec: logic rules, use cases, constraints
    ad-libs.md             ← decisions made beyond the spec
    message_formats/       ← Kafka topic shapes (JSON or XML samples)
      <topic>.json
      <topic>.xml
```

## Workflow

**Phase 1** (done — in Manager): `genai-logic create` → running API + Admin UI  
**Phase 2** (here): copy a requirements set, say "implement reqs" → AI executes spec, reports ad-libs

## Sample requirement sets

Available in the Manager at `samples/requirements/`:
- `Order-EAI/` — Kafka order integration (subscribe + publish, custom B2B API)
- `elmo/` — CIMCorp/ISDC customs shipment XML ingestion via Kafka

Copy one into this folder:
```bash
cp -r <manager>/samples/requirements/Order-EAI/* docs/requirements/
```

## Ad-libs report

After "implement reqs", AI produces an ad-libs report listing every decision
made beyond the spec. Zero ad-libs = spec was complete and unambiguous.
