---
description: "Use when: adding EAI consume, Kafka consumer, subscribe to topic, ingest XML/JSON from partner, enterprise application integration, message-driven persistence, event-driven insert, bridge Kafka to database, add kafka consume, kafka inbound, receive from kafka, how do I add EAI, reliability, replay, duplicate handling"
applyTo: "**/kafka_subscribe_discovery/**"
version: "1.3"
lastUpdated: "2026-09-23"
---
# EAI Consume — Mandatory Pre-Implementation Read

Changelog:
- 1.3 (Sep 23, 2026) - error_text capture is mandatory, same weight as the 2-message design —
  a failed Tx 2 must record why on the blob row, not just in the server log (see
  docs/training/eai_subscribe.md § error_text)
- 1.2 (Apr 14, 2026) - behavior-first reliability contract (invariants/tests); implementation structure not mandated
- 1.1 (Apr 14, 2026) - duplicate handling clarified as requirements-driven (insert-only default; explicit replace-on-duplicate allowed)
- 1.0 (initial) - mandatory pre-read and 2-message consume guidance

⛔ STOP. Before writing any code:

1. Read `docs/training/eai_subscribe.md` IN FULL
2. The 2-message design is mandatory — single-transaction consumers cause data loss
3. Error capture is mandatory — a failed Tx 2 must set `error_text` on the blob row
   (via `_record_error_text()`), not just log the exception. `is_processed=False` alone
   does not tell an operator why a message is stuck.
4. Then follow the MANDATORY SEQUENCE in `.github/copilot-instructions.md` Step 2.5
5. For verification, ensure runtime stability before concluding failure:
	- Run exactly one API server process during Kafka consume testing
	- Use a project-unique `KAFKA_CONSUMER_GROUP` after project renames/clones
	- If lookup/reference data must survive reruns, clear ingest tables only
	- Normalize placeholder external IDs mapped to local PKs (e.g., `0` → `None`) so DB autoincrement assigns unique local keys
	- Duplicate handling is requirements-driven: insert-only by default; explicit replace-on-duplicate allowed when required
	- Do not mandate specific internal structure (helper layout, function nesting, ORM-vs-DB cascade mechanics)
	- Required outcome: replay invariants and delete integrity checks must pass

Required reliability checks (pass/fail):
- Same payload replay (x2): domain graph counts stable, ingest/blob count increments appropriately
- Parent delete integrity: no orphan child rows remain after parent delete via API/Admin path
- Induced failure (bad lookup or business-rule rejection): blob row has `is_processed=False`
  AND a non-null `error_text` describing the failure — not just a server-log entry
- If checks fail, prioritize behavior fixes and rerun checks before structural cleanup

After implementation, run the project test gate if present (server must be running):
```bash
bash docs/requirements/customs_demo/test_gate.sh
```
