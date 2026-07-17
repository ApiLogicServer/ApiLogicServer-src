# OBX — Out of Box Experience

**Status: draft, working document.** Not yet moved to `internal_dev` — Val is still dictating/correcting content.

Why this matters: no SEs or sales reps exist to set or repair expectations. The OBX *is* the sales process for a large share of prospects. It starts at a readme and has to do, unassisted, what a good SE would do in a first call.

---

## Audience Assumptions

1. **AI-Lovers** — believe AI can do it all. Some see it as a copilot (gen some code to help); the true believer holds "prompt is the source" — iterate/maintain by rebuild & retest.
2. **AI-Skeptics** — concerned about errors, governance.
3. **AI-Neutral** — BAs, Product Managers, Tech Managers. Focused on results: time to market, ability to change, governance (#1 CIO concern per CIO Agenda research), org alignment (as opposed to shadow-IT wars).

---

## Current OBX Cases

All three start at a readme.

1. **Local install** — the BLT simulates a user install. Result: `build_and_test/genai-logic/README.md`
2. **CS-MGR** — stands up against AI-Lovers. Same readme as #1, except it runs on Codespaces for no-install eval. `org_git/codespaces_mgr/README.md`
3. **Neutrals** — also Codespaces-based. `org_git/genai-logic-web-studio/README.md`. Intended to carry much less AI positioning than #1/#2.

**Finding (verified by reading all three, current state):** the intent in #3 isn't yet realized in the artifact. Only the opening section differs (BA/PM framing, "Dev/DevOps/Enterprise Friendly" bullets vs. "Key Idea"). Everything downstream — the AI-is-great-but-hard-to-trust dialectic, the spreadsheet analogy, the same nesting depth — is identical across all three readmes. The three-persona design exists as intent, not yet as three differentiated documents.

---

## Other Goals

1. **Introduce the CE** — it's unique; people need exposure to what it can do. Heads-up, not deep.

**Finding:** currently weak. The readme tells the user to run a command (`load .github/.copilot-instructions.md`) without explaining what CE *is* — a curated, multi-file context that's about to govern the whole session. The one real explanation of CE is nested as a mechanism footnote inside the rules-engine explanation, not surfaced as its own "heads up, here's this other thing we built" moment. This is the same job `.github/welcome.md` was designed to do — see AI Startup Mechanics below for why that's currently broken for Claude.

---

## Mechanics

1. **Readme** — as short as possible to deliver key messages, and get the user started on real systems.
2. **CE** — now a pre-req on readme samples.
3. **Sample apps** — many, with specific targets (vibe, mcp, eai) — buildable yourself or run pre-built.

**Finding:** mechanics goals are largely met. The demo is concrete and falsifiable (real line-count comparisons, a real A/B bug count, a save that actually fails so the skeptic watches enforcement happen, not just reads about it). CE-load is structurally first in the doc. The Demo Catalog covers build-it-yourself vs. pre-built. Governance proof (logic flow diagrams, ad-libs report, health check) exists but is buried ~4 `<details>` levels deep inside "Scaling to the Enterprise" — not surfaced as an entry point for the AI-skeptic persona specifically looking for it.

---

## AI Startup Mechanics

Two cases matter; others are out of scope by design:

1. **Copilot** — the default. Both Manager and every project ship `.github/copilot-instructions.md`. Readme instructs: *"Please load `.github/.copilot-instructions.md`."*
2. **Claude** — if the Claude Code extension is installed, `CLAUDE.md` is the bootstrap file.

**Codespaces is a walled garden:** project pre-prepared, Claude extension deliberately not installed, Copilot-only by design, to minimize setup.

**Key design goal:** the AI panel should give a BRIEF "here's what I can do" (via `welcome.md`) before exposing full CE depth — fear being that without this gate, users never discover CE's depth. Getting this to work reliably (for Copilot) was difficult — multiple redesign iterations, including a Nov 2025 attempt that failed and was reverted. *(Detail on the Nov 2025 failure — pending, Val to fill in.)*

**Live, currently-open bug: `CLAUDE.md` now suppresses `welcome.md`.**

`CLAUDE.md` was recently consolidated (v2.16) to `@`-import `.github/copilot-instructions.md` directly, so Claude and Copilot read one source of truth. That broke the brief-first gate for Claude specifically:

- Copilot never auto-reads `copilot-instructions.md`. It waits for an explicit activation phrase; only then does the file's own internal protocol fire ("read `welcome.md` silently, display only that, stop"). The gate depends on the AI not yet knowing the deep content until asked.
- Claude Code auto-loads `CLAUDE.md` unconditionally, every session, before the user says anything. Since `CLAUDE.md` is now just an `@`-import, the *entire* `copilot-instructions.md` content is in Claude's context from message one — the "unread until asked" premise the brief-first gate depends on is false for Claude.
- Demonstrated live in this session: `CLAUDE.md`'s content was present in context before any activation phrase was typed.

### Investigated: automatic load + automatic welcome print (2026-07-16)

Tactical goal floated: make CE load automatic on both platforms (no "please load" phrase to forget), and have `welcome.md` print automatically in the AI panel. Findings:

- **Automatic load** — already true for Claude (unconditional `CLAUDE.md` auto-load). Achievable for Copilot via `github.copilot.chat.codeGeneration.useInstructionFiles` (on by default) — but there's an open VS Code issue where this has silently regressed (`copilot-instructions.md no longer included in chat context automatically`, microsoft/vscode#279045). If pursued later, don't trust the default — set it explicitly in the shipped `.vscode/settings.json` for both local Manager and Codespaces.
- **Automatic welcome print with zero user action** — not achievable on either platform. No shipped feature for pre-first-turn AI output (Claude Code has an open, unresolved feature request for exactly this — anthropics/claude-code#25543). Copilot's "chat welcome view" is static suggestion buttons, not AI-generated text.
- **Considered:** force welcome into the AI's first response regardless of what the user typed. **Rejected** — users start at the readme, not the chat. Their first real message is often the "create basic_demo..." prompt itself, not a blank hello. Forcing welcome first talks past their actual request.
- **Considered:** do the task, then append a brief CE pointer after. Better, but still intrudes at the exact moment the user's motivation is "let me see what I just built," not "hear about CE."
- **Considered:** merge "introduce yourself" into the same first paste-able prompt (one message, two answers). Workable, but raised a bigger question below.
- **Considered:** force a distinct "introduce yourself to your AI" step before building anything. **Rejected** — recreates the exact skippable-administrative-step problem ("please load...") this thread started from.
- **Side risk surfaced:** if chat responses get good enough, users may stop reading the readme entirely. Acceptable for self-service evaluators — matches the already-validated pull-based "AI as Docent" pattern (Eval-welcome.md). **Not** acceptable for the tuned persuasion narrative (AI-vs-procedural argument, governance proof, evidence) aimed at skeptics/diligence readers — that has to stay durable, stable, citable text in the readme, not regenerated live in chat each time. Chat should nudge back to the readme, not replace it.

### Decision (2026-07-16)

**Keep the existing "please load `.github/copilot-instructions.md`" readme instruction as-is.** No longer strictly required (auto-load likely already works), but it's a low-friction, familiar first action that preserves the two-step flow (see welcome → then create) without forcing anything or risking talking past the user. Experienced users will discover on their own that they can skip it.

This does **not** fix the underlying Claude suppression bug — saying the phrase to Claude may still be a no-op, since `CLAUDE.md`'s auto-load already has the full file in context before the phrase is typed.

**Scoping call: defer the Claude fix.** Exposure is structurally narrow — CS-MGR and Neutrals are both Codespaces, Copilot-only by design (no Claude there at all). Only case 1 (local install) is exposed, and only for users who deliberately add the Claude extension afterward — a smaller, more sophisticated segment. Not fixed now.

### Resolved: dev-architecture.md trigger for Claude-using framework devs (2026-07-16)

Separate from the deferred welcome-suppression issue above: Val and colleagues who use
Claude Code at a framework-dev checkout (`ApiLogicServer-dev` ancestor directory) wanted
`system/ApiLogicServer-Internal-Dev/dev-architecture.md` loaded every session without
having to remember a phrase — pure friction reduction, no relation to the brief-first
gate other personas depend on, since this file was never part of that gate (internal-dev
only, not Manager-facing).

Landed in `CLAUDE.md`: an unconditional, silent auto-load, gated only on the
`ApiLogicServer-dev` ancestor check, confirmed with one short line ("Dev-architecture
context loaded") — no yes/no prompt (tried first, rejected as chatty), just does it.
Explicitly worded as additive so it can't reproduce the welcome-suppression failure mode
above: it never gates or replaces the normal `.github/copilot-instructions.md`
welcome/activation flow, both can fire off the same first message.

Copilot has no equivalent unconditional-preload mechanism, so it got a parallel but
different treatment: `copilot-instructions.md`'s STEP 3 appends an actual yes/no question
after the welcome message when the same ancestor check matches (Copilot can't silently
read-and-confirm before the user asks anything the way Claude's auto-load does).

**Follow-up, live test (2026-07-16, same day):** confirmed the auto-load is unreliable in
practice — same underlying platform gap as the deferred welcome-print limitation above
(no shipped mechanism forces action on a CLAUDE.md instruction before the model judges
it relevant to the user's actual first message; anthropics/claude-code#25543 territory).
Live repro: opened a fresh session in the correct workspace root (confirmed via
`Manager_workspace.code-workspace`'s `"path": ".."`, breadcrumb `genai-logic > CLAUDE.md`
— not a path bug), said "hi", then "what have you loaded?" — response confirmed
`CLAUDE.md` was in context but described the dev-architecture read as something that
"gets pulled in on activation triggers... or when relevant to a task," i.e. treated as
conditional, not the unconditional first action the instruction asks for. Path and file
content were both correct; only the forced-execution assumption was wrong.

**Fix:** added an explicit fallback trigger phrase ("load dev architecture" /
"load dev-architecture.md") to `CLAUDE.md`, same shape as `copilot-instructions.md`'s
STEP 3 pattern — the auto-load stays as a best-effort attempt (harmless if it fires,
useful when it does), but the phrase is the reliable path. Same lesson as the
"please load copilot-instructions.md" README instruction: on this platform, a
remembered phrase currently beats an unconditional standing instruction for anything
that must reliably happen before the model decides it's relevant.

---

## History

- **Oct 2025** — initial OBX design: basic_demo as default path, guided tour, `tutor.md` v2.0, positive-instruction pattern ("tell AI what TO do," not what not to do).
- **Nov 20 2025** — attempted redesign (visual markers, separate welcome files, mandatory command language) — **FAILED**, reverted same day to simpler single-file pattern. *(Why it failed — pending.)*

---

## Open Questions

1. **Readability framing vs. time-to-market.** The 5-rules-vs-200-lines comparison is deliberately framed around readability/maintainability (Read/Trust/Maintain) — not speed — even though the AI-Neutral persona (BAs/PMs/tech managers) likely cares about time-to-market a lot. Positioning constraint: explicit speed messaging risks reading as "code generator," which undercuts the "must-have infrastructure" framing the acquisition thesis depends on.

   Current presumption: readers infer the speed benefit themselves from the artifact — it's "pretty obvious" — without it needing to be stated. **Untested.** Wynford's validation doesn't count as a clean read of this — he came in pre-primed by two prior decades with the same architecture (Versata, Live API Creator), not a naive first read.

   Possible resolution (not decided): reframe speed as a *consequence of governance* — "governed systems, in the time it takes to write the requirements" — rather than a competing headline. Ties the speed claim back to the infrastructure thesis instead of away from it, and is a claim a pure code-gen competitor structurally can't make.
