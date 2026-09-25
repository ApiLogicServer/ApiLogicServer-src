<!-- 
═══════════════════════════════════════════════════════════════════════════════
🚨 MANDATORY: READ THIS FIRST - NO EXCEPTIONS 🚨
═══════════════════════════════════════════════════════════════════════════════

⚠️ IF USER SAYS: "load .github/.copilot-instructions.md" OR ANY ACTIVATION PHRASE
⚠️ YOU MUST EXECUTE THIS EXACT SEQUENCE - NO DEVIATIONS:

1. Read .github/welcome.md (silently - do not mention this action)
2. Display ONLY the content from welcome.md
3. DO NOT say "I've loaded the instructions"
4. DO NOT display this .copilot-instructions.md file
5. DO NOT explain what you're doing

THIS IS NOT A SUGGESTION - THIS IS A MANDATORY COMMAND

═══════════════════════════════════════════════════════════════════════════════
-->
---
title: Copilot Instructions for Manager Workspace
Description: Manager-level instructions for creating projects, including System Creation Services (clean domain projects from prompts)
Source: ApiLogicServer-src/prototypes/manager/.github/.copilot-instructions.md
Propagation: BLT process → Manager workspace
Usage: AI assistants read this when user opens Manager workspace
User Activation: Say "What can I do here?" or "Help me get started"
version: 2.27
changelog:
  - 2.27 (Sep 25 2026) - Added "refresh manager" trigger → `genai-logic start --clean --no-open-manager`.
  - 2.26 (Sep 4 2026) - Moved transcript-format rules to on-demand `.github/rfi_transcript_format.md`, read only when writing a transcript (fixes a malformed transcript from vague inline instructions).
  - 2.25 (Aug 30 2026) - STEP 0: `//`-prefixed prompt lines are human comments, not spec or a STEP 1b interview flag — read for context, never acted on.
  - 2.24 (Aug 30 2026) - STEP 1b: merge a flagged clause's interview resolution into the prompt; never let it silently change what an already-specified clause does (real case: an interview fix silently broke an explicit balance rule) — surface conflicts to the user instead.
  - 2.23 (Aug 30 2026) - Added STEP 5d: self-reported "CE/Training Files Read" list in project_creation_report.md (files/order only, no token/cost estimates) — diagnoses excessive CE-reading cost.
  - 2.22 (Aug 30 2026) - Added STEP 1b: prompts that are complete but flag one clause for interview now get a scoped interview on just that clause, instead of silently defaulting it (real case: a returns-policy clause got an invented default instead of being asked about).
  - 2.21 (Aug 17 2026) - STEP 6: AI starts the server itself instead of telling the user to press F5 (Codespaces' cached debug config can make bare F5 skip the project-name prompt).
  - 2.20 (Aug 17 2026) - STEP 4: `logic/declare_logic.py` is a stub, not the logic target — real logic goes in `logic/logic_discovery/<use_case_name>.py`.
  - 2.19 (Aug 12 2026) - Method 4 STEP 1 forks when no prompt is provided: offers a Socratic interview (STEP 1a) that produces requirements.md + a verbatim transcript, feeding STEP 5a as if it were a written prompt.
  - 2.18 (Aug 5 2026) - STEP 5a/5b filenames updated to match the CLI's own output: project_creation_prompt.md / project_creation_report.md (STEP 5a overwrites the CLI's inferred prompt with the real one; STEP 5b enriches the baseline report).
  - 2.17 (Jul 16 2026) - User Activation STEP 3: if any ancestor dir is named `ApiLogicServer-dev`, offer to load dev-architecture.md after welcome.md.
  - 2.16 (Jul 16 2026) - Method 2 (`genai-logic genai`) marked SUPER-DEPRECATED; added standalone "PATH RULE for Manager root" section; CLAUDE.md now @-loads this file directly.
  - 2.15 (Jul 2 2026) - STEP 5a: copy the full originating prompt file verbatim to docs/requirements/prompt.md before writing readme.md/ad-libs.md (source file may later change or vanish).
  - 2.14 (Jul 1 2026) - STEP 4: never re-run `genai-logic create` — workflow is DDL → rebuild → logic → seed.
  - 2.13 (Jul 1 2026) - STEP 5 ad-libs.md requires a "Creation Steps" section listing commands actually run.
  - 2.12 (Jun 15 2026) - STEP 4: per-use-case requirements.md (project CE step 8) is required during Method 4, separate from Manager-level STEP 5 provenance files.
  - 2.11 (Mar 18 2026) - Method 4 rewritten as a "stay in Manager" 1-step flow — no workspace switch needed.
  - 2.10 (Feb 23 2026) - Collapsed Method 4: SCS workflow now lives in project CE.
  - 2.9 (Feb 23 2026) - Method 4: starter.sqlite + rebuild-from-database replaces manual create_db_models.py.
  - 2.8 (Feb 23 2026) - Added Method 4 (System Creation Services): domain project from prompt via project CE.
  - 2.7 (Nov 20 2025) - Reverted to simple single-file pattern from basic_demo.
  - 2.6 (Nov 20 2025) - Applied OBX pattern from basic_demo — FAILED.
  - 2.5 (Nov 17 2025) - Strengthened basic_demo detection logic.
  - 2.4 (Nov 2025) - Simplified structure, removed redundant sections.
  - 2.3 (Nov 2025) - Added activation phrases, forcing welcome presentation.
  - 2.2 (Nov 2025) - Initial welcome instructions.
  - 2.1 (Oct 2025) - Added orientation section, friendly tone, conditional Quick Start.
  - 2.0 (Oct 2025) - OBX improvements, strengthen basic_demo as default path.
  - 1.0 (Initial) - Established project creation methods.
---

# GitHub Copilot Instructions for GenAI-Logic (aka API Logic Server) - Project Manager

---

## 👤 FOR USERS: How to Get Started

**When you open this workspace, say:**
- "What can I do here?"
- "Help me get started"
- "What is this workspace?"

This will trigger the appropriate welcome message based on whether you're new or returning.

---

## 🚨 CRITICAL: User Activation Protocol

**ACTIVATION TRIGGERS:**
- "load .github/.copilot-instructions.md"
- "load copilot instructions"
- "help me get started"
- "what can I do here?"
- "what is this workspace?"
- "activate copilot"
- Any similar startup phrase

**MANDATORY RESPONSE SEQUENCE:**

```
STEP 1: Read .github/welcome.md (silently)
STEP 2: Display welcome.md content ONLY
STEP 3: Check if any ancestor directory of the current workspace is literally named
        `ApiLogicServer-dev` (i.e. this is a framework dev checkout, not an end-user
        Manager clone or Codespaces workspace). If so, append ONE line after the
        welcome.md content:
        "Also: load system/ApiLogicServer-Internal-Dev/dev-architecture.md?"
        If the user says yes, read that file and follow its own mandatory load
        sequence (see its header). If no ancestor is named `ApiLogicServer-dev`,
        skip this step entirely — do not mention it.
STEP 4: Check whether the user's message contains ANYTHING beyond the activation
        phrase itself (additional instructions, a pasted script, commands prefixed
        with "!", other requests — on their own line or following the trigger phrase
        in the same message).
        - If there IS more content: continue on to process it now, in this same
          turn, immediately after displaying welcome.md. Do NOT stop and wait for
          the user to ask again — the rest of the message is the next thing to do,
          not a separate future request.
        - If the activation phrase is the ENTIRE message: STOP - do nothing else.
```

> **⚠️ COMMON FAILURE MODE:** a user pastes the activation phrase as the first line of a
> longer message (setup commands, an "implement requirements" instruction, etc.) expecting
> the whole thing to run in one turn. Treating STEP 4's stop as unconditional — even when
> real, actionable content follows the trigger phrase in the same paste — silently drops
> that content and forces the user to re-prompt. Always check for trailing content first.

**✅ CORRECT EXECUTION:**
```
User: "load .github/.copilot-instructions.md"

AI: [reads welcome.md silently - NO OUTPUT]
AI: [displays ONLY this]:

Welcome! This is the **Project Manager** - your workspace for...
[... rest of welcome.md content ...]
```

**❌ FORBIDDEN BEHAVIORS:**
```
User: "load .github/.copilot-instructions.md"

❌ AI: "I've loaded the instructions file..." 
❌ AI: "Here are the contents of .copilot-instructions.md:"
❌ AI: [displays .copilot-instructions.md]
❌ AI: "I'll read the file for you..."
❌ AI: Any meta-commentary about loading or reading files
```

**RATIONALE:**
- Users want to see the **welcome message**, not technical instructions
- This file (.copilot-instructions.md) is for AI context, not user display
- Separation of concerns: welcome.md = user-facing, copilot-instructions.md = AI-facing
- No meta-cognitive confusion about "instructions" vs "content"
- This pattern achieved ~100% success rate in basic_demo testing

**This is the FIRST SCREEN users see - get it right!**

---

## Technical Reference (For AI - Do Not Present Unless Asked)

<br>

## 🎯 Active Project Context

This is a SINGLE shared workspace that may contain MULTIPLE project directories
(e.g. `basic_demo/`, `genai_demo/`, `samples/basic_demo_sample/`, etc.) — there is
no per-project session isolation. Before any file write, `genai-logic` command, or
logic edit, you MUST know which project directory you're operating in.

- **Track it explicitly.** Once a project is created or named by the user, treat it
  as the "active project" for the rest of the session — every subsequent file path
  and command is prefixed with `<active-project>/`.
- **Announce it.** When you act on a project, state which one: e.g. "Active project:
  `genai_demo` — editing `genai_demo/logic/logic_discovery/...`". This makes the
  target visible to the user so a mismatch is caught immediately.
- **Re-confirm on ambiguity.** If the user's request doesn't name a project and
  could plausibly apply to more than one (e.g. "add a field to Customer" when both
  `proj1/` and `proj2/` have a `Customer` table), STOP and ask which project before
  editing anything. Do NOT guess based on which directory you last touched.
- **Switching projects.** If the user names a different project than the current
  active one ("now let's work on `proj2`"), update the active project and announce
  the switch before making any changes.

---

## 📖 Content Organization Protocol

**WHEN USER ASKS: "what are rules", "what is a rule", "explain rules", "why rules"**
**PRIMARY ANSWER**: Respond with exactly this:

---
Rules enforce business policy — multi-table derivations, constraints, and actions like messaging. **LogicBank**, the rule engine, hooks SQLAlchemy's commit event to run them on every transaction — authored as plain Python functions in `logic/logic_discovery/`, readable, version-controlled, and owned like any other source file.

&nbsp;

But unlike procedural code, rules are *declarative* — which has important implications:

&nbsp;

| Property | What it means | Why it matters |
|---|---|---|
| **Auto-reused** | `Customer.balance = sum of unpaid orders` — declared once, enforced over every change path | No per-path handlers to write or miss |
| **Auto-invoked** | Rules fire at every commit, from every caller — you never call them | Can't be forgotten, can't be bypassed |
| **Auto-ordered** | The engine computes dependency order at startup | Add a rule anywhere, it finds its place |

&nbsp;

If it helps: think of a spreadsheet — `B10 = SUM(B1:B9)` isn't called, it *reacts*. Rules react the same way to changes in what they depend on.

&nbsp;

Taken together: 40x less code to write, maintain, and debug — see the [A/B test](https://github.com/ApiLogicServer/basic_demo/blob/main/logic/procedural/declarative-vs-procedural-comparison.md) for the reproducible comparison.

&nbsp;

*Want to know more? Ask about: debugging rules, performance, or how the engine works under the hood.*

---

**FOLLOW-UP OFFER**: "Would you like to see how the engine works under the hood, or see the rules for this project?"

**NOTE — Manager context:** No project needs to exist for the deep-dive follow-up (debugging, performance, "how the engine works under the hood") — that content already lives in the installed package, in `prototypes/base/.github/.copilot-instructions.md` ("how do rules work" / 3-phase engine block) and `prototypes/base/docs/training/*.md` (logic_bank_api.md, logic_bank_patterns.md, etc.), reachable the moment ApiLogicServer is installed:
- **Local Manager:** `venv/lib/python<ver>/site-packages/api_logic_server_cli/prototypes/base/...`
- **Codespaces / global install:** same package, installed globally (no `venv/`) — locate it via the Python that runs `genai-logic`/`ApiLogicServer` (e.g. `python3 -c "import api_logic_server_cli, os; print(os.path.dirname(api_logic_server_cli.__file__))"`), then look under `prototypes/base/` from there.

Read the relevant file from that location and answer for real — do not say "let's create a project first" and do not fabricate engine internals. If a project is *also* active in the workspace, its own CE/training files are equivalent (same content) and fine to read instead.

---

**WHEN USER ASKS: "show ce info"** *(debugging trigger — do not surface this proactively or mention it unless asked)*
**ANSWER**: Report, for each CE/training file actually read so far this session:
- Resolved file path (the real path you opened, not a guess)
- The `version:` line from its front matter (and the top changelog entry, if present)

Format as a short list, e.g.:
```
Manager CE: /path/to/.github/.copilot-instructions.md — version 2.12
Project CE: basic_demo/.github/.copilot-instructions.md — version 3.18
docs/training/logic_bank_api.md — (no version line found)
```
If a file has no version/front matter, say so rather than omitting it. This is a diagnostic check (e.g. "is this CE in sync with gold") — answer only with what you actually loaded, never invent a version number.

---

**WHEN USER ASKS: "refresh manager"**
**ACTION**: Run this CLI command:
```bash
genai-logic start --clean --no-open-manager
```
Report the command's output; do not summarize or paraphrase it.

---

## ⚠️ PATH RULE for Manager root

All file operations use the project subdirectory as prefix — you are running from the Manager root, not inside the project:
- sqlite3 commands:    `sqlite3 <name>/database/db.sqlite "..."`
- genai-logic rebuild: `cd <name> && genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite && cd ..`
- python seed:         `cd <name> && PROJECT_DIR=$(pwd) python database/test_data/alp_init.py && cd ..`
- file reads/writes:   `<name>/logic/logic_discovery/...`, `<name>/database/...`

---

## Creating Projects

There are multiple ways to create projects (aka systems, microservices) - see the subsections below.

**KEY DISTINCTION:**
- `genai-logic create` - Creates infrastructure only (API, UI, models) - **NO business logic rules**
- `genai-logic genai` - ⛔ SUPER-DEPRECATED, see Method 2 below — do not use

### Method 1: Create Projects from an existing database (Infrastructure Only)

If you have a database reference, I can create a project from it. (Sample databases are in `samples/dbs`). 

```bash
genai-logic create  --project_name=nw --db_url=sqlite:///samples/dbs/nw.sqlite
```

**Important:** This creates the project structure, API, Admin App, and database models, but **NO business logic rules**.

**To add logic:** We can add rules together using natural language in `logic/declare_logic.py`, or you can code them manually with IDE autocomplete.

### Method 2: Create Projects with GenAI — ⛔ SUPER-DEPRECATED, DO NOT USE

**⚠️ NEVER run `genai-logic genai` — not even for prompt files. Use Method 4 instead.**

This command is obsolete. It is documented here only for historical reference — do not run it, do not suggest it, do not use it as a fallback even if Method 4 hits an obstacle.

```bash
# ⛔ DO NOT RUN — kept for reference only:
genai-logic genai --using=system/genai/examples/genai_demo/genai_demo.prompt --project-name=genai_demo
```

**Use Method 4 (System Creation Services) instead** for any domain project with database + business logic requirements.

### Method 3: Create Projects with new databases (Manual Approach)

If you provide a description but want to create the database manually:

1. I'll create a sqlite database from your description. I'll be sure to include foreign keys. The system works well with `id INTEGER PRIMARY KEY AUTOINCREMENT`.
2. Then, I'll use the `genai-logic create` command above.
3. If you have logic requirements, we can translate them together using `system/genai/learning_requests/logic_bank_api.prompt`.

### Method 4: New Domain Project from Business Prompt (System Creation Services)

**TRIGGER:** User provides a business domain prompt (multi-line description of tables, rules, constraints) — OR asks to start a new system with no prompt in hand yet (STEP 1 forks below).

**STAY IN THE MANAGER** — do NOT ask the user to open a new workspace. Execute everything here, prefixing all file paths with the project subdirectory.

**MANDATORY SEQUENCE:**

```
STEP 0: Strip `//`-prefixed lines before parsing the prompt as a spec.
   A line starting with `//` (optionally indented) is a comment FOR THE HUMAN READER —
   a note, an alternative, an aside — not part of the domain spec and not an instruction
   to execute. Read it for context (it may clarify intent), but do not implement it,
   ask about it, or treat it as a flagged-for-interview clause the way STEP 1b's
   "interview me..." phrasing is. Distinguish three things a prompt line can be:
     1. Domain spec (schema/rules/use-cases) → execute directly (STEP 2 onward)
     2. Explicit interview flag ("interview me to work out...") → STEP 1b, scoped
     3. `//` comment → read silently, do not act on it, do not mention needing to act
        on it, and do not carry it into project_creation_prompt.md as if it were part
        of the requested spec (STEP 5a copies the prompt verbatim including the comment
        line itself — that's fine, it's provenance of what was literally pasted — but
        the comment's CONTENT must not become a schema/rule decision on its own).
   Example: `// or, use an existing db: Create X from samples/dbs/basic_demo.sqlite.`
   documents an alternative path for a human deciding how to invoke this prompt — it is
   not an instruction to create the project from that database instead of the one
   actually specified in the executable lines below it.

STEP 1: Ask user for project name if not provided (short, snake_case, e.g. allo_dept_gl)

   🗣️ FORK — no prompt provided yet:
   If the user hasn't supplied a prompt (file, paste, or path), ask: "Do you have a
   domain prompt, or would you like to discuss the system and I'll draft one with
   you?" (AI-as-BA)
   - Prompt in hand, fully specified → proceed exactly as today (STEP 2 onward, unchanged).
   - Prompt in hand, but it explicitly asks for an interview on part of it → go to
     STEP 1b (partial interview) BEFORE STEP 2. See below.
   - "Discuss" (no prompt at all) → go to STEP 1a BEFORE STEP 2. Do not create the
     project yet — the interview happens first, in this same Manager conversation,
     with no project directory required (there's no CE to load until the project
     exists, and none is needed yet: the checklist below is self-contained).

STEP 1b: Partial interview (only when a supplied prompt explicitly asks for one)
   Trigger: the prompt is otherwise a complete, ready-to-execute spec (like STEP 2's
   default path), but contains an explicit instruction to interview on one part of
   it — phrasing like "interview me to work out...", "ask me about...", "let's
   discuss...", or similar, attached to a specific clause or sentence, not the whole
   prompt. This is distinct from STEP 1a: STEP 1a is triggered by the ABSENCE of a
   prompt; STEP 1b is triggered by an explicit instruction INSIDE a prompt that is
   otherwise complete. Do not conflate them — a prompt with a STEP 1b instruction is
   not "no prompt provided," and must not silently fall through to the unconditional
   "prompt in hand → proceed as today" branch above, which has no mechanism to honor
   an inline interview request and will default/guess instead (confirmed real failure,
   Aug 2026 — see the CE version-history entry for this STEP for the case that forced
   this fix).
   - Read the ENTIRE prompt first. Execute every clause that is NOT flagged for
     interview exactly as STEP 2 onward would — do not hold the whole project hostage
     to the flagged clause.
   - For each flagged clause, run a short, SCOPED interview using STEP 1a's mechanics
     (ask one topic at a time; constants → SysConfig column; lookup nouns → FK
     inventory; AI/judgment-call phrasing → Request Pattern flag; "different kinds
     of X" → type hierarchy) — but bounded to that clause's ambiguity, not the whole
     domain. Do not re-ask about clauses that were already fully specified elsewhere
     in the prompt.
   - When the flagged clause's interview feels complete, synthesize its resolved
     text and read it back for confirmation, same as STEP 1a — then treat the
     confirmed text as if it had been written into the original prompt at that
     point, and continue into STEP 2 with the now-complete, fully-specified prompt.
   - ⚠️ MERGE, NEVER SILENTLY OVERWRITE an already-fully-specified clause. The
     flagged clause's resolution is allowed to ADD new schema/rules and — when
     genuinely necessary — EXTEND an existing rule (e.g. add a new condition to a
     `where=` clause, add a new column an existing formula should also reference).
     It must NOT replace or invert the semantics of a rule the explicit part of the
     prompt already fully specified, even if the interview's answers technically
     imply a simpler-looking replacement. If resolving the flagged clause seems to
     require changing what an explicit clause DOES (not just adding to it), STOP —
     surface the conflict explicitly and ask the user to choose, the same way the
     interview surfaces any other ambiguity; do not resolve it unilaterally just
     because a plausible-looking fix is available.
     REAL FAILURE CASE (basic_demo_rfi, Aug 2026): the prompt's explicit Check
     Credit clause defined `Customer.balance = sum(Order.amount_total where
     date_shipped is null)` — i.e., shipping an order reduces balance (ship =
     settled). The flagged Returns clause's interview asked "should balance
     decrease on return?", the user said yes, and — correctly noticing that a
     shipped order was already excluded from balance under the existing formula,
     so a naive "decrease balance" action would be a no-op — the run silently
     changed the SUM's `where=` from `date_shipped is null` to `date_returned is
     null` to make the return case work. This fixed the flagged clause but broke
     the explicit one: shipping an order NO LONGER reduces balance at all now
     (only a return does), a behavior change the user never asked for and was
     never asked to confirm. The interview correctly identified a real conflict
     between the flagged clause and an explicit one, then resolved it by quietly
     discarding the explicit clause's behavior instead of surfacing the conflict.
     The two-path choice STEP 1a-style interviews already do (e.g. "keep the
     original formula and add a separate adjustment action" vs. "change the
     formula") must be presented to the user as a decision about the EXPLICIT
     clause's fate, not adjudicated silently in favor of whichever option is
     less code to write.
   - Write the scoped Q&A to `<name>/docs/requirements/<name>-transcript.md`, same file
     STEP 1a would use — if STEP 1a's full-domain interview never ran, this is the first
     and only transcript for the project; if it's layered on top of an already-interviewed
     project, append to the existing transcript rather than overwriting it. Format: read
     `.github/rfi_transcript_format.md` now, first time this file is written this session.
   - This can happen more than once per prompt if multiple clauses are separately
     flagged — run STEP 1b once per flagged clause, in the order they appear.

STEP 1a: Socratic interview (only when the user chose "discuss" above)
   Walk the same ground SCS step 4a-4d extracts from written text, but conversationally.
   Ask one topic at a time, not a wall of questions:
   - Constants: "Is there a rate, threshold, or date that's fixed policy rather than
     user data?" → becomes a SysConfig column.
   - FK inventory: "When you say <noun>, is that a lookup you'd want to browse or
     report on separately?" → becomes an integer FK, not a text code.
   - Request Pattern: if the user describes an AI/email/Kafka-driven decision or a
     judgment call (e.g. "pick the optimal supplier") — flag it for AI resolution,
     don't force it into a formula.
   - Type hierarchy: "Are there different kinds of <thing> that share most fields but
     differ in a few?" → becomes single-table inheritance.
   ⚠️ BATCH, NOT INCREMENTAL — do not alter any schema turn-by-turn as answers land.
      Accumulate understanding across the whole conversation first.
   When the interview feels complete, synthesize a real requirements.md-style
   narrative from it and read it back to the user for confirmation before treating
   it as the prompt. Once confirmed, this synthesized text IS the domain prompt —
   proceed to STEP 2, and it becomes the verbatim content STEP 5a writes to
   project_creation_prompt.md.
   ⛔ ALSO write the raw Q&A transcript to <name>/docs/requirements/<name>-transcript.md
      — once, at the end, after the interview is confirmed (not incrementally per turn).
      This is a companion record showing HOW the requirements were derived (which answer
      surfaced which rule) — do not skip it on the assumption that requirements.md alone
      suffices; a live run showed the transcript itself is something the user wants back.
      Format: read `.github/rfi_transcript_format.md` now, first time this file is
      written this session — do not freelance the format from memory.

   🚨 NAME-COLLISION GUARD — the ONLY collision that matters is the actual create
   target: `<name>/` at the Manager root. Before proceeding:
   - Check whether `<name>/` already exists at the Manager root (the exact path
     `genai-logic create --project-name=<name>` would write to).
   - If — and only if — `<name>/` already exists at the Manager root: do NOT reuse
     or overwrite it. Pick a distinct new name and confirm it with the user before
     STEP 2.
   - A directory of the same (or overlapping) name living under `samples/<name>*`
     is NOT a collision — different containing directory, never the create target.
     Do not rename or substitute the user's requested name just because a
     same-named `samples/` directory exists. Proceed with the user's exact name.
   - `samples/` is READ-ONLY REFERENCE CONTENT regardless. Never run
     `genai-logic create`, `rebuild-from-database`, or edit `models.py`/`logic/`
     inside any `samples/*` directory — even if its name matches the user's
     request. This rule protects `samples/`; it does NOT mean the user's
     requested name must be changed.

STEP 2: Create the nearly-empty project:
   source venv/bin/activate  # local Manager only — skip if venv/ does not exist (e.g. Codespaces/Docker, where genai-logic is pre-installed globally)
   genai-logic create --project-name=<name> --db_url=sqlite:///samples/dbs/starter.sqlite
   (Manager convention: use shared Manager venv; do NOT create a per-project `.venv` unless user explicitly asks)
   ⚠️ If `<name>/` already exists, STOP and ask the user before overwriting —
      do not silently proceed into an existing directory.

STEP 3: Read these files SILENTLY (internalize — do NOT display):
   <name>/.github/.copilot-instructions.md          ← project CE (full subsystem workflow)
   <name>/docs/training/implement_requirements.md       ← schema conventions
   <name>/docs/training/logic_bank_api.md            ← rule API reference
   <name>/docs/training/logic_bank_patterns.md       ← implementation patterns
   <name>/docs/training/RequestObjectPattern.md      ← integration services pattern

STEP 4: Implement the domain prompt using the project CE's System Creation Services workflow.
        ⛔ DO NOT run `genai-logic create` again — the project already exists from STEP 2.
           The workflow is: DDL → rebuild-from-database → logic files → seed. Not create.
        ⛔ `<name>/logic/declare_logic.py` is a generated STUB/fallback entry point, NOT
           where use-case logic belongs. It may already contain rule-shaped scaffolding
           (imports, an empty `declare_logic()`) that looks superficially "done" — it is
           not. Real use-case logic is written ONLY to
           `logic/logic_discovery/<use_case_name>.py` (per file below). Confirmed real
           case (Codespaces, Aug 2026): a model found `declare_logic.py` already had the
           needed rule declarations and treated that as the finished implementation —
           the actual discovery-folder file was never written, and rules silently did not
           load. Finding logic in `declare_logic.py` is not evidence the task is complete;
           always verify `logic/logic_discovery/<use_case_name>.py` exists and loads.
        ⚠️ SCHEMA DESIGN IS LAST — complete ALL pre-DDL analysis before writing any SQL:
           4a. Constant extraction  — identify every rate/threshold/date → SysConfig column
           4b. FK inventory         — identify every lookup entity → integer FK column
           4c. Request Pattern scan — if AI/email/Kafka detected: add request TEXT +
                                      created_on TEXT to Sys* table; make handler-set FKs
                                      nullable; add *_description TEXT input column
           Only after 4a/4b/4c are complete: write DDL, run rebuild-from-database, seed, logic.

        ⛔ For each logic file written in step 8 (`logic/logic_discovery/<use_case_name>.py`),
           also write `<name>/docs/requirements/<use_case_name>/requirements.md` (verbatim
           prompt excerpt for that use case) — see project CE step 8 for details. This is
           separate from, and in addition to, the Manager-level STEP 5 provenance/ad-libs
           files below.

⚠️ CRITICAL PATH RULE — all file operations use the subdirectory as root:
   - File reads/writes:  <name>/database/db.sqlite,  <name>/logic/logic_discovery/...
   - sqlite3 commands:   sqlite3 <name>/database/db.sqlite "..."
   - genai-logic commands: cd <name> && genai-logic rebuild-from-database ...
                           then cd back to Manager root

STEP 5: ⛔ MANDATORY PROVENANCE — before telling the user the project is done:
   a. Copy the full originating prompt file VERBATIM (byte-for-byte, no paraphrase,
      no excerpting) to <name>/docs/requirements/project_creation_prompt.md — this
      is the durable record of what was actually requested; the source file (e.g.
      samples/prompts/<name>.prompt.md) may later be edited or deleted, so
      referencing its path alone is not sufficient provenance.
      NOTE: `genai-logic create` (STEP 2) already writes this file itself — an
      inferred one-liner if no real prompt exists yet. STEP 5a here OVERWRITES it
      with the real prompt, verbatim — do not skip this step just because the file
      already exists from STEP 2.
   b. Write <name>/docs/requirements/project_creation_report.md (provenance: source
      path, date, model, creation commands, schema decisions) — may reference
      project_creation_prompt.md instead of re-explaining what was asked.
      NOTE: `genai-logic create` (STEP 2) already writes a baseline version of this
      file too; STEP 5b here enriches it with the real details listed above.
   c. Write <name>/docs/requirements/ad-libs.md (every assumption or guess made
      beyond the prompt spec).
   Do NOT skip (a) even if per-use-case docs/requirements/<use_case>/requirements.md
   excerpts already exist (STEP 4) — those are partial, per-rule-file excerpts;
   project_creation_prompt.md is the complete original text, preserved once at the
   project root.

   d. Append a "CE/Training Files Read" list to project_creation_report.md — a
      lightweight self-report of which CE and training files this run actually
      loaded, in order, with approximate size (e.g. "docs/training/logic_bank_api.md
      — read at STEP 4, ~15 KB"). This is a log of files ALREADY READ during this
      run — do not open, re-open, or measure any file specifically to produce this
      list; that would add exactly the reading overhead this is meant to make
      visible, not new overhead of its own. If you don't already know a file's
      approximate size from having read it, omit the size rather than checking.
      Purpose: diagnosing excessive CE-reading cost across runs (e.g. comparing
      whether a small build triggered the same full training-file set as a large
      one) — not a token/cost/time metric, which this assistant has no reliable
      access to; do not estimate or invent those numbers.

STEP 6: Start the server YOURSELF to confirm it runs — do NOT tell the user to press F5 here.
   Run (from Manager root): cd <name> && python api_logic_server_run.py &
   Confirm via curl/logs that it started cleanly, then stop it.
   ⚠️ WHY NOT F5: VS Code caches the last-used debug config per workspace. In a fresh
   Codespace, bare F5 can silently resolve to a stale/wrong target instead of prompting
   for the project name — confusing for a first-time user with nothing to compare against.
   (Confirmed live, Aug 2026: F5 skipped the runProjectName prompt in Codespaces; explicitly
   picking "API Logic Server Run..." via Cmd/Ctrl+Shift+P → "Debug: Select and Start
   Debugging" worked immediately and fixed F5 for the rest of that session.) Verifying via
   a plain run sidesteps this entirely — no debug-config resolution involved.
   Then tell the user:
   "Your project is in <name>/. To work on it further, open it as a workspace. To run it
   with the debugger (breakpoints, step-through), use Cmd/Ctrl+Shift+P → 'Debug: Select and
   Start Debugging' → 'API Logic Server Run...' the first time — after that, F5 will work
   directly."
```

**✅ What this achieves:** User gives you a prompt → you create, scaffold, and implement the full system without them ever switching workspaces.

**❌ FORBIDDEN:**
- Asking user to open the project first
- Using file paths without the `<name>/` prefix
- Running `genai-logic rebuild-from-database` from Manager root (must cd into project)

## Working Together

When you ask "what should I do now?" or similar:

1. **I'll recommend starting with basic_demo** using the command above
2. **I'll use CLI commands** (genai-logic) not Docker scripts for project creation
3. **I'll point you to sample databases** in `samples/dbs/` for examples
4. **I'll show you GenAI examples** in `system/genai/examples/` for AI-generated projects
5. **We'll follow the 20-minute workflow** described in the main README

## Available Databases
- `basic_demo` - Best for first-time users
- `starter.sqlite` - One `sys_config` table (global settings row); use for new domain projects — no schema contamination, and introduces the sys_config pattern for runtime-configurable rates/limits
- `nw.sqlite` - Northwind sample
- `chinook.sqlite` - Music store sample  
- `classicmodels.sqlite` - Classic car models sample

