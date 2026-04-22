---
description: "Use when: adding EAI consume, Kafka consumer, subscribe to topic, ingest XML/JSON from partner, enterprise application integration, message-driven persistence, event-driven insert, bridge Kafka to database, add kafka consume, kafka inbound, receive from kafka, how do I add EAI, reliability, replay, duplicate handling"
applyTo: "**/kafka_subscribe_discovery/**"
version: "1.2"
lastUpdated: "2026-04-14"
---
# EAI Consume — Mandatory Pre-Implementation Read

Changelog:
- 1.2 (Apr 14, 2026) - behavior-first reliability contract (invariants/tests); implementation structure not mandated
- 1.1 (Apr 14, 2026) - duplicate handling clarified as requirements-driven (insert-only default; explicit replace-on-duplicate allowed)
- 1.0 (initial) - mandatory pre-read and 2-message consume guidance

⛔ STOP. Before writing any code:

1. Read `docs/training/eai_subscribe.md` IN FULL
2. The 2-message design is mandatory — single-transaction consumers cause data loss
3. Then follow the MANDATORY SEQUENCE in `.github/.copilot-instructions.md` Step 2.5
4. For verification, ensure runtime stability before concluding failure:
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
- If checks fail, prioritize behavior fixes and rerun checks before structural cleanup

After implementation, run the project test gate if present (server must be running):
```bash
bash docs/requirements/customs_demo/test_gate.sh
```
