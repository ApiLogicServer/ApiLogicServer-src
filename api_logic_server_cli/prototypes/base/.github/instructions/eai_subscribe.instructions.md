---
description: "Use when: adding EAI consume, Kafka consumer, subscribe to topic, ingest XML/JSON from partner, enterprise application integration, message-driven persistence, event-driven insert, bridge Kafka to database, add kafka consume, kafka inbound, receive from kafka, how do I add EAI"
applyTo: "**/kafka_subscribe_discovery/**"
---
# EAI Consume — Mandatory Pre-Implementation Read

⛔ STOP. Before writing any code:

1. Read `docs/training/eai_subscribe.md` IN FULL
2. The 2-message design is mandatory — single-transaction consumers cause data loss
3. Then follow the MANDATORY SEQUENCE in `.github/.copilot-instructions.md` Step 2.5
4. For verification, ensure runtime stability before concluding failure:
	- Run exactly one API server process during Kafka consume testing
	- Use a project-unique `KAFKA_CONSUMER_GROUP` after project renames/clones
	- If lookup/reference data must survive reruns, clear ingest tables only
