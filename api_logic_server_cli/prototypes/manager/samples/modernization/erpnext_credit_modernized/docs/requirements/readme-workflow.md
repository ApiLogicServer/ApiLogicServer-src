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
- `demo_eai/` — B2B order intake via Kafka, custom API, outbound shipping notification (minimal Folder example)
- `customs_demo_clvs/` — CBSA customs system: 7 XML message variants + CSV mapping table (enterprise-scale Folder example)
- `students_courses/` — course enrollment capacity + attendance drop-off alerting (CE regression fixture; its streak/alert clause is correctly left blocked — see its `README.md` and `RECREATE_PROMPT.md`)
- `students_courses_attendance_sweep/` — phase 2 of `students_courses`: an externally-triggered sweep endpoint + `Enrollment` table that resolves the blocked clause (run it in a project where `students_courses` is already implemented)
- `RFI/` — a real conversational-interview transcript showing how a `requirements.md` is drafted

Copy one into this folder:
```bash
cp -r <manager>/samples/requirements/Order-EAI/* docs/requirements/
```

A flat set named for its `implement reqs <name>` command is copied as the folder itself:
```bash
cp -r <manager>/samples/requirements/students_courses_attendance_sweep docs/requirements/
```

## Ad-libs report

After "implement reqs", AI produces an ad-libs report listing every decision
made beyond the spec. Zero ad-libs = spec was complete and unambiguous.
