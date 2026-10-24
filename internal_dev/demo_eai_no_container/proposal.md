# Proposal: demo_eai without containers (Kafka and Keycloak optional)

Date: 2026-10-23. Follows `analysis.md` (the 25-minute Codespace run with no container runtime). Status: the scripts are built in gold source and were run end to end locally (results below); not yet run in a Codespace.

## Goal

The demo should finish quickly and honestly for a user who has Python, VS Code and API Logic Server but no Docker or Podman (or has them but not started). It should say which mode ran and must not depend on the AI improvising.

## Decision

Two bare scripts generated from one annotated source, plus a stop-instead-of-improvise guard in the full script.

| File (gold: `prototypes/manager/samples/requirements/demo_eai/`) | Purpose |
|---|---|
| `create_script_annotated.txt` | Single source. `//` lines are notes; `[full] ` lines go only to the full script; `[no-container] ` lines only to the no-container script; untagged lines go to both. The two regenerate commands are in its header. |
| `create_script.txt` | Full: Keycloak in a container, live Kafka. New first line: run `docker info` then `podman info`; if both fail, STOP and point to the no-container script; if only podman works, use `podman compose`. |
| `create_script_no_container.txt` | No containers: `add-auth --provider-type=sql`, `KAFKA_SERVER` left unset (fallback mode), verification through `/consume_debug` and the server log, an explicit "do not start or install Docker, Podman, Keycloak or Kafka, and do not download anything" instruction, and a verbatim closing line naming the mode and what was not verified. |

Both scripts now also tell the AI to skip logic diagrams with one line if `dot -V` fails, rather than installing graphviz.

## Why this shape

- The platform already has the switches: `KAFKA_SERVER` unset gives `Kafka mode: FALLBACK` (no producer or consumer, publish logs "Kafka not enabled" and continues, `/consume_debug/order_b2b` is the test path); `--provider-type=sql` needs no container.
- The no-container script can be run locally without a Codespace, so it can be tested and analyzed quickly.
- A tagged single source keeps the two scripts from drifting.
- A CLI command (`genai-logic containers --sense|--disable`) and a `preflight.py` were considered and deferred: the second script does the same job with no new code. Revisit if more samples need it (at least 7 samples ship a Kafka compose file).

## What was verified (local run, no containers)

Run on this Manager with the no-container script, from `genai-logic create` to the traceability report, with no Docker, Podman, Keycloak or Kafka broker used:

- Wall time: about 6 minutes (16:50:46 to 16:56:42), including build, diagrams, tests and report. Caveat: this run was not blind (the CE and demo had been read earlier), so a cold run will be slower.
- Defaults already give fallback: `config/default.env` ships with `KAFKA_SERVER` commented out and `APILOGICPROJECT_CONSUME_DEBUG = true`; `Kafka mode: FALLBACK` appeared in the server log. The "C2" step in the no-container script is therefore a check, not a change.
- Row-Level Security passes on the SQL provider: user `s1` (role `sales`, password `p`, from the pre-built auth database) sees the 4 customers matching `credit_limit >= 3000 or balance > 0` and not the fifth. This answers the open question.
- Behave: 5 features, 11 scenarios, 11 passed, 0 skipped. Traceability report: 5 of 5 requirements implemented and tested.
- Publish side: a shipped order logs `publish_kafka_message: topic='order_shipping' ... [Note: **Kafka not enabled**]` followed by the message JSON, and the PATCH returns immediately (no 10 s stall, since no producer is configured).
- B2B API: an over-limit order returns HTTP 400 with the credit message (via `safrs.ValidationError`); the Codespace run had returned HTTP 200 with the error in the body.

Not verified in this mode: live Kafka delivery (Consumer 1, Consumer 2, the bridge event, `error_text` recording, delivery to `order_shipping`), Keycloak.

## Live subscribe test (added after the no-container run)

The no-container Behave tests never touched Kafka, so a live-capable version was built in `demo_eai` and proved against a throwaway Podman broker (`broker_demo_eai`, port 9192, removed afterwards; `broker1` untouched):

- **Endpoint** `/consume_debug/order_b2b?file=...&mode=auto|simulated|live`: live publishes to topic `order_b2b` with the server's producer and returns when the broker acknowledges (like any sender); simulated runs the parse-and-save function directly. The response says which ran (`mode`). Works with curl. The switch is parsed as a boolean (`false`/`0` turn it off). No token requirement yet.
- **Tests** call the endpoint in `auto` mode, poll the API for the outcome when delivery was live, record the mode per scenario in `logs/delivery_modes.json` (cleared by a `before_all` hook), and include one live-only scenario (a rejected message keeps its `error_text`) that skips without a broker.
- **Artifacts the CE lists but the first build skipped:** `test/send_order_b2b.py` (clvs-style publisher) and `integration/kafka/order_b2b_reset.sh` (container and bootstrap overridable).
- **Report** reads the recorded modes: simulated run gives "⚠ 11 of 12 passed, 1 skipped" and "simulated, no broker"; live run gives "✅ 12 of 12" and "live (localhost:9192)". Outbound `order_shipping` rows read "⚠ message checked in the log, not on the topic" in both modes.
- **Results:** simulated 11 passed + 1 skipped; live 12 passed. The 9 shipping messages were read back from the `order_shipping` topic.

**Bugs the live run found (simulated tests could not):**
1. `eai_subscribe.md`'s `_record_error_text` template uses `safrs.DB.session`, the same session that holds the failed Tx 2's rows, and calls it "fresh". Its first query autoflushes them and raises the original error again. Fixed in the project with a new `Session(safrs.DB.engine)`.
2. `FlaskKafka._run_handlers` calls `sys.exit` on any exception that escapes a handler, so that (or any) exception ends the consumer thread and every later message is silently never processed (only a CRITICAL log line). Fix in `prototypes/base/integration/system/FlaskKafka.py`: log and continue. The Codespace run's "bad message leaves error_text" check may have exercised only a lookup failure, not a failure after rows were added.

## Findings to fix in gold source

1. **Report counts skipped scenarios as passed** (from the Codespace run). Fixed in gold (generator 2.10, not committed): skipped scenarios show as skipped (a ⚠ verdict, "10 of 11 passed, 1 skipped (not verified: §5 Security)", "⚠ SKIPPED" on the scenario). Checked by marking the Row-Level Security steps unrun in a copy of `behave.log`.
   Same change: Messages and APIs has a Kafka mode note above the table (simulated through `/consume_debug`, or live), the "Tests mention it" column is next to Name and reads "⚠ simulated (no broker)" for Kafka channels without a broker, and At a Glance has a Kafka row. `prototypes/base/test/api_logic_server_behave/requirements_traceability_report.py` and its `reports/Requirements Traceability Report Template.md`.
2. **`EaiPublishMapper._serialize_value` does not convert `Decimal`**, so `publish_kafka_message` (`json.dumps(default=str)`) emits amounts as strings (`"390.0000000000"`) instead of numbers as in `order_shipping.json`. This run worked around it in the project's mapper. Fix in `prototypes/base/integration/system/EaiPublishMapper.py`.
3. **`/consume_debug/order_b2b` is unauthenticated, on by default, and reads a server-side path** from the query string. With security enabled, tests call it without a token. Either require auth on the route or default `APILOGICPROJECT_CONSUME_DEBUG` off outside development (CE: `docs/training/eai_subscribe.md`, "DEBUG ENDPOINT GUARD").
4. **`order_date` has no natural source.** `Order.CreatedOn` is null unless something sets it. The CE or the requirement should name the source.
5. **`received_at` has no default** in the generated blob table; the CE's model snippet sets `default=datetime.utcnow` but `rebuild-from-database` does not. The Codespace run hit this as an error-correction loop; this run set it explicitly.
6. **Readme wording:** "Prerequisites: Docker or Podman running" in the demo readme and `Manager-readme.md` should point to the no-container script. Edit in `org_git/Docs/docs/`.

## Remaining steps

1. Review the gold diff: `create_script_annotated.txt`, `create_script.txt`, new `create_script_no_container.txt`, `requirements_traceability_report.py` and its template. The no-container script now also tells the AI to word the Kafka Subscribe delivery step as "submitted through /consume_debug, simulating topic order_b2b with no broker".
2. (Done in gold, not committed) Move the live-subscribe design into the CE: `eai_subscribe.md` (the two-mode endpoint, boolean switch, corrected `_record_error_text`, artifacts #8/#9 completeness check) and `testing.md` (a step that discovers `kafka_subscribe_discovery/*.py` and generates the mode-aware scenarios), plus the `FlaskKafka` fix. Written: `eai_subscribe.md` 1.6 and `testing.md` (Step 1d); code in gold: `integration/system/EaiDebug.py`, `EaiSubscribeMapper.record_error_text`, the `FlaskKafka` fix, `kafka_producer.kafka_available()`. Both demo scripts now name the artifact list.
2b. Commit gold source (not done; nothing is committed).
3. Point the Codespaces README at `create_script_no_container.txt` (injected by `create_codespaces_mgr.py`).
4. Try `docker-in-docker` in `.devcontainer-codespaces/devcontainer.json` and graphviz in `For_VSCode.dockerfile`; if both work, Codespaces can use the full script.
5. Rerun in a fresh Codespace with the no-container script and compare time, config, and closing message with the Codespace run in `analysis.md`.
6. Fix the report (finding 1) and the publish mapper (finding 2), then BLT and `create_codespaces_mgr.py --push`.

## Open questions

- Is `docker-in-docker` allowed and fast enough on the Codespaces plan in use, with prebuilds?
- Should `/consume_debug` stay on by default in generated projects?
- Should a missing Keycloak with `SECURITY_ENABLED=True` fail fast with a clear message instead of hanging at startup?


## Debug endpoints in gold (Oct 24)

- `/consume_debug/<topic>` (send) and `POST /consume_debug/<name>/reset` (purge) are now system code (`integration/system/EaiDebug.py`); each pipeline's file is a thin call with copy-paste curl commands in its docstring (the commands are also logged at startup). Reset purges messages with `delete_records` (topics, consumers and offsets stay), and tells you "nothing to purge" without a broker.
- `kafka_available()` (cached 30 s, 1 s probe) is used by the publish paths, the bridge and the debug endpoints. Measured with the broker stopped: the first publish after the outage costs one 10 s flush while the cache still says "up", then 0.01 s; after the window, a 1 s probe, then 0.01 s. Only one "NOT delivered" is logged (no backlog).
- Verified in `demo_eai` against a throwaway Podman broker: 12 of 12 scenarios live; the reset purged 4 + 4 messages and the suite passed again; without a broker 11 passed + 1 skipped, and the report labels each case.
- Existing projects and the two sample snapshots (`basic_demo_eai`, `demo_customs_clvs`) keep their old debug files until regenerated.

## Run time in the test log and the report (Oct 24)

- `behave_run.py` times the run and appends `Behave run time: N s` to `behave.log`; a shared `features/environment.py` (new, in `prototypes/base`) times each scenario into `logs/scenario_times.json` and clears the previous run's records (including `delivery_modes.json`).
- Report 2.11 shows the run time in At a Glance ("took 0.61 s" simulated, "took 3.0 s" live), the Coverage summary and the Tests line, and each scenario's time next to its result (live Kafka Subscribe scenarios 0.54-0.58 s; the others 0.01-0.05 s).
- The whole-run time includes Behave's own start-up (about 0.3 s), so it is larger than Behave's console "Took" line and larger than the sum of the scenario times.

## Codespaces and Docs (Oct 24)

- Docs repo (not committed): `Manager-readme.md` row for EAI and `Sample-Basic-EAI.md` (v1.10) now point to `create_script_no_container.txt` and explain the two differences (SQL auth, Kafka tested through the debug endpoint / simulated).
- `create_codespaces_mgr.py`: the injected Codespaces note now points EAI users to the no-container script.
- `docker-in-docker` is added to `devcontainer.json` as a commented-out EXPERIMENT only (cannot be tested locally).
- **graphviz in the Codespace image does not build:** the base image `apilogicserver/api_logic_server` is Debian 11 (bullseye, end of life); `apt-get install graphviz` fails with a 404 on a security-archive package (tested on arm64; Codespaces is amd64, likely the same). So `For_VSCode.dockerfile` is unchanged. A base image on a supported Debian (e.g. bookworm) would fix this, and is the more useful change.
