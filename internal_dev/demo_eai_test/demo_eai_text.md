clarifications required

shipping is a copy_over for test
* doc'd as failing...?

demo_eai includes a subscribe step
* and (ugly) says run rules
* is this <> the blt?

confusing - 2 samples (what is in mgr/samples?)
* Sample-Basic-EAI - is for mgr/basic_demo_eai -- kafka with just 1 system (vs shipping)
* Integration-EAI - more extensive, 2 projects (eg, shipping, using the overlay creation technique)
* Sample-Integration - ??

---

## BLT relationship (confirmed, 2026-09-23)

BLT = `org_git/ApiLogicServer-src/tests/build_and_test/build_load_and_test.py`.
The referenced test is ~line 1519-1564:

* `test_create_shipping` — `ApiLogicServer create --project_name=tests/Shipping --db_url=shipping`
  (a SEPARATE db/project, not basic_demo)
* `test_run_shipping` — runs Shipping on port 5757, subscribes to Kafka (has a
  FIXME: fails when run from BLT, works manually in VSCode/debugger — "?threads?")
* `test_run_nw_kafka` — runs `ApiLogicProject` (nw db) on default port, with
  `APILOGICPROJECT_KAFKA_PRODUCER` env set
* `test_nw_kafka` / `validate_nw_with_kafka()` — POSTs an order to nw's
  `OrderB2B` custom service, asserts it's "seen in shipping"

So BLT's version is genuinely **2 separate running projects/processes** (ApiLogicProject
publisher on 5656, Shipping subscriber on 5757), each from its own database
(nw vs shipping). This is the "Integration-EAI" 2-project pattern referenced above.

**TODO:** confirm whether `test_run_shipping` still actually fails when run from BLT
(the FIXME/threads comment above it may be stale — could have been fixed since). Check
current BLT run logs/CI, or just re-run BLT's Kafka/shipping section, before trusting
the FIXME comment as still-accurate.

**basic_demo_eai** (`samples/basic_demo_eai`, readme.md) collapses this to **1 project**:
same models.py has both the publish rule (Check Credit's `app_integration.py`, on
`date_shipped` set → Kafka topic `order_shipping`) and a subscribe step (Section 5,
`order_b2b` topic → Order/Item) — both running in the same process, same port 5656.
Avoids the fiddliness of standing up + coordinating 2 projects/ports just to see
pub+sub work. Confirms Val's recollection: basic_demo_eai was devised as the
1-project simplification of the BLT's 2-project shipping test, for demo purposes.

## readme.md cleanup — issues found in current samples/basic_demo_eai/readme.md

* Two literal garbled lines (leftover edit artifacts?), not proper headers/asides:
  * line 266: `**ppings here but not in Section 7?**`
  * line 352: `**pings needed in the prompt**`
  (look like truncated "mappings" — need proper section headings/callouts)
* Section 1's "Create From Existing DB" collapsible tells user to create
  `basic_demo_vibe` in the Manager — but the TL;DR at top says the project is
  `demo_eai` from `basic_demo.sqlite`. Name mismatch is confusing (copy/paste from
  a different sample?).
* TL;DR line 18 says the project was created via
  `genai-logic create --project_name=demo_eai --db_url=...`, then "Executable
  Requirements (implement reqs)" — but Section 1 describes the OLDER
  create-then-declare-logic-by-hand flow (Sections 2 onward), not implement-reqs.
  Readme seems to be mixing two eras/methods of building the same sample.
* References an `Integration-EAI` doc page (line 215, 356) for more detail — not
  yet clear if that page is current/consistent with this simplified readme.
* Readme's TL;DR/top says the build path is `create` + `implement requirements
  docs/requirements/demo_eai` (1 shot, from `samples/requirements/demo_eai/...
  requirements.md` — 5 gherkin features incl. row-level security). But Sections
  1-7 are a separate, older, manual step-by-step walkthrough (create → hand-declare
  Check Credit → custom API → subscribe → publish) that predates that consolidation.
  The manual walkthrough **never covers Security (req §5)** at all — readme is
  silently missing a whole feature vs. the real requirements.md.
* Section 7 tells the user to "upgrade" the publish rule from key-only to
  by-example — but see verification below: the pre-built sample already ships
  with by-example publish. Section 7's prompt is stale/no-op against the actual
  prototype state.

## Verified against the pre-built samples/basic_demo_eai (2026-09-23, ran the actual server)

Ran `python api_logic_server_run.py` in `samples/basic_demo_eai`. First run showed
`UNKNOWN_TOPIC_OR_PART` errors on startup — wrongly read as "no Kafka broker running."
**Corrected:** Val's Docker Desktop already runs `broker1` persistently (16h+ uptime,
9092/9093) alongside sqlsvr/postgresql/mysql/keycloak containers — this is a standing
dev environment, not spun up per-test. The error just meant the `order_b2b` /
`order_b2b_processed` topics didn't exist yet. Ran the readme's own
`integration/kafka/order_b2b_reset.sh` (creates both topics), restarted the server —
clean subscribe, no errors. Then published a real message directly via
`docker exec broker1 kafka-console-producer.sh --topic order_b2b` (had to
`json.dumps` to single-line first — piping a multi-line file to the console producer
fragments it line-by-line, my mistake, not a product bug) — consumed live end-to-end:
blob saved → 2-message pattern → parsed → Order/Item created via LogicBank →
`is_processed: True`. So live Kafka pub/sub is fully verified, not just the
no-Kafka debug endpoint.

**Lesson:** don't infer infra absence from an app-level error message — check
`docker ps` first. Result: **every documented capability works as claimed**:

* Admin app (302 redirect) + Swagger API (200) both up on :5656
* Section 6's `consume_debug/order_b2b` curl — works, creates Order+Items,
  amount_total correct (390 = 90+300), blob marked processed
* Section 4's B2B custom API (`POST /api/OrderB2B`, using the docstring's own
  curl) — works, order created, Check Credit rules fire
* Check Credit rejection — POSTing an over-limit order correctly returns 400
  "balance exceeds credit limit"
* Section 7 publish — PATCHing `date_shipped` fires `publish_kafka_message` with
  a **full by-example payload** (customer_name, items, unit_price, total) — NOT
  the key-only `{"id": 42}` shape Section 7's prompt claims is the starting point
* Live Kafka (not just consume_debug) — reset topics, restarted, published a real
  message to `order_b2b` via the broker's console producer — consumed and
  processed correctly, `is_processed: True`

So: the running system is solid and everything in the readme that IS documented
works. The problems are entirely in the readme's own narrative/organization
(stale "needs upgrading" framing, missing security section, two unreconciled
build paths, name mismatch, garbled headers) — not in the underlying sample.

## Readme rewrite (2026-09-23) — done, both gold + local

Restructured both `org_git/Docs/docs/Sample-Basic-EAI.md` (gold) and
`samples/basic_demo_eai/readme.md` (local mirror, hand-applied copy_md transform)
to fix the core issue: **the doc looked like a multi-step build process, but it's
actually one command** (`create` + `implement requirements docs/requirements/demo_eai`).
Sections 2/4/5/7 were imperative "create the X" prompts implying the user runs them
in sequence — they're really a tour of what that one command already built.

Changes:
* Top: "entire build" framing + direct link to the real requirements.md on GitHub
  (verified 200, not the wrong Docs-repo path I guessed first — it lives in
  ApiLogicServer-src/api_logic_server_cli/prototypes/manager/samples/requirements/demo_eai/...)
* Added upfront fork (moved to right after TL;DR, not buried below Overview per
  Val's steer): "just run it → Section 6" vs "build it yourself → Sections 1-5b, 7"
* Section 1: was a redundant second "create" step with the `basic_demo_vibe` name
  bug — replaced with "Run and Verify" (no rebuild, just confirms it works)
* Sections 2/4/5/7: reworded from "Create a B2B API..." (imperative) to "requirements.md
  §N asked for X — implement requirements built Y" (retrospective), each showing the
  actual Gherkin feature from requirements.md
* Added missing 5b (Security, req §5) — previously absent from the walkthrough entirely
* Fixed §4/Section 7's stale claim that publish needs "upgrading" to by-example —
  it's already by-example out of the box (verified live)
* Diagram: replaced wrong 2-project demo_kafka.png (old shipping/BLT diagram) with
  new demo-eai.png (1 box: basic_demo_eai, labeled order_b2b sub / order_shipping
  pub, Shipping System explicitly "(not part of demo)") — Val edited in Slides,
  iterated on topic labels, confirmed final version live via cache-busted fetch

Not yet done: local mirror's TL;DR block still has un-transformed raw `!!!` mkdocs
syntax (never got copy_md'd recently) — left as-is, cosmetic, didn't block this pass.

## Second pass (2026-09-23) — "read as a new user" review

Val asked: step back, read cold — is it clear what this shows, and does it show it?
Answer was "mostly, but": found 5 real friction points even after the first
restructure —
1. build instructions repeated 3x before any action (TL;DR box, fork, "Executable
   Requirements" block) — reader has to read past two preambles
2. `## Overview` heading didn't match its content (it was the build command)
3. "Section 6" referenced 3x before reader could jump there
4. diagram appeared mid-instructions, before reader had run anything to ground it
5. Section 1 ("Run and Verify") didn't actually verify any of the 5 EAI
   requirements — just base CRUD/Admin App — so "build it yourself" reader had to
   backtrack to Section 6 for the tests everyone needs

Fixed in both gold + local:
* Collapsed the 3x repetition — TL;DR now just explains Kafka concepts; one
  `## Build It` section has the command, once
* Diagram + architecture list moved to top (right after TL;DR, before Build It) —
  Val's call: "always good if the diagram is at the top" — grounds the reader in
  what they're about to build/run before any commands
* Section 1 renamed "Run and Verify", ends with an explicit fork line: go to
  Section 6 to test EAI features, or keep reading for the requirement-by-requirement
  tour — so Section 6 is reachable in one click from both paths, not just the
  "pre-built" shortcut
* "Just want to run it" pointer now targets Section 1 (not Section 6 directly) —
  both paths converge there since Section 1 is real verification either way

## Third pass (2026-09-23) — Kafka-less new users

Val asked: what about new users with no Kafka/Docker installed? Checked whether
`confluent-kafka` is a hard install requirement — it's pulled in transitively by
the `ApiLogicServer` pip package itself (`confluent-kafka>=2.6.0; platform_system
!= "Windows" or platform_machine != "ARM64"`), so a normal install always has the
library; `kafka_producer.py` also has a defensive `try/except ImportError` for the
one excluded platform. So: no broker needed to build, run, or test ANY of this
sample's features (confirmed earlier, Section 6's callout) — the gap was purely
that the doc never told the reader this until deep in Section 6. Added an explicit
"No Kafka installed? No Docker?" callout near the top (right before the "just want
to run it" fork) in both files, so it's seen before Section 1/Build It, not after.

Also moved the "just want to run it, skip building" fork to BEFORE the `## Build
It` command block (was after) — Val's steer: a reader who only wants to run the
pre-built sample shouldn't have to scroll past create/implement-requirements
commands to find their off-ramp.

Verified: pre-built sample DOES include get-Kafka instructions —
`integration/kafka/kafka_readme.md` has a "Live Kafka Test" section
(`dockercompose_start_kafka.yml`, Podman alternative, DevOps-Podman link). Added a
pointer to it from the "No Kafka installed?" callout in both files, so a reader who
does want live Kafka has a direct path instead of hunting.

## Fourth pass (2026-09-23) — "insulting requirements" + CE error_text mandate + full rebuild

Val: the "with all Check Credit rules enforced" / "use the 2-message pattern" lines
in requirements.md §2/§3 are insulting — they imply enforcement is opt-in when it's
actually structural (LogicBank fires on every commit path regardless; CE already
mandates 2-message design in eai_subscribe.instructions.md independent of what the
requirement says). Confirmed both are true by reading check_credit.py (single
declaration, no per-endpoint scoping) and the CE instruction file (mandate predates
this requirements.md). Root cause of the gasp: the requirements.md template was
stating platform guarantees as if they were per-feature asks.

Also found via consume_debug testing: `is_processed=False` alone doesn't say WHY a
blob failed — invalid-lookup and business-rule-rejection failures were
indistinguishable at the DB level, only visible in server logs. Val: for messages
(unlike APIs, where a client is watching synchronously), silent failure isn't
acceptable — the constraint/error text should be captured on the blob row. Val
confirmed this should be as mandatory as the 2-message pattern itself.

**CE changes (org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/):**
* `docs/training/eai_subscribe.md` v1.4→v1.5: added `error_text` column to the
  generated blob table + `_record_error_text()` helper (writes in its own clean
  session scope, respecting the existing "never session.rollback() in a consumer's
  except block" rule) + wired into both consumer-2 code examples + Minimal
  Generation Prompt updated so new projects get this by default
* `.github/instructions/eai_subscribe.instructions.md` v1.2→v1.3: new mandatory
  step 3 (same STOP weight as 2-message design) + added to the pass/fail reliability
  checklist

**requirements.md fix** (both copies — `build_and_test/genai-logic/samples/
requirements/demo_eai/...` and the git-tracked `org_git/ApiLogicServer-src/
api_logic_server_cli/prototypes/manager/samples/requirements/demo_eai/...`):
removed "And create the order with all Check Credit rules enforced" from §2/§3, and
removed the 2-message-pattern/blob/transaction lines from §3 (now a CE default, not
a per-requirement ask). §4's "by-example vs key-only" line was KEPT — that's a
genuine design choice, not a structural default, unlike the other two.

**Full rebuild, following the readme's own instructions, per Val's ask** — built
`demo_eai` fresh in `build_and_test/genai-logic/demo_eai/` from scratch:
* `genai-logic create` + copied the FIXED requirements.md — confirmed clean (no
  "insulting" lines) before implementing
* Had to sync the two edited CE training files into the Manager's venv
  site-packages (org_git checkout isn't pip -e installed here — see
  [[project_org_git_sibling_convention]] memory) — recreated the project after
  syncing so it picked up the error_text mandate
* Implemented all 5 requirements by hand (check_credit.py, app_integration.py +
  order_shipping publish mapper, order_b2b.py subscribe + OrderB2bMapper +
  order_b2b_consume.py row-event bridge + consume_debug endpoint + reset script,
  order_b2b_api.py custom API, declare_security.py Grant) — following
  eai_subscribe.md's exact artifact list and logic_bank_api.md's rule patterns
* Per-use-case docs/requirements/<name>/requirements.md written for each logic file
  (CE mandate)
* Fresh DB (different seed data than the older pre-built sample) — confirmed real
  credit-limit rejection still fires correctly once pushed hard enough (5070 >
  5000, then 9180 > 5000 messages)
* **Live-Kafka end-to-end verification of the error_text fix itself** — reset
  topics, enabled real KAFKA_CONSUMER/PRODUCER config, published a bad message
  (invalid product) directly to the broker: log showed `error_text: [None-->]
  resolve_lookups: no Product found...` written via `_record_error_text()`, no
  crash, no manual rollback; confirmed at the DB level
  (`sqlite3 ... "SELECT error_text FROM order_b2b_message"`). Then published a good
  message to confirm the happy path still works (`is_processed=1, error_text=NULL`).
  This is the first live proof the CE fix actually works, not just that it compiles.
* Kafka Publish (by-example) verified live too — PATCH date_shipped fired
  `publish_kafka_message` with the full shaped payload.

Net result: every one of the 5 requirements works correctly in a completely fresh
build, using the corrected requirements.md and the updated CE. Server cleaned up
after testing (PID killed, port confirmed free).

## Fifth pass (2026-09-23) — swap in the new reference implementation

Val: "yes, we have a new ref-impl. replace the old one (local mgr and gold)."

Full directory swap (Val's chosen option — not an overlay):
* Local Manager: `rm -rf samples/basic_demo_eai && mv demo_eai samples/basic_demo_eai`
* Gold: `rm -rf prototypes/manager/samples/basic_demo_eai`, copied the (now-swapped)
  local one over it

Confirmed the readme.md swap-in was automatic and correct — `genai-logic create`'s
`create_readme()` step (clone_and_overlay_prototypes/create_readme.py) matched
`demo_eai` against the `demo_eai: Sample-Basic-EAI` mapping in Manager-readme.md's
frontmatter and pulled the already-fixed gold `Sample-Basic-EAI.md` via `copy_md()`
— so the fresh build's readme.md was ALREADY our finished content, no manual
reapply needed. Noted (not fixed, not blocking): `copy_md()`'s `title="..."`
code-block-title feature is duplicating some bold labels in the transformed output
(e.g. "Check Credit — no Kafka needed:" appears twice, once as plain bold text once
via the title= directive) — a `copy_md()` mechanism quirk, not something this
session introduced; worth a look sometime but not urgent.

Cleanup before finalizing the gold copy (the working dir had my session's test
artifacts baked in):
* `database/db.sqlite` had 9 orders + 3 blob messages from my manual testing —
  replaced with a fresh copy of `samples/dbs/basic_demo.sqlite` (5 orders, clean
  seed) + re-ran just the `order_b2b_message` DDL (0 rows) — ships clean, not
  polluted with scratch test data
* Removed `__pycache__`/`.pyc` (gitignored anyway, `**/__pycache__` in .gitignore),
  `logs/`, stray keycloak h2 db files (`.mv.db`/`.trace.db`) — none of these belong
  in a committed reference sample
* `docs/images/demo-eai.png` inside the sample was a stale/different-dimension copy
  of the diagram (1454x796 vs the final 1136x688) — even though the readme actually
  references the absolute GitHub URL, not this local copy — synced it for
  consistency anyway

Verified post-swap, both locations: `error_text` column present in models.py +
`_record_error_text()` wired into the subscribe handler; requirements.md clean (no
"insulting" lines); readme.md has the restructured content (13 "Requirement §"
references, matches what we built). `git status` scope on the gold checkout: 76
changed files under `prototypes/manager/samples/basic_demo_eai/` (expected for a
full rebuild-vs-old-prebuilt swap) + the 2 CE training files under `prototypes/base/`.

**Not done / lower priority:** the *installed pip package's* own
`prototypes/manager/samples/basic_demo_eai/` (in this Manager's `venv/lib/.../
site-packages/`) still has the old sample — didn't sync it, since it's a build
artifact that'll refresh naturally on the next package reinstall from gold, not
something checked into source control. Also haven't committed any of this session's
changes (gold checkout has uncommitted modifications) — that's a separate decision
for Val to make explicitly, not assumed here.

## Sixth pass (2026-09-23) — readme + kafka_readme.md: explicit "you don't have to ask" callouts

Val: update the eai readme (and every project's `integration/kafka/kafka_readme.md`,
which comes from `prototypes/base`) to state explicitly what does NOT need to be
specified in a Kafka-subscribe requirement: the 2-message pattern, error handling
(`error_text`), and automatic business-logic enforcement. Scoped explicitly to
`prototypes/base` + the `basic_demo_eai` sample, not every sample.

**Sample-Basic-EAI.md (gold) + samples/basic_demo_eai/readme.md (local) — both:**
* Found and fixed stale quoted Gherkin in Sections 4 and 5 — these had NOT been
  updated when we fixed the real requirements.md earlier this session (the readme
  quotes the spec text inline, so the quotes had drifted out of sync with the
  actual file). Removed "with all Check Credit rules enforced" from §4's quote and
  the 2-message-pattern/blob/error lines + Check-Credit line from §5's quote —
  these quotes now match the real requirements.md exactly.
* Added explicit callout after §2 (Check Credit) explaining rules fire on every
  write path automatically (Admin App, API, custom API, Kafka) — nothing has to
  re-request enforcement.
* Added explicit callout inside §5 (Kafka Subscribe) naming what's absent from the
  Gherkin and why: 2-message pattern + error_text are CE mandates, not per-project
  asks.
* "What Got Built" detail block: added `error_text` alongside `is_processed`
  (previously only documented the boolean flag, not the failure-reason capture) —
  same "not something you asked for" framing.
* Also fixed 3 stale file paths caught along the way while editing this block
  (`place_order/order_b2b_consume.py` → `order_b2b_consume.py`,
  `order_b2b_kafka_consume_debug.py` → `order_b2b_consume_debug.py`,
  `test/order_b2b_reset.sh` → `integration/kafka/order_b2b_reset.sh`) — these were
  leftover references to a directory structure this fresh build doesn't use.

**integration/kafka/kafka_readme.md — 3 copies, all now identical:**
`prototypes/base/...` (gold template for every new project),
`build_and_test/genai-logic/samples/basic_demo_eai/...` (local),
`prototypes/manager/samples/basic_demo_eai/...` (gold sample). Changes:
* New "What you don't have to ask for" section up top, same 3 points
* Trimmed the AI-generation example prompt to remove "using the 2-message pattern"
  and "save the raw payload first, then parse..." — the OLD example told the
  requester to ask for something that's actually always-on; new example is what a
  requirement should look like now (mapping + endpoint only), with a note
  explicitly calling out what's missing and why
* Added a note under "Debug Endpoint" clarifying a real, easy-to-miss behavioral
  gap we found via our own testing earlier this session: the debug endpoint does
  NOT exercise error_text on failure (no blob row created at all if resolve_lookups
  or Check Credit rejects) — only the live 2-message Kafka path does, because Tx 1
  has already committed the blob before Tx 2 can fail. Debug endpoint failures only
  surface via HTTP response + server log.

Did NOT touch any other sample's kafka_readme.md (customs_demo_surtax,
demo_customs_clvs, etc.) per Val's explicit scope — only base/proto + basic_demo_eai.

## Seventh pass (2026-09-23) — testing-helpers quick reference

Val: kafka_readme.md should also flag the testing helpers explicitly — test via
API (debug endpoint), resilience when Kafka's down, topic init/create service.
Asked whether the list was complete.

Answer given: yes, plus one Val didn't name — "no Kafka needed for development at
all" as its own headline point (implied by the other three, but worth stating
directly since it's the single biggest practical win). Added a "Testing helpers —
quick reference" bullet section, placed right after "What you don't have to ask
for" (before the Example), in:
* `prototypes/base/integration/kafka/kafka_readme.md` — generic 4 bullets (debug
  endpoint, Kafka-down resilience, topic-reset-script-does-both-create-and-reset,
  DB-only reset script)
* Local + gold `basic_demo_eai/integration/kafka/kafka_readme.md` — same 3 bullets,
  project-specific (order_b2b, no DB-only reset script bullet since this sample
  genuinely doesn't have one — checked `find ... -iname "*reset*"` first rather
  than assuming symmetry with the generic template)

**Bug found while verifying, not silently worked around:** kafka_readme.md's own
"Live Kafka Test" section pointed at `python test/send_order_b2b.py` — this file
does not exist in basic_demo_eai (confirmed: `find test -iname "*send*"` empty),
even though `eai_subscribe.md`'s "Generated Artifacts" list marks it mandatory
(artifact #9, added in that file's v1.4 changelog specifically to close a prior
dangling-reference gap). So the CE says "always generate this" but this build
skipped it — a real gap in what got built, not something to paper over. Fixed the
SAMPLE's kafka_readme.md (not the generic template, which is correctly describing
what *should* exist) to say so plainly and give the actually-verified alternative
instead: `jq -c .` + `docker exec broker1 kafka-console-producer.sh` (same command
this session already used and confirmed working, `jq -c .` avoids the
multi-line-JSON-gets-mangled mistake made earlier in this same session).

**Not fixed (out of scope for this pass, flagging for later):** the actual missing
`test/send_order_b2b.py` artifact — either regenerate it into basic_demo_eai per
the CE mandate, or decide the mandate is wrong/optional and fix eai_subscribe.md
instead. Left as a known gap, not silently patched over or silently ignored.

## Eighth pass (2026-09-23) — security/readme_security.md rewrite

Val: same treatment for `samples/basic_demo_eai/security/readme_security.md` —
predates the RBAC-via-NL CE update (`docs/training/security.md` v1.0, Apr 21
2026), needs a few NL examples.

Confirmed predates it: old file only had ONE NL example, a stale/wrong Python
translation for it (NL said "credit_limit >= 3000 OR positive balance," the code
only had the credit_limit half — missing the second Grant, and even mislabeled the
comment "credit_limit > 3000" vs the code's actual `>=`), used the old `als` CLI
name instead of `genai-logic`, and never mentioned `Roles`/`DefaultRolePermission`/
`GlobalFilter` at all — just `Grant`. Read the current `docs/training/security.md`
(the real CE) to get the accurate DSL shape before rewriting.

Rewrote (both local + gold, identical) with:
* Correct `genai-logic add-auth` bootstrap commands (was `als`)
* 4 NL→declaration example pairs, using this project's own actual entities
  (Customer.name/balance/credit_limit — verified these columns exist in
  models.py) and matching what §5b's requirements.md/declare_security.py already
  built this session: DefaultRolePermission (read-only sales), Grant with the
  correct 2-clause OR'd pair (credit_limit >= 3000 OR balance > 0 — now actually
  matching the NL, unlike the old file), DefaultRolePermission (manager
  read/write/no-delete), GlobalFilter (exclude a named customer for all but
  manager/admin)
* Pointer to `docs/training/security.md` for the full DSL reference rather than
  duplicating it

Did not touch `docs/training/security.md` itself (the CE) — that one's already
current, this pass was only the stale project-level readme that predated it.

## Ninth pass (2026-09-23) — kafka_readme.md: actually show Kafka + Podman setup

Val: "Live Kafka Test" section just said `docker compose up -d` + a bare link to
DevOps-Podman for Podman — never showed what's actually in the compose file or
walked through Podman's one-time setup inline. Read
`integration/kafka/dockercompose_start_kafka.yml` (single-broker KRaft mode, no
Zookeeper, container `broker1`, ports 9092/9093) and gold `DevOps-Podman.md` to
pull accurate setup steps rather than just linking out.

Rewrote "Live Kafka Test" as 3 numbered steps in both `prototypes/base` (generic)
and both `basic_demo_eai` copies (project-specific, `order_b2b` topic name,
`demo-eai-group1` group — verified against this session's actual
`config/default.env`):
1. **Start the broker** — Docker one-liner + verify (`docker ps`), AND the full
   Podman one-time setup inline (brew install podman, machine init/start, optional
   podman-desktop, docker-compose plugin + wiring) followed by the same
   podman-compose command — not just a link out
2. **Enable Kafka in the app** — the `config/default.env` KAFKA_SERVER/
   KAFKA_CONSUMER_GROUP lines, with a note that omitting them is expected
   fallback behavior, not an error (ties back to "What you don't have to ask for")
3. **Reset topics, start server, publish** — existing reset-script + (for the
   sample) the jq/console-producer workaround for the missing send script, now
   with an explicit Podman substitution note added
Also added a "stop the broker when done" reminder (docker/podman compose down) —
wasn't mentioned anywhere before.
