# docs/requirements/

Place your **Executable Requirements (XRD)** here, then say **"implement reqs"** to AI.

## Structure

```
docs/requirements/
  readme.md              ← this file (narrative, not executed)
  requirements.md        ← executable spec: logic rules, use cases, constraints
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
