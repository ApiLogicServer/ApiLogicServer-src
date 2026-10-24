# demo_eai in a Codespace with no container runtime: analysis

Date: 2026-10-23. Run by GitHub Copilot in a Codespace (`/workspaces/codespaces_mgr`) using `samples/requirements/demo_eai/create_script.txt`. Elapsed time: about 25 minutes, paste to final message. The network at the time may have been slow (see "Timing" below). Evidence: `transdcript.md`, `ad-libs.md`, `Requirements Traceability Report.md` in this folder.

## Question

Does the EAI Enterprise Technology Demo degrade gracefully when the user has Python, VS Code and API Logic Server but no Docker or Podman (or it is not started)?

## Verdict

The demo finished and was honest about what it could not verify, but it is not enough yet. Three problems remain, one of them a bug in the report a viewer is told to open.

## What went well

- It completed: 5 of 5 requirements implemented, live Kafka verified (sample message gave a processed blob and a new order; a bad message left `is_processed=0` with `error_text`; shipping an order published a message in the `order_shipping` shape).
- It was honest in `ad-libs.md`: Row-Level Security is a 🔴 "declared but NOT verified", and the closing message listed every deviation from the script.
- It stopped to ask the user about Keycloak instead of guessing.
- It confirmed a risk that had only been inferred: with `SECURITY_ENABLED=True` and no Keycloak, **the server hangs at startup** (it does not return 401s).

## What is not enough

1. **The traceability report misreports the skipped scenario.**
   - Headline: "5 tested; 11 of 11 scenarios passed". Section §5 Security: "✅ 1 scenario(s): 1 passed".
   - But all three Row-Level Security steps are `_(skipped)_` (report lines 1132-1134).
   - `ad-libs.md` tells the truth; the report does not. The report is the file the script tells the viewer to open.
   - Likely cause: the report generator counts skipped as passed. Fix belongs in the gold source `requirements_traceability_report.py` (prototypes/base), then BLT.
   - Also: `ad-libs.md` says 12 scenarios (11 pass, 1 skipped) while the report counts 11. The two disagree.

2. **The recovery was improvisation, not design.**
   - Copilot downloaded a JDK and the Kafka 3.7 tarball into `/tmp`, started a broker and created the topics by hand.
   - It extracted graphviz `.deb` files by hand because `dot` was missing.
   - The script still lists "Docker or Podman running" as a prerequisite.
   - A first-time Codespace user would see something different on each run, or a failure if the downloads are blocked or slow.
   - The report's Data Model section still reads "Graphviz not installed", because `dot` was not on PATH when it was generated.

3. **Security was the cheapest thing to save and was not.**
   - With `--provider-type=sql` (no containers, pre-built User/Role schema), Row-Level Security should have been verified instead of skipped. `declare_security.py` does not depend on the provider.
   - Not yet verified: that the Row-Level Security scenario passes on the SQL provider.

## Timing

The run took about 25 minutes. The transcript has no timestamps, so the split between phases is not measured. What the transcript does show:

- The downloads ran inside the Codespace, so the user's wifi does not affect them. The Kafka tarball from `archive.apache.org` needed a 120 s attempt, then a 170 s resume (`-C -`), then a 4-try retry loop. That points at a slow or throttled source, not a local connection.
- Wifi could slow the chat UI round trips, but each of ~150 tool calls adds seconds, not minutes.
- The AI did ~23 reads/searches of CE and training files before writing its first file (line 200 of the transcript), then created files, ran tests and the report.
- The no-runtime detour added work: debugging the server hang waiting on Keycloak, stopping to ask the user, a hand-assembled graphviz, and the JDK + Kafka download and manual topic setup.
- Likely cost of the missing runtime, inferred from the command pattern (no timestamps):
  - Kafka download: `curl -m 120` was followed by a resume `curl -m 170 -C -`, then a 4-try loop with `-m 170`. The resume pattern means the first two attempts hit their time caps, so at least about 5 minutes went to timeouts and at most about 16 (120 + 170 + 4 x 170 s). A JDK download (`-m 180`) was separate. All of this exists only because there was no Docker broker.
  - Keycloak hang: the server did not come up after `sleep 12` (curl exit 7, connection refused) and `sleep 8`, followed by about 7 diagnostic calls and a kill. Probably 1-3 minutes, plus the question to the user.
  - Kafka publish stalls: not a factor in the test run. `KAFKA_SERVER` was only set in the final live-Kafka step, after the report was generated, so the 10 s `flush` stall did not apply.
  - Human waits: the transcript shows "Continue to iterate?" and "Run in Terminal" prompts and an "Analyzing your answers" question. Time spent waiting for a click is included in the 25 minutes and is unmeasured.
- Baseline (reported by Val): the same script takes about 7-9 minutes at home, with good wifi and Docker. The Codespace run took about 25, so roughly 16-18 minutes of extra time. That is the same size as the estimated detour above (Kafka download timeouts 5-16 min, Keycloak hang 1-3 min, hand-built graphviz, the question). The baseline run differs in more than the runtime (local vs Codespace, and possibly a different assistant), so this is consistent with the explanation but not proof.
- To measure instead of guess: add timestamps per step, and rerun with `docker-in-docker` (recommendation 2) to see how much of the 25 minutes the detour cost.

## Caveats

- One run, one assistant (Copilot, not Claude), one environment. Other assistants may behave differently with no runtime: stop and ask (as here), skip quietly, or report success anyway.
- Earlier findings on the local Manager (not this run): `docker` is not installed there, only `podman`; the existing `demo_eai` project ran Keycloak under podman and reused a broker that had been up 7 days, so neither the "start a broker" nor the "no runtime" path was exercised there.

## Recommendations

1. **Fix the report.** Treat skipped scenarios as ⚠ "skipped", not passed; make the headline and the §5 row say so; reconcile the scenario count with `ad-libs.md`.
2. **Fix the environment, not the script, for Codespaces.** Codespaces is the no-runtime case every time.
   - `.devcontainer-codespaces/devcontainer.json` has no `features` block. Try the standard `docker-in-docker` dev container feature so `docker compose` works.
   - Add `apt-get install graphviz` to `For_VSCode.dockerfile`.
   - Both are untested; verify in a fresh Codespace and prebuild.
3. **Make the script degrade by design** (for local machines too), in `create_script_annotated.txt` (`create_script.txt` is generated from it):
   - A preflight step: `docker info`, then `podman info`, then `dot -V`. Treat a podman machine that is not started as "not available". Print one line with the result.
   - Default to `--provider-type=sql`; offer Keycloak only when a runtime is up.
   - Write `KAFKA_SERVER` to config only after a broker is confirmed up. The producer's `flush(timeout=10)` stalls about 10 seconds per ship PATCH when `KAFKA_SERVER` is set and no broker answers; when unset it logs "Kafka not enabled" instantly.
   - Verify with a broker if there is one, otherwise via `consume_debug` and the publish log line, and say which mode ran.
   - Use `<runtime> compose` instead of the hardcoded `docker compose`.
   - Skip logic diagrams with one line if graphviz is missing.
4. **Then rerun** in a fresh Codespace and compare what the AI says it did, what the config contains, and what the closing message claims.

## Open items from the demo review

- `requirements.md` section 1 says "reject if balance exceeds the credit limit" (no "unshipped" qualifier); the README's Check Credit text says "where date_shipped is null". Confirm the two match.
- Boundary operator: "exceeds" was implemented as `balance <= credit_limit` (FYI in `ad-libs.md`). Fine, but confirm it is what the demo should show.
- Naming drift: the script creates `demo_eai`; the Manager ships `basic_demo_eai`. Confirm the `Manager-readme.md` prefix mapping picks the right readme.
- Known behaviors to keep in view: Kafka offsets are not committed (a restart replays messages and creates duplicate orders); published `order_date` is null because nothing sets `Order.CreatedOn`; the B2B API reports failures in the body with HTTP 200.

## Follow-up: local no-container run (same day)

After the Codespace run, a no-container script was built (see `proposal.md`) and run locally from `genai-logic create` to the report, with no Docker, Podman, Keycloak or Kafka broker.

- Time: about 6 minutes (16:50:46 to 16:56:42). That run was not blind, so a cold run will be slower, but it shows the no-container path itself is cheap: the 25-minute Codespace run spent an estimated 16-18 minutes on the detour.
- Result: 5 requirements implemented and tested, 11 of 11 scenarios passed, 0 skipped. Row-Level Security passed against the SQL authentication provider (user `s1`, role `sales`), which was the open question in the Codespace analysis.
- Kafka fallback was already the default: `KAFKA_SERVER` commented out and `APILOGICPROJECT_CONSUME_DEBUG = true` ship in `config/default.env`.
- New findings: `/consume_debug` is unauthenticated and on by default; `EaiPublishMapper` emits Decimal amounts as strings; `order_date` has no source. See `proposal.md` for the full list and where each fix belongs.
- Not verified: live Kafka delivery and Keycloak (by design in this mode). The report's skipped-as-passed bug was not exercised because nothing was skipped.

## Follow-up: live subscribe

The generated Behave tests never exercised a real Kafka subscribe (they used `/consume_debug`, which does not touch Kafka). A two-mode endpoint and mode-aware tests were then built in `demo_eai` and run against a throwaway Podman broker: 12 of 12 scenarios passed live, and 11 passed with 1 skipped without a broker, with the report labelling each case. The live run found two bugs the simulated tests could not (see `proposal.md`): the CE's `_record_error_text` template re-raises on the poisoned session, and `FlaskKafka` ends the consumer thread on any handler exception. The report generator (2.10) reads the recorded per-scenario mode.
