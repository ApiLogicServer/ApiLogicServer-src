We have a running app on CodeSpaces, so, it works.  It uses our docker container.

I believe making the *Manager* available will:

* promote trials
* be interesting to acquistors - zero friction, cloud on-ramp, way better than low-code or generic ai storefront for ent apps

Here are issues to work:

## 1. venv ✅ DONE

Needs to work without fiddling.  It should - it's the global Python.

**Findings (superseded):** The original plan below assumed codespaces-mgr would have its own `venv/` (like local-mgr). The actual architecture is the opposite: codespaces-mgr has **no `venv/`** — ApiLogicServer is pre-installed globally in the devcontainer image (`apilogicserver/api_logic_server`, `/usr/local/bin/python`). `als` works fine from the terminal.

**Real bug found in live testing (2026-06-14):** F5 ("API Logic Server Run") failed because `.vscode/settings.json`'s `python.defaultInterpreterPath` was `${workspaceFolder}/venv/bin/python` (correct for local-mgr, but codespaces-mgr has no `venv/` — this path never existed). `.devcontainer/devcontainer.json` separately sets `/usr/local/bin/python`, but `.vscode/settings.json` overrides it.

**Fix (Manager root):** `create_codespaces_mgr.sh` step 2 rewrites Manager root `.vscode/settings.json`'s `python.defaultInterpreterPath` → `/usr/local/bin/python`. Applied directly to `org_git/codespaces_mgr` and pushed.

**Fix (samples — 2026-06-15):** All 9 `samples/*/. vscode/settings.json` had broken paths too (`../../venv/bin/python` or baked absolute local paths). Patched all directly in `org_git/codespaces_mgr` and pushed. `create_codespaces_mgr.sh` now includes a loop (after the Manager root patch) that applies the same sed replacement to all `samples/*/. vscode/settings.json` automatically on every future run.

<details markdown>
<summary>Original (superseded) plan</summary>

- `.vscode/settings.json` already points to `${workspaceFolder}/venv/bin/python` — correct.
- But every `.devcontainer-option/devcontainer.json` (basic_demo, scaffold, samples/*, tests/*) hardcodes `"python.defaultInterpreterPath": "/usr/local/bin/python"` — leftover from when each sample was a standalone project with its own venv. Wrong for the Manager layout.
- No `.devcontainer` exists at the Manager root at all, so Codespaces falls back to a default Python, requiring manual interpreter selection.

**Recommendation:** Add a root-level `.devcontainer/devcontainer.json` with `python.defaultInterpreterPath` set to `${containerWorkspaceFolder}/venv/bin/python`, and a `postCreateCommand` that creates/primes `venv` before VS Code's Python extension first scans. Linked to issue 6 (Reload Window) — likely same root cause/fix.

**Manager venv creation command (confirmed from current Manager venv):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install ApiLogicServer
```
- Current Manager venv: Python 3.13.5, `ApiLogicServer==17.0.34` (pulls in `logicbank`, `safrs`, `Flask`, etc. as transitive deps — no `requirements.txt` at Manager root).
- `postCreateCommand` for the new devcontainer: `python3 -m venv venv && venv/bin/pip install --upgrade pip && venv/bin/pip install ApiLogicServer`

</details>

---

## ⏯️ Pick up here (next session)

**Status (2026-06-15):** F5 working in Codespaces after settings fix. OBX reworked. Joel path wired in CE.

**Remaining:**
1. Push `.devcontainer-codespaces/` to gold (`org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager`).
2. Issue 2 — samples/debugger launch configs (run samples with debug from Manager root window).
3. Issue 4 — Kafka/Keycloak scoping note in README.
4. Issue 6 — Reload Window reliability (get interpreter path right before first scan via devcontainer settings).
5. Test F5 in live Codespaces session to confirm yaml import error is gone.

## 2. samples / debugger

We want to be able to run the samples, with debug.  In local version, approach was open new vsc instance - sounds yucky for cs.  `als run` should work, but no debugger...

**Findings:**
- `.vscode/launch.json` (33K, many configs) is scoped to the Manager root — assumes debugging from here, not from a reopened sample folder.
- "Open new VSC instance" per sample = new browser tab/window in Codespaces — clunky, and likely related to issue 6.
- `als run` starts the server but attaches no debugger. No existing "attach to running process" (debugpy attach-by-port) launch config found.

**Recommendation:** Stay in the single Manager-root window. Add launch.json entries that:
  - target `<sample>/api_logic_server_run.py` directly with `cwd` set to the sample dir (debug samples without reopening), and/or
  - "Attach" config (debugpy attach-by-port) for a server already started via `als run --debug` (or equivalent), so no reopen is needed either way.

## 3. OBX / Tutorial ✅ DONE

Manager readme says start here.  I have a sense that is proper for downloaders (== motivated), but a web tire-kicker might want something more shock & awe, ala  samples/prompts/genai_demo.prompt.  But, what of the tutorial?

**Findings:**
- README's "🚀 First Time Here?" (line 56) already splits "Do it" (basic_demo + guided tour, 30-45 min) vs. "Understand it" (basic_demo_logic_gov readme).
- `samples/prompts/genai_demo.prompt` is just a 5-line input spec — not shock & awe itself. The wow is the *output* of running `genai-logic create` against it (full API + Admin UI + rules in ~5 sec), but that's buried in README line 126 under "Additional Demos."

**Recommendation:** For Codespaces, pre-build a demo during container creation (`postCreateCommand` runs `genai-logic create` against genai_demo.prompt or basic_demo) so a working Admin UI/API is *already running* when the browser VS Code loads — tire-kicker sees a live system within seconds. Tutorial/OBX remains the "go deeper" path for motivated users — keep both, just sequence shock-and-awe first for Codespaces.

**Done (2026-06-14):** Reworked "🚀 First Time Here?" in the gold source `org_git/Docs/docs/Manager-readme.md`, and mirrored into local-mgr `README.md` and codespaces-mgr `README.md`. New sequence: "⚡ See it work — 5 minute shock & awe" → "📖 Understand it" → "🔨 Go deeper — 30-45 min guided tour".

**Further reworked (2026-06-15):** "⚡ See it work" block substantially rewritten — see section 5.1 below for current state. The `postCreateCommand` pre-build (running automatically during container creation) is a separate follow-up, not yet done.

## 4. Kafka and Keycloak

Sound pretty heavy... maybe out of scope?  But, they are prominent in the mgr readme.

**Findings:**
- Both require `docker compose up` for a second container — heavy for a quick Codespaces trial; default Codespaces resource tier may struggle running devcontainer + Kafka + Keycloak together.
- Both are core to 2 of the 6 "Strategic Use Cases" in the README (EAI/Kafka demo, security/Keycloak demo).

**Recommendation:** Don't remove from the main catalog — instead mark Kafka/Keycloak demos as "**Local/Docker only — not yet in Codespaces**" in a Codespaces-specific README section (see issue 5), so expectations are set without losing the content.

## 5. OBX / Readme

So, do preceding 2 issues mean we want a tweaked readme

**Recommendation:** Yes — a separate, short `README-codespaces.md` (or a top section in the existing README, shown only in Codespaces) that:
  - Leads with the pre-built running demo (shock & awe, from issue 3) — ✅ done, see issue 3.
  - Points to OBX/tutorial as the "go deeper" path for motivated downloaders — ✅ done, see issue 3.
  - Flags Kafka/Keycloak demos as out-of-scope for the Codespaces quick path (issue 4) — not yet done.
  - Skips/abbreviates the existing "Setup Codespaces" section (README.md:766), which explains *how to get into* Codespaces — moot once you're already there — not yet done.

### 5.1 User Path (current — 2026-06-15)

Reworked in gold (`org_git/Docs/docs/Manager-readme.md`) and all three READMEs:

1. **Lead:** "Most code generators produce code you then have to own. This one produces *models* — executable, maintainable." → `implement project basic_demo from samples/prompts/genai_demo.prompt`
2. **What did it create?** Data model (`database/models.py`), full JSONAPI with Swagger/pagination/opt-locking (`api/expose_api_models.py` — 52 lines, zero per-table code), admin app (`ui/admin/admin.yaml`). *Model-driven generation.* Plain Python — nothing locks you in.
3. **Run it (F5)**, open Admin App.
4. **Trigger the logic:** open Order 1 / Alice, edit Widget item, change quantity to a very large number. Save — it fails.
5. **Ask AI:** *"Why did that fail?"* — explains the credit-limit rule and shows where it lives.
6. **Look at the logic:** `basic_demo/logic/logic_discovery/` — 5 rules replace ~200 lines of procedural code, catch 2 bugs the procedural version misses.
7. **⚠️ Declarative warning:** Rules are auto-invoked, reused, ordered — breaking every assumption about how logic works. Spec said *add*, logic fired on *update*, nobody called it. Ask AI: *"What are rules?"*
8. **Iterate:** new rule via natural language.
9. **Joel tease** (in CE "what are rules" close): *"Convinced? Or thinking 'AI will just generate the logic anyway'? Ask: 'Why not just let AI write the code?'"* → new CE section with governance/audibility argument + link to [Why GenAI-Logic](https://www.genai-logic.com/#h.yo3meupszav4).

## 6. Reliability

Both tries, I had to: Cmd+Shift+P → type "Reload Window" → Enter.

Can we allow for this?

**Findings:**
- No `.devcontainer` exists at Manager root — Codespaces likely falls back to a generic Python devcontainer/image, and the Python extension doesn't pick up `venv/bin/python` until a manual reload forces re-discovery.
- Open question: does `venv/` pre-exist (committed) or get created by a `postCreateCommand` *after* VS Code starts scanning for interpreters? If the latter, that's the classic race causing the reload requirement.

**Recommendation:** Same fix as issue 1 — root-level `.devcontainer/devcontainer.json` with correct interpreter path + `postCreateCommand` that primes the venv before first interpreter scan. Verify venv creation timing relative to VS Code startup.

**Update (2026-06-14), F5 live test:** Hit "F5 timed out waiting for launcher to connect" on first try after pulling the synced repo (`05393cb`). Root cause was a stale extension host from before `.vscode/settings.json`'s `python.defaultInterpreterPath` fix (`ba2ca5a` — was `${workspaceFolder}/venv/bin/python`, a path that doesn't exist in codespaces-mgr; now `/usr/local/bin/python`). **Cmd+Shift+P → "Developer: Reload Window"** picked up the corrected interpreter (3.12.8 at `/usr/local/bin/python`, marked "Recommended"), and F5 ("API Logic Server Run") then worked against `samples/basic_demo_sample`. Confirms this issue's root cause: interpreter/settings changes need a reload to take effect — same fix direction as above (get the interpreter path right *before* first scan, via `.devcontainer/devcontainer.json`'s `postCreateCommand` or `settings`, so no reload is needed at all).

## 7. AI Model

Is < Claude Sonnet 4.6.... up to the task??

**Findings:**
- README.md:48 already states: "We get consistently good results with Claude Sonnet 4.6 (GitHub Copilot or Claude Code extension). 'Ask' mode will not work — use Agent mode." This is an explicit, documented floor.
- Given the volume/complexity of the CE files (2000+ line copilot-instructions, mandatory multi-step "STOP ✋" protocols, strict rule-dependency-tracking conventions), smaller/older models are likely to skip steps.

**Recommendation:** Treat as already answered by the README — no further action unless an A/B test against a specific smaller model is wanted.

---

## Suggested priority order

1. **Root `.devcontainer/devcontainer.json`** — fixes #1 (venv/global Python) and #6 (Reload Window reliability) together; likely same root cause.
2. **Samples/debugger launch configs** (#2) — next-highest impact on "promote trials."
3. **Shock & awe pre-build + tweaked Codespaces README** (#3 + #5) — content/UX exercise, depends on #1 being solid.
4. **Kafka/Keycloak scoping note** (#4) — simple documentation change, can ride along with #5.
5. **AI Model** (#7) — no action needed; already documented.

---

## Internal Procedures — local-mgr vs codespaces-mgr

**Terminology:**
- **local-mgr** — the Seminal Manager at `~/dev/ApiLogicServer/ApiLogicServer-dev/` (root of this repo's parent). Owns a shared `venv/` per `dev-architecture.md`; used for framework development and BLT.
- **codespaces-mgr** — this repo (`ApiLogicServer/codespaces_mgr`), a separate GitHub repo for the Codespaces/cloud trial experience. No `venv/` — relies on the globally pre-installed ApiLogicServer in the devcontainer image (`/usr/local/bin/python`).

### Goal: recreate codespaces-mgr as close to "copy local-mgr" as possible

codespaces-mgr is **not** part of the BLT propagation flow (Seminal Manager → BLT Manager → ApiLogicServer-src). It's a snapshot of local-mgr's *content* (samples, prompts, CE/training docs, README) with a small, fixed set of **environment-specific overrides** for the no-venv/global-Python container.

Pattern: same idea as per-project `.devcontainer-option/` (user renames to `.devcontainer` to opt in to Codespaces config). Applied at the Manager level too — this directory, `.devcontainer-codespaces/`, is a self-contained override bundle (devcontainer files + CLAUDE.md/.gitignore append-fragments + `CodeSpaces.md` itself + `create_codespaces_mgr.sh`), renamed to `.devcontainer/` at the codespaces-mgr target.

### Shared improvements — adopt in BOTH mgrs (not Codespaces-specific)

These came out of Codespaces testing but are general improvements. Push them to **local-mgr** too, so a future "copy local-mgr → codespaces-mgr" inherits them automatically and the conversion script doesn't need to touch them:

- **`.vscode/launch.json`** — "API Logic Server Run (run project from manager)" as the **default F5 target** (move to top of `configurations`). Done in codespaces-mgr (`cd8e91f`), local-mgr, and gold (`prototypes/manager`) — all three now identical.
- **`.vscode/settings.json`** — removed `workbench.editorAssociations` (`*.md` → markdown-preview webview), which was hanging on open. Done in codespaces-mgr (`6723d6e`), local-mgr, and gold (`prototypes/manager`) — all three now identical.
- **OBX "First Time Here?" rework** — new shock-and-awe path (section 5.1 above: create from `genai_demo.prompt` → run → hit credit-limit rule → AI explains → explore → iterate with a new rule), replacing/reordering the current "Do it" 30-45 min tour as the *first* step. Sequence becomes: **shock & awe → understand it → deep-dive tutorial**. This is a README change, and per `dev-architecture.md` the gold source for README content is the Docs repo (`org_git/Docs/docs/Manager-readme.md` or equivalent) — edit there, not in either mgr's `README.md` directly, so both mgrs pick it up via `copy_md()`/normal propagation.

### Codespaces-only overrides — keep in `.devcontainer-option/` + conversion script

These are structurally required by the no-venv/global-Python container and should **not** be pushed to local-mgr (local-mgr's `venv/`-based settings are correct for itself):

- **`.vscode/settings.json`** — `python.defaultInterpreterPath` → `/usr/local/bin/python` (not `${workspaceFolder}/venv/bin/python`); review `python.terminal.activateEnvironment`/`activateEnvInCurrentTerminal`.
- **`.devcontainer/devcontainer.json`** — root devcontainer (renamed from `.devcontainer-option/` on setup, same pattern as per-project samples). Uses `ms-python.debugpy` (not the unofficial fork), `/usr/local/bin/python` as interpreter, port 5656 forwarded for AdminApp.
- **`.devcontainer/setup.sh`** — Codespaces port-visibility script.
- **`.gitignore`** — exclude `venv/` and `.venv/` (codespaces-mgr has neither; guards against an agent mistakenly creating one).
- **`CLAUDE.md`** — Codespaces-specific notes: ApiLogicServer is pre-installed globally, do not create `venv/`/`.venv/` or `pip install ApiLogicServer`, how to recognize/fix a stray `.venv` shadowing the global interpreter.
- **README** — Codespaces-specific framing per issue 5 (leads with shock & awe, flags Kafka/Keycloak as local-only, abbreviates "Setup Codespaces" since you're already there). Layered on top of the shared OBX rework above, not a replacement for it. Also: a one-line "🤖 AI Assistance" note that the Chat panel may default to a non-Claude model in Codespaces and the user must pick Claude Sonnet 4.6 manually each session — **`README.md` is in `SYNC_PATHS`, so re-add this note (and re-check the `demo_customs_surtax` frontmatter line) after each `create_codespaces_mgr.sh` run** until this is automated.

### Recreation procedure — `create_codespaces_mgr.sh` (built, validated)

`.devcontainer-codespaces/create_codespaces_mgr.sh /path/to/org_git/codespaces_mgr [--dry-run]`

codespaces-mgr is a **deliberately curated subset** of local-mgr, not a full mirror — confirmed by `git ls-tree HEAD` on codespaces-mgr (commit `5b360cc`). It has never included `basic_demo/`, `demo_customs/`, `demo_eai/`, `dockers/`, `scaffold/`, `tests/`, `venv/` (all dev/test infra, ~208M combined). The script:

1. Syncs only the intended subset (`SYNC_PATHS` in the script): `.claude`, `.devcontainer-codespaces`, `.env`, `.github`, `.gitignore`, `.vscode`, `CLAUDE.md`, `CodeSpaces.md`, `README.md`, `readme_vibe.md`, `samples/`, `system/`, `webgenai/`.
2. Renames `.devcontainer-codespaces/` → `.devcontainer/` at the target (overwriting any copied-over `.devcontainer-codespaces`).
3. Applies `CLAUDE.md.append` (Codespaces venv-warning block) and `gitignore.append` (`.venv/`) if not already present.
4. Leaves the target staged for review/commit — does NOT commit or push.

**Validated** (2026-06-14) with `--dry-run` against the clean codespaces-mgr checkout (commit `5b360cc`): diff is just the `requirements/readme_reqmts.md` rename, 7 generated `*_governance_report.md` files, and a handful of `system/genai/temp/*` scratch artifacts — i.e. essentially a no-op. `.vscode/launch.json` and `.vscode/settings.json` are now identical across local-mgr, codespaces-mgr, and gold (see shared improvements above), so the sync no longer risks reverting those live-tested fixes.

**Done (2026-06-15):** Non-dry-run executed, all 9 sample settings patched, committed and pushed. Script updated with samples loop.

**Still pending:** pushing `.devcontainer-codespaces/` to gold (`org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager`).

---

## Repo / README changes log (from live Codespaces testing)

Tracking edits made to the repo as issues are found during real Codespaces sessions
(repo: `ApiLogicServer/codespaces_mgr`).

- `.devcontainer/devcontainer.json` — replaced unofficial `atariq11700.debugpy-old` with
  official `ms-python.debugpy`; fixed a total VS Code window hang on first file open.
- `.vscode/settings.json` — removed `workbench.editorAssociations` forcing `*.md` into
  the markdown-preview webview (was hanging on open). `.md` now opens as text; Preview
  button itself still doesn't render — **deferred** (UX issue, not session-blocking).
- `.vscode/launch.json` — moved "API Logic Server Run (run project from manager)" config
  to the top of the `configurations` array, so it's the default F5 target.
- `CLAUDE.md` — added note that ApiLogicServer is pre-installed globally in the
  Codespaces container (`/usr/local/bin/python`); agents should not create a `venv/` or
  `pip install ApiLogicServer`.
- `README.md` (AI Assistance section) — added note that the Chat panel may default to a
  non-Claude model in Codespaces; user must manually pick Claude Sonnet 4.6 via the model
  picker each session (no workspace-default setting exists for this in VS Code).
- `prototypes/manager/.github/.copilot-instructions.md` (gold, propagates to both mgrs) —
  added two guards prompted by a live Codespaces session where the AI edited
  `samples/basic_demo_sample/` in place instead of creating a new sibling project:
  1. **🎯 Active Project Context** (new section before "Creating Projects") — AI must
     track/announce the active project directory and re-confirm before acting on
     ambiguous requests. Needed because Codespaces is a SINGLE persistent workspace
     (no per-project VS Code windows like local-mgr), so multiple project directories
     stay simultaneously "in view."
  2. **NAME-COLLISION GUARD** (Method 4 STEP 1/2) — before naming/creating a new project,
     check for collisions with existing `<name>/` or `samples/<name>*` dirs (e.g. user
     says "basic_demo", `samples/basic_demo_sample/` already exists); `samples/` is
     read-only reference content, never a `genai-logic create`/`rebuild-from-database`
     target.
