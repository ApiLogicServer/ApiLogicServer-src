---
title: Developer Architecture for BLT Manager Workspace
Description: Enables AI assistants to be co-designers for GenAI-Logic features
Source: ApiLogicServer-src/prototypes/manager/system/ApiLogicServer-Internal-Dev/dev-architecture.md
Propagation: BLT process → Manager workspace
Usage: AI assistants read this to understand project structure, development workflow, and recent additions
version: 2.17
changelog:
  - 2.17 (Jul 2026) - Two fixes found live-debugging basic_demo: (1) opt_locking checksum
    mismatch on Decimal/float round-trip (false-positive lock failures on every Item update);
    (2) removed serverReadyAction from prototypes/base/.vscode/launch.json - unreliable on
    first F5 in a fresh VS Code window, retained only in prototypes/manager/.vscode/launch.json
    where the Manager's long-lived warm window makes it reliable
  - 2.16 (Jul 2026) - Noted nw_sample doubles as Val's manual pre-release LogicBank
    regression test, not just a teaching/demo project - patterns that look like tech debt
    (declare_logic.py monolith, as_exp= string param, custom calling= Kafka function,
    wildcard imports, the Ready/cascade-add pattern) may be deliberately preserved to
    exercise specific LB code paths across releases. Do not modify nw_sample's domain
    logic without checking with Val first. See samples/nw_sample/review.md ("Also: LB
    Regression Test").
  - 2.15 (Jul 2026) - Ready Flag pattern (Training Pattern Categories #4): documented the
    underlying engineering reason it exists - min-cardinality constraints ("Order must have
    Items") can't be reliably enforced at insert time through SAFRS due to cascade-add PK
    timing (parent PK is DB-computed, not stamped into children until flush). Ready defers
    the cardinality check to an explicit later state transition; the workaround was then
    recognized as better UX independent of the technical constraint. See samples/nw_sample/
    review.md for the full writeup, samples/nw_sample/logic/declare_logic.py:187-195 for
    the code.
  - 2.14 (Jul 2026) - Type hierarchy pattern: STI vs joined/concrete CTI comparison, GL preference for STI, CE location pointers (project CE step 4d, manager CE 4d checklist)
  - 2.13 (Jun 2026) - Added README.md broken-link check to create_codespaces_mgr.py (Step 2h, gates --push/--release). First 2 attempts were unusable (236, then still-noisy false positives) until scope was narrowed to README.md only - see "README Broken-Link Check" section for the false-positive traps and what actually works
  - 2.12 (Jun 2026) - LogicBank 1.31.04 multi-relationship fix: child_role_name now works correctly on Rule.sum/count/copy (and link()) when 2+ relationships connect the same parent/child classes. Documented in prototypes/base/docs/training/logic_bank_api.md (user-facing CE) - was previously undocumented even though the parameter existed. See "Multi-Relationship Fix (LogicBank)" section
  - 2.11 (Jun 2026) - opt_locking.py: fixed non-deterministic hash() checksum (sha256) and null S_CheckSum on POST (after_flush stamping) - see "Optimistic Locking Fixes" section
  - 2.10 (Jun 2026) - Noted LogicBank's own internals-doc system (CLAUDE.md + system/LogicBank-Internal-Dev/dev-architecture.md, bug investigation docs, release-management.md) now exists in the org_git/LogicBank sibling clone, and cross-references this file + prototypes/base CE
  - 2.9 (Jun 2026) - Documented org_git/ sibling-clone convention; install-ApiLogicServer-dev.sh now also clones LogicBank (rule engine source) as a sibling for dev visibility — not yet wired to pip -e or venv override
  - 2.8 (Jun 2026) - Flagged base-vs-basic_demo CE drift incident: write/test new CE in base first, basic_demo is a copy not the source
  - 2.7 (Jun 2026) - Noted clean/genai-logic as a BLT output sibling (pristine baseline, not for working in)
  - 2.6 (Jun 2026) - Added "Sibling Workspace: codespaces_mgr (cs-mgr)" section - how it's generated from .devcontainer-codespaces/, what's excluded, and why its Manager CE has extra Active Project / name-collision guards
  - 2.5 (Jun 2026) - Added Demo readme mapping (Manager-readme.md front-matter / create_readme.py) gotcha section
  - 2.4 (Apr 2026) - Renamed from copilot-dev-context.md to dev-architecture.md
  - 2.3 (Mar 2026) - Added mandatory load sequence: also read Manager + prototype copilot-instructions
  - 2.2 (Feb 2026) - Subsystem creation - use rules, data model hints 
  - 2.1 (Feb 2026) - Eval AI from RS
  - 2.0 (Oct 2025) - Added AI-Guided Training section (tutor.md v2.0, OBX improvements, design philosophy)
  - 1.0 (Initial) -  Established workspace structure, GenAI prompt engineering, development workflow
---

<!-- 
═══════════════════════════════════════════════════════════════════════════════
🚨 MANDATORY: WHEN THIS FILE IS LOADED — READ THESE FILES SILENTLY FIRST
═══════════════════════════════════════════════════════════════════════════════

When the user says "load system/ApiLogicServer-Internal-Dev/dev-architecture.md"
or any similar activation phrase, you MUST silently read all three files below
BEFORE responding. Internalize all three. Do not display them.

1. .github/.copilot-instructions.md
   → Manager-level instructions: how to create projects, Method 4 (SCS), welcome protocol

2. venv/lib/python3.13/site-packages/api_logic_server_cli/prototypes/base/.github/.copilot-instructions.md
   → Prototype/project-level instructions: full architecture guide, 13 services,
     logic patterns, stamping, security, testing — what AI can do inside a created project
   ⚠️ READ-ONLY reference copy — do NOT edit this file directly.
      Gold source (edit here): org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/.github/.copilot-instructions.md
      Same for Manager CE:      org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager/.github/.copilot-instructions.md
      The venv copy is downstream — it reflects gold only after a pip install/BLT run.

3. This file (dev-architecture.md)
   → BLT workspace context: directory structure, gold sources, development workflow

SEQUENCE:
  STEP 1: Read .github/.copilot-instructions.md (silently)
  STEP 2: Read venv/lib/python3.13/site-packages/api_logic_server_cli/prototypes/base/.github/.copilot-instructions.md (silently)
  STEP 3: Read this file fully (silently)
  STEP 4: Confirm to user with ONE short sentence, e.g.:
          "Context loaded — Manager instructions, prototype CE, and BLT workspace context are active."

DO NOT display any of the three files. DO NOT summarize them. Just confirm and await instructions.
═══════════════════════════════════════════════════════════════════════════════
-->

# Context Restoration: BLT Manager Workspace

**Purpose:** This file re-establishes AI assistant context after BLT runs regenerate this workspace.

&nbsp;

## 🎯 YOU ARE HERE: BLT Manager (Nested Workspace)

**Current Location:** `~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/`

This is the **BLT Manager** - a nested workspace that gets regenerated by the Build-Load-Test process.

**Directory Structure:**
```
~/dev/ApiLogicServer/ApiLogicServer-dev/          # Seminal Manager (stable)
├── build_and_test/
│   └── ApiLogicServer/                           # ← YOU ARE HERE (BLT Manager)
│       ├── samples/                              # Sample/test projects
│       ├── venv/                                 # Shared venv for test projects
│       ├── .github/.copilot-profile.md           # This file
│       └── docs/training/                        # Training materials
└── org_git/
    ├── ApiLogicServer-src/                       # Framework source (edit here)
    ├── LogicBank/                                 # Rule engine source (sibling, cloned for dev convenience)
    ├── Docs/                                     # Documentation project
    └── codespaces_mgr/                           # Codespaces trial repo (see below)
```

**`org_git/` convention — sibling clones of related repos:** `org_git/` exists so every
git repo related to ApiLogicServer dev lives as a sibling, cloned side-by-side, not buried
inside `ApiLogicServer-src/` or installed only as an opaque pip dependency. `install-ApiLogicServer-dev.sh`
clones `ApiLogicServer-src`, `Docs`, and `LogicBank` here for a fresh dev setup (see
`system/ApiLogicServer-Internal-Dev/install-ApiLogicServer-dev.sh`). Today the `LogicBank`
clone is a reference checkout — not wired to `pip install -e` or any venv override — but
it is not bare source: `org_git/LogicBank/` has its own self-contained CE/internals doc
system mirroring this one, entry point `CLAUDE.md` at its root, pointing into
`system/LogicBank-Internal-Dev/dev-architecture.md` (engine architecture, Versata design
lineage, release coupling with GenAI-Logic, Executable Requirements context) plus sibling
bug-investigation docs (`multi-relationship-bug.md`, `dragons-deferred-adjustment.md`) and
`release-management.md`. That doc explicitly cross-references back into *this* file and
into `prototypes/base`'s CE (`.copilot-instructions.md`, `docs/training/logic_bank_api.md`
— the "Rosetta Stone") — so the two repos' dev-architecture docs are meant to be read
together when a bug spans the GL/LB boundary, not independently.

**Key Facts:**
- This workspace is **regenerated** with each BLT run
- Sample projects live here for testing
- Has its own venv shared by test projects
- Framework changes happen in `org_git/ApiLogicServer-src/`
- Rule engine source lives in `org_git/LogicBank/` — related project, sibling clone, same convention
- **CE gold sources** (edit here, not in venv):
  - Project CE: `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/.github/.copilot-instructions.md`
  - Manager CE: `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager/.github/.copilot-instructions.md`
  - Propagation: org_git → pip install/BLT → venv copy → created projects

**`clean/genai-logic` — also produced by BLT.** Sibling of this BLT Manager, at
`~/dev/ApiLogicServer/ApiLogicServer-dev/clean/genai-logic`. Same BLT run regenerates both;
this is the **pristine, never-worked-in** install — no test-project edits, no manual venv
tweaks — useful as a baseline to diff against when this (working) Manager's state is in
question. Not a git repo, like this one.

**🚨 CRITICAL: README Files - Gold Source is Docs Repo**
- **Gold source:** `org_git/Docs/docs/` (NOT `ApiLogicServer-src/prototypes/`)
- **copy_md() function:** Fetches from GitHub Docs repo (or local Docs if dev), converts mkdocs → markdown
- **Affected files:** Any file containing "readme" or "README" (readme_vibe.md, readme_ai_mcp.md, Tutorial.md, Sample-Integration.md, etc.)
- **Implication:** Changes to README files must go to **Docs repo**, not prototypes - prototypes get overwritten on project creation
- **See:** [Architecture-Internals.md#docs-used-in-project-creation](https://apilogicserver.github.io/Docs/Architecture-Internals/#docs-used-in-project-creation)

&nbsp;

## 🌌 Sibling Workspace: codespaces_mgr (aka "cs-mgr")

**`org_git/codespaces_mgr`** is a trimmed-down Codespaces trial repo generated FROM this
local-mgr via `.devcontainer-codespaces/create_codespaces_mgr.py` — not a full mirror
(excludes `basic_demo/`, `scaffold/`, `tests/`, `dockers/`, `demo_customs/`, `demo_eai/`, `venv/`).

**See `.devcontainer-codespaces/CodeSpaces.md`** for generation details, the curated
`SYNC_PATHS`, Codespaces-only overrides, and a running log of live-Codespaces-session
fixes (including why Manager CE has extra "Active Project Context" / name-collision
guards for its single-persistent-workspace flow).

&nbsp;

## 📚 Complete Architecture Documentation

**For comprehensive technical context, read:**

### [Architecture-Internals.md](https://apilogicserver.github.io/Docs/Architecture-Internals/)

This document contains **everything** you need to understand the system:

1. **Technology Lineage** - 40+ years of proven history:
   - Wang Labs PACE (6,000+ customers, 1980s-1990s)
   - Versata ($3.4B startup, Fortune 500 deployments, 1990s-2010s)
   - API Logic Server (modern cloud-native evolution, 2020s-present)

2. **Declarative Architecture** - The NL → DSL → Engines pattern:
   - Why rules are mandatory (correctness guarantee)
   - Dependency chains and automatic completeness
   - Database, API, UI, Logic engines

3. **Nested Manager Architecture** - Critical development structure:
   - Seminal Manager vs. BLT Manager (nested)
   - Development workflow: edit → BLT → test
   - Why this architecture exists

4. **Installation & Development Procedures** - How to work with the system:
   - Manager installation (`install-ApiLogicServer-dev.sh`)
   - Running BLT (Build-Load-Test)
   - Critical smoke test procedures
   - Ongoing development workflows

5. **Cross-References** - Complete navigation map to all documentation

**👉 START HERE when establishing context in a new session.**

&nbsp;

## 🧭 Documentation Navigation Map

### For AI Assistants Working on Framework Internals:
- **[Architecture-Internals.md](https://apilogicserver.github.io/Docs/Architecture-Internals/)** - Complete technical architecture (read this first)
- **[Medium Article](https://medium.com/@valjhuber/declarative-genai-the-architecture-behind-enterprise-vibe-automation-1b8a4fe4fbd7)** - Architectural rationale and NL→DSL→Engines pattern
- **`api_logic_server_cli/cli-internals.md`** (gold source) - Internal developer reference: project creation mechanics (base clone + overlay pattern), clone_and_overlay_prototypes file roles, manager.py existing-workspace short-circuit, key files to edit for common tasks. **Read this before working on project creation, prototypes, or manager workspace.**

### For Creating New Projects:
- **Manager-level `.copilot-instructions.md`** - How to CREATE projects (in workspace root)
  - **Location:** `prototypes/manager/.github/.copilot-instructions.md`
  - **Size:** ~86 lines
  - **Scope:** Creating projects ONLY (3 methods: existing DB, GenAI, new DB)
  - **Purpose:** Instructions for creating new projects with `genai-logic create` commands
  - **Does NOT contain:** Project customization, logic patterns, testing, security, etc.

### For Working Within Created Projects:
- **Project-level `.copilot-instructions.md`** - How to EXTEND/CUSTOMIZE projects (auto-generated in each project)
  - **Location:** `prototypes/base/.github/.copilot-instructions.md` (template) and `prototypes/basic_demo/.github/.copilot-instructions.md` (tutorial version)
  - **Size:** ~740 lines
  - **Scope:** Complete architecture guide for EACH created project
  - **Purpose:** 13 Main Services (what AI can do in a project):
    1. **Run Project** - F5 debug, `api_logic_server_run.py`
    2. **Adding Business Logic** - Translate NL → LogicBank rules (sums, formulas, constraints, events)
    3. **Discovery Systems** - Auto-load logic from `logic/logic_discovery/*.py`, APIs from `api/api_discovery/*.py`
    4. **Automated Testing** - Behave tests with BLT reports (requirements traceability)
    5. **Adding MCP** - Enable MCP client UI with `genai-logic genai-add-mcp-client`
    6. **Configuring Admin UI** - Edit `ui/admin/admin.yaml` for customization
    7. **Create React Apps** - `genai-logic genai-add-app` for custom UIs
    8. **Security - RBAC** - `als add-auth` for SQL/Keycloak, `security/declare_security.py` for grants
    9. **Custom API Endpoints** - Add routes in `api/customize_api.py`
    10. **B2B Integration APIs** - Complex endpoints with Row Dict Mappers for partner integration
    11. **Customize Models** - Add tables, attributes, derived fields
    12. **Adding Events** - Row events for integrations (Kafka, webhooks, etc.)
    13. **Critical Patterns** - React component best practices, null-safe constraints, test repeatability
  - ⚠️ **CRITICAL:** These are TWO DIFFERENT FILES - never replace the per-project version with the manager version!
  - 🚨 **PROPAGATION PROBLEM:** Changes to project-level instructions must be carefully copied to both `prototypes/base/.github/.copilot-instructions.md` AND `prototypes/basic_demo/.github/.copilot-instructions.md`
  - 🪤 **`base` is the one that matters — `basic_demo` is only a testing/tutorial convenience.** Real-world incident (Jun 2026): a governance/A-B-test answer block existed only in `basic_demo` — added there during CE drafting/testing — and was never ported to `base`. Everyone validating the answer kept testing against `basic_demo` (the easy, fast-to-load file) and got "excellent" results for months, while every real customer project (created from `base`) silently lacked the content. **When drafting or testing new CE content, write/verify it in `base` first** — `basic_demo` should only ever be a copy of what's already proven in `base`, never the original.
  - 📋 **OBX PATTERN (v2.3, Oct 2025):** Use **positive instructions** for AI behavior:
    - ✅ **Works:** "When user asks to read instructions, respond with the Welcome section content below"
    - ❌ **Fails:** "Do NOT add preamble" or relying on structure alone
    - **Theory:** Tell AI what TO do, not what NOT to do
    - **Result:** Clean welcome message without meta-commentary ("I've read the instructions...")
- **`docs/training/logic_bank_api.prompt`** - LogicBank API reference (Rosetta Stone for rules)
- **`docs/training/testing.md`** - Behave testing guide (1755 lines, read BEFORE creating tests)

### For End Users:
- **[API Logic Server Documentation](https://apilogicserver.github.io/Docs/Doc-Home/)** - Complete user guide
- **[Installation Guide](https://apilogicserver.github.io/Docs/Install/)** - Setup procedures
- **[Tutorial](https://apilogicserver.github.io/Docs/Tutorial/)** - Step-by-step learning

### For AI-Guided Training (New Feature):
- **`basic_demo/tutor.md`** - AI assistant guide for conducting 30-45 min hands-on tour
  - **Version:** 2.0 (762 lines, October 2025)
  - **Purpose:** "Message in a bottle" for AI assistants - enables guided discovery learning
  - **Method:** Provocation-based (e.g., "how did it know ORDER has a foreign key to Customer?")
  - **Philosophy:** Users learn by DOING (hands-on tour), not reading docs or taking quizzes (Versata approach)
  - **Structure:** 9 sections with timing checkpoints (15 min, 35 min), concrete metrics (48 vs 200+ lines)
  - **Key Additions in v2.0:** Spreadsheet analogy, procedural comparison (BUG FIX examples), context for schema commands, three ways to add logic (Discovery/IDE/Chat), MCP server integration
  - **Location:** `prototypes/basic_demo/tutor.md` (template), propagates to created `basic_demo` projects
  - **Invocation:** User says "Guide me through basic_demo" → AI reads tutor.md → conducts tour
  
- **Design Philosophy - Why Provocation Over Instruction:**
  - **Problem with traditional training:** PowerPoint → quiz/assessment approach tests memorization, not understanding
  - **Versata insight:** "Stop killing people with PowerPoint; identify critical skills, design lab to DO it"
  - **Discovery learning:** Ask provocative questions that force pattern recognition ("How did it know ORDER references CUSTOMER?")
  - **"Aha moments" over rote learning:** User discovers foreign keys exist, then learns they're essential for multi-table logic
  - **Spreadsheet analogy:** Excel user understands formulas → multi-table database is "Excel for related tables"
  - **AI as training partner DURING the lab:** Not quiz after, not docs before - real-time guidance while doing
  - **Result:** 30-45 min hands-on experience creates deeper understanding than hours of documentation reading

- **v1.0 → v2.0 Evolution (Battle-Tested Refinements):**
  - **v1.0 (595 lines):** Initial design based on architecture understanding
  - **Live testing:** User spent "several hours with your cousin testing and revising" actual tours
  - **v2.0 (+506 net lines):** Added based on what users actually needed during tours:
    - **Spreadsheet analogy** - Non-technical users needed familiar mental model
    - **Procedural comparison** - Show 48 vs 200+ lines WITH concrete BUG FIX examples (not just line counts)
    - **Context for commands** - Why `add-cust` exists (schema variability, new users discover structure)
    - **Three ways to add logic** - Discovery file (recommended), IDE autocomplete, or Chat
    - **Timing checkpoints** - 15 min at Security, 35 min at Q&A (helps pace the tour)
    - **MCP server mention** - Claude Desktop integration for external AI access
    - **Best practices** - `logic/logic_discovery/` organization pattern
    - **Short response guidance** - "One idea per interaction" prevents overwhelming new users
  - **Key learning:** Initial version was too instruction-heavy, v2.0 adds more context and concrete examples

- **`add-cust` Mechanism for Tutor** - Progressive feature addition during guided tour:
  - **Purpose:** Add pre-built customizations progressively during tour (avoids GenAI unpredictability, ensures working examples)
  - **Battle scars:** Also serves as **error recovery** - if users make mistakes during tour, `add-cust` restores database integrity and gets them back on track
  - **Usage in tutor:** Two `add-cust` commands progressively add features:
    1. **First `add-cust`** (from `customizations/` folder) → adds security (RBAC filters) + check credit logic (5 rules), **restores database to known-good state**
       - `logic/declare_logic.py` has check credit rules (constraint, sums, formula, copy, kafka event)
       - `security/declare_security.py` has role-based filters
       - `database/db.sqlite` restored with clean data
    2. **Second `add-cust`** (from `iteration/` folder) → adds schema change (Product.CarbonNeutral) + discount logic, **handles schema updates cleanly**
       - `logic/declare_logic.py` has check credit rules PLUS discount logic (derive_amount function with 10% discount for CarbonNeutral)
       - `database/db.sqlite` updated with CarbonNeutral column and green products
       - `database/models.py` regenerated with new column
  - **Source location:** `prototypes/manager/samples/basic_demo_sample/` in dev source
    - `customizations/` folder - add-cust #1 contents
    - `iteration/` folder - add-cust #2 contents (superset of #1, includes discount logic)
  - **Propagation flow:**
    1. Dev source: `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager/samples/basic_demo_sample/`
    2. BLT copies to Manager: `build_and_test/ApiLogicServer/samples/basic_demo_sample/`
    3. BLT installs to venv: `venv/.../api_logic_server_cli/prototypes/manager/samples/basic_demo_sample/`
    4. During tutor: `add-cust` executes from venv, copies to user's `basic_demo/` project
  - **Key insight:** `add-cust` is a tutor utility, not a production feature - copies pre-built working examples to demonstrate patterns reliably AND recovers from user errors
  - **Maintenance:** When updating add-cust content:
    - Update `customizations/` for add-cust #1 changes
    - Update `iteration/` for add-cust #2 changes (must include everything from #1 plus new content)
    - Both folders in `prototypes/manager/samples/basic_demo_sample/` (dev source)
    - BLT propagates to venv

- **OBX (Out-of-Box Experience) Design** - Manager → Project flow optimization (October 2025):
  - **Manager README:** "🚀 First Time Here? Start with basic_demo" section (clear default path)
  - **Manager .copilot-instructions.md:** "CRITICAL: ALWAYS start" directive (no choices, single path)
  - **Project README:** "🤖 Ready to Explore? Recommended: Guide me through" (guided tour as primary option)
  - **Project .copilot-instructions.md:** "🎯 Most Common Next Steps" (5 succinct items at top)
  - **Goal:** Eliminate friction/choice paralysis, make basic_demo → guided tour the clear default
  - **Problem addressed:** Users didn't automatically know to start with basic_demo, didn't default to guided tour
  - **Solution:** Strengthen every touch point in the journey to push toward the optimal path
  - **Flow:** Install → Open Manager → Create basic_demo → Auto-opens → "Guide me through" → 30-45 min tour

&nbsp;

## 👤 Current Maintainer

**Val Huber**
- **Wang Labs PACE**: Designed and led the business rules architecture, co-invented (in parallel with Ron Ross) the declarative rules paradigm and execution engine
- **Versata**: CTO, designed and lead scaling the rules technology to J2EE and the web
- **API Logic Server**: Architect and lead developer, modernizing proven patterns for cloud-native Python/React stack, the use of GenAI, and current IDEs/deployment practices.

**Expertise:** 40+ years leading business rules technology evolution - inventor of declarative multi-table derivations, constraint propagation, and rule execution engines.

&nbsp;

## 🌐 AI-Based Evaluation - Context Engineering Export

**Purpose:** Making internal Context Engineering (CE) materials publicly available for external AI-assisted evaluation.

### The Architecture

**The Rosetta Stone (RS)** - LogicBank API reference embedded in project-level `.copilot-instructions.md`:
- **Source:** `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/.github/.copilot-instructions.md`
- **Size:** ~740 lines (includes complete LogicBank rule syntax, patterns, testing guide references)
- **Propagation:** Copied to every created project's `.github/.copilot-instructions.md`
- **Purpose:** Trains AI assistants working within projects to correctly translate NL → LogicBank rules

### Exporting CE Materials for Online Evaluation

**Script:** `org_git/Docs/sync_ce_to_docs.sh`

**What it does:**
1. **Copies bootstrap:** `.copilot-instructions.md` → `Eval-copilot-instructions.md` (includes RS)
2. **Copies 12 training files:** `docs/training/*.md` → `Eval-*.md`
   - logic_bank_patterns.md, logic_bank_api.md, testing.md, probabilistic_logic.md, etc.
3. **Transforms references:** Internal links `docs/training/*.md` → `Eval-*.md`
4. **Places in Docs:** `org_git/Docs/docs/` → Published at `apilogicserver.github.io/Docs/`

**Result:** 2,599+ lines of CE materials accessible online without requiring installation.

### The Evaluation Workflow

**Bootstrap prompt** (from `org_git/Docs/docs/Eval.md`):
```
I'm evaluating GenAI-Logic. Here are the resources:
1. https://www.genai-logic.com
2. https://apilogicserver.github.io/Docs/Eval-copilot-instructions/
3. https://apilogicserver.github.io/Docs/Integration-MCP-AI-Example/

Help me understand what this actually does - I want facts, not sales pitch.
```

**What happens:**
1. User's AI reads `Eval-copilot-instructions.md` (contains Rosetta Stone + architecture)
2. AI follows links to other `Eval-*.md` files as needed (patterns, testing, etc.)
3. AI analyzes materials and forms independent technical conclusions
4. AI answers user's specific questions (not a canned pitch)

### Why This Works

**Independent AI analysis, not vendor persuasion:**
- External AIs (Claude, ChatGPT, Gemini) analyze the same technical materials
- They reach consistent conclusions (4.8-5.0 stars on InfoQ challenge)
- Conclusions emerge from observable architecture, not marketing claims
- If claims were false ("cows jump over the moon"), AI would reject them

**The CE materials are credible because:**
- Created through Socratic process (Val showed artifacts, AI analyzed/questioned)
- Contain senior-level technical reasoning (dependency graphs, failure modes, trade-offs)
- Survived active AI scrutiny during creation
- Focus on facts (40X code reduction, 200 lines → 5 rules) not hyperbole

### Maintenance Workflow

**When updating CE materials:**
1. **Edit source:** `ApiLogicServer-src/prototypes/base/.github/.copilot-instructions.md` or `docs/training/*.md`
2. **Test locally:** BLT creates projects with updated CE
3. **Sync to Docs:** Run `cd org_git/Docs && ./sync_ce_to_docs.sh`
4. **Verify:** Check `git diff docs/Eval-*.md`
5. **Commit to Docs:** `git add docs/Eval-*.md && git commit`
6. **Publish:** Docs site rebuild makes materials available online

**Critical distinction:**
- **Internal use:** CE materials train AI assistants working *within* projects
- **External use:** Same materials enable prospects to evaluate GenAI-Logic *through* their AI
- **Same content, dual purpose:** Context engineering for internal productivity + external credibility

### Pull-Based Documentation Strategy (Feb 2025)

**Problem solved:** Initial approach pushed 1745 lines at evaluators ("drink from fire hose"). ChatGPT truncated responses mid-evaluation. Users needed control over discovery pace.

**Core Strategy: ONE SCREEN + AI AS GUIDE**

**Architecture:**
1. **Eval-welcome.md** (~40 lines) - Minimal entry point
   - Two prompts (Prompt 1: infrastructure, Prompt 2: logic)
   - Closes with: "I have some key concepts you'll probably want to explore. Just ask."
   - No detailed explanations, FAQs, or resource lists
   
2. **Evaluation Checklist** (in `.copilot-instructions.md`) - Structured discovery system
   - 15 items grouped: Core Understanding → Key Features → Hands-On → Deep Dives → Critical Questions
   - First item: "What IS this?" - Explains 4 layers (Infrastructure gen → Rules engine → Context Engineering → AI Codegen)
   - Critical for addressing "is it AI or infrastructure?" confusion
   
3. **AI as Docent** - Museum guide pattern
   - User asks → AI shows checklist
   - User picks item → AI retrieves relevant content (via content mapping)
   - After each item: Mark as ☑, ask "What else have you got for me?"
   - AI adapts suggestions based on role (architect vs developer)

**Implementation:**
- **Menu item #12** in capabilities list: "Explore evaluation concepts" 
- **Content mapping** directs AI to specific sections (Admin UI TL;DR, API overview, FAQ answers, etc.)
- **Checklist tracking** maintains progress visibility

**Why This Works:**
- **Pull-based:** User controls depth through questions (not pushed a 1745-line document)
- **Layered disclosure:** Surface (one screen) → Structure (checklist) → Content (item-by-item) → Reference (full doc)
- **Trust through agency:** User sees what's available, chooses what to explore, controls pacing
- **Discovery not prescription:** Curiosity-driven for web evaluators, task-driven for IDE developers
- **AI maintains momentum:** Checklist provides structure, content mapping ensures consistent answers

**Entry Paths:**
- **Web evaluators:** Eval.md bootstrap → "Show me Eval-welcome" → curiosity-driven exploration
- **IDE developers:** Menu item #12 in capabilities list → task-driven query
- **Both:** Lead to same checklist system, different motivations

**Key Insight:** Explicit prompts work better than implicit protocols. "Start with a quick overview by showing me [URL]" beats "FIRST RESPONSE PROTOCOL" sections.

**Lesson Learned:** User agency beats comprehensive reference. Let evaluators control their learning journey instead of forcing march through all content.

&nbsp;

## 🤖 AI Integration Architecture - Four Distinct Modes

**API Logic Server uses AI in four distinct ways:**

### 1. Manager Context Engineering (Claude/Copilot)
**Purpose:** AI assistance for **creating projects**  
**Location:** Manager workspace `.copilot-instructions.md` (~86 lines)  
**What it does:** Guides AI to help developers:
- Create projects from existing databases
- Create projects from natural language (via GenAI CLI)
- Create projects from scratch
- Navigate Manager workspace structure

**Example:** User asks "Create a project from my Postgres database" → Copilot guides through `genai-logic create` command

### 2. Project Context Engineering (Claude/Copilot)
**Purpose:** AI assistance for **customizing projects** after creation  
**Location:** Per-project `.copilot-instructions.md` (~740 lines) + `docs/training/` folder  
**What it does:** Guides AI to help developers:
- Add business logic (translate NL → LogicBank rules)
- Add custom API endpoints
- Reorganize database schemas (Alembic migrations)
- Configure Admin UI, security, testing
- Create React apps

**Example:** User asks "Add a rule that Customer.balance = sum of unpaid orders" → Copilot translates to LogicBank formula

**Key Materials:**
- Rosetta Stone: Complete LogicBank API reference (sums, formulas, constraints, events)
- Training files: logic_bank_api.md, testing.md, implement_requirements.md, RequestObjectPattern.md
- Pattern library: Discovery systems, Request Pattern, null-safe constraints

### 3. GenAI CLI Services (OpenAI Fine-Tuned ChatGPT)
**Purpose:** Automated project **generation from natural language prompts**  
**Technology:** Fine-tuned ChatGPT (not Claude)  
**Commands:**
- `genai-logic create --using="natural language"` - Generate complete project from prompt
- `genai-logic logic-translate --using-file=docs/logic` - Generate rules from NL requirements

**What it does:** Transforms natural language → working projects:
- Parses NL requirements
- Generates SQLAlchemy models (with derived columns for rules)
- Generates LogicBank rules (sums, formulas, constraints)
- Generates test data
- Returns structured JSON (WGResult with models, rules, test_data)
- Note: this is PE (prompt engineering); the items above are CE (Context Engineering built into projects)

**Example Input:**
```
Create a system with customers, orders, items and products.
Check Credit: Customer.balance = sum of unpaid orders, 
balance must not exceed credit_limit.
```

**Example Output:** Complete project with 4 tables, 5 rules, working API, Admin UI, test data

**Key Insight:** Generates **specifications** (rules), not procedural code. Rules executed by proven engine.

**Prompt Engineering:**
- Templates: `system/genai/prompt_inserts/` (sqlite_inserts.prompt, logic_inserts.prompt, etc.)
- Training examples: `org_git/ApiLogicServer-src/tests/genai_tests/logic_training/`
- Fine-tuning data: logic_training/ft.jsonl

### 4. AI Rules in Running Systems (Probabilistic Logic)
**Purpose:** **Runtime AI-powered business rules** in deployed applications  
**Technology:** OpenAI/Claude/etc. called from LogicBank formulas  
**Location:** Project `logic/` folder  

**What it does:** Business rules that invoke AI for decisions:
- Conditional formulas: `if condition → call AI, else → deterministic calculation`
- AI handlers: Reusable functions that call LLM APIs
- Request Pattern: Audit trails for AI decisions (SysXxxReq tables)

**Example:**
```python
Rule.formula(
    derive=models.Order.freight_estimate,
    calling=lambda row, old_row, logic_row:
        call_ai_for_freight(row) if row.is_international 
        else row.weight * standard_rate
)
```

**Key Materials:**
- `docs/training/probabilistic_logic_guide.md` - Implementation patterns
- `docs/training/genai_logic_patterns.md` - Framework integration
- Request Pattern for audit trails

**Use Cases:**
- Dynamic pricing based on market conditions
- Risk assessment for loan approvals
- Fraud detection scores
- Freight cost estimation for unusual routes

---

&nbsp;

## 🤖 AI Assistant Quick Reference

### Two Working Modes:
- **Developer/Maintainer** - You working on framework internals, debugging, testing
- **Simulating End Users** - You testing product workflows, creating demos, validating UX

### Context Establishment Protocol:
1. **Read [Architecture-Internals.md](https://apilogicserver.github.io/Docs/Architecture-Internals/)** for complete technical context
2. Identify which documentation to consult based on task:
   - Framework development → Architecture-Internals.md
   - Project creation → Manager-level `.copilot-instructions.md` (86 lines, in prototypes/manager/)
   - Project customization → Project-level `.copilot-instructions.md` (740 lines, in prototypes/base/)
   - Adding logic → `docs/training/logic_bank_api.prompt`
   - Creating tests → `docs/training/testing.md`
3. **CRITICAL:** Never confuse the two `.copilot-instructions.md` files:
   - Manager version = how to CREATE projects (small, workspace-level)
   - Project version = how to CUSTOMIZE projects (large, per-project with architecture details)
4. When your role is unclear, I'll ask: "Are you simulating an end user or working on internals?"

### Key Principles:
- **Assume deep technical expertise** - Technology refined over 40+ years
- **Focus on efficient execution** - Less explanation, more action
- **Respect the architecture** - Patterns represent battle-tested solutions from thousands of deployments
- **Check training materials** - `logic_bank_api.prompt` and `testing.md` prevent common AI mistakes

### Communication Tone Guidelines:
- **Confident but NEVER hyperbolic** - Make only claims backed by specific, measurable evidence
- **Cite concrete metrics** - "200 lines → 5 rules (40X)" not "transforms years into days"
- **Reference historical facts** - "40+ years, 6,000+ deployments" establishes credibility
- **Avoid unfounded superlatives** - No "revolutionary", "game-changing", or time-compression claims without data
- **Be specific** - "Creates working API in 5 seconds" vs "drastically reduces development time"
- **NEVER claim** - Time compression like "30-40 years → 3-4 days" - these are unmeasurable and unfounded
- **DO claim** - Specific productivity gains with evidence: "40X code reduction", "instant API from database"

&nbsp;

## 🤖 GenAI Prompt Engineering Architecture

### Overview: ChatGPT Project Creation Pipeline

The `genai-logic create` command uses **fine-tuned ChatGPT** to translate natural language requirements into complete working projects. The system uses **prompt engineering** to surround user input with structured instructions.

### Key Locations

**Prompt Templates:** `system/genai/prompt_inserts/`
```
├── sqlite_inserts.prompt                    # Main orchestrator for DB creation
├── sqlite_inserts_model_test_hints.prompt   # SQLAlchemy class generation rules
├── logic_inserts.prompt                     # LogicBank rule generation
├── logic_translate.prompt                   # NL → LogicBank translation (existing DB)
├── graphics.prompt                          # Dashboard chart generation
├── response_format.prompt                   # WGResult Pydantic schema
└── web_genai.prompt                         # WebGenAI-specific (15+ tables)
```

**Training Examples:** `org_git/ApiLogicServer-src/tests/genai_tests/logic_training/`
```
├── genai_demo.prompt                        # Check Credit + No Empty Orders
├── ready_flag.prompt                        # Ready Flag pattern (3 use cases)
├── emp_depts.prompt                         # Chain Up: sum salaries, constrain budget
├── graduate.prompt                          # Cardinality: counts with thresholds
├── products.prompt                          # Qualified Any: severity checks
├── honor_society.prompt                     # Complex cardinality with qualified counts
└── *.txt / *_corrected_prompt.txt           # Expected outputs and corrections
```

**Test Examples:** `system/genai/examples/`
```
├── genai_demo/                              # Complete example with iterations
├── airport/                                 # Complex 10+ table system
├── emp_depts/                               # Simple aggregation pattern
└── time_tracking_billing/                   # Real-world scenario
```

### The Prompt Assembly Process

**User Input:**
```
Create a system with customers, orders, items and products.

Use case: Check Credit
1. Customer.balance <= credit_limit
2. Customer.balance = Sum(Order.amount_total where date_shipped is null)
3. Order.amount_total = Sum(Item.amount)
4. Item.amount = quantity * unit_price
5. Item.unit_price = copy from Product.unit_price
```

**System Surrounds With:**

1. **Model Generation Instructions** (`sqlite_inserts_model_test_hints.prompt`):
   - Use autonum keys for ALL tables (including junction tables)
   - Create classes, never tables (Class names singular, capitalized)
   - **CRITICAL:** "If you create sum, count or formula Logic Bank rules, then you MUST create a corresponding column in the data model"
   - No check constraints (logic uses rules instead)
   - Foreign key columns (not relationship names) for test data

2. **Logic Generation Instructions** (`logic_inserts.prompt`):
   - "Use LogicBank to enforce these requirements (do not generate check constraints)"
   - "be sure to update the data model and *all* test data with any attributes used in the logic"

3. **Response Structure** (`response_format.prompt`):
   ```python
   class WGResult(BaseModel):
       models: List[Model]              # SQLAlchemy classes
       rules: List[Rule]                # LogicBank declarations
       test_data: str                   # Python test data creation
       test_data_rows: List[TestDataRow]
       test_data_sqlite: str            # INSERT statements
       graphics: List[Graphic]          # Dashboard queries
       name: str                        # Suggested project name
   ```

**Result:** ChatGPT returns structured JSON with models, rules, and test data that:
- Has `Customer.balance`, `Order.amount_total`, `Order.item_count` columns created automatically
- Contains LogicBank rules for all derivations
- Includes test data with derived attributes pre-initialized

### Key Insight: Model + Logic Co-Generation

**Unlike existing database projects**, GenAI creation can **modify the data model** to support logic:

- **Derived attributes materialize:** `Customer.balance`, `Order.amount_total`, `Product.total_ordered`
- **Count columns appear:** `Order.item_count` for existence checks
- **Qualified counts split:** `Product.notice_count` + `Product.severity_five_count`

This is why the training examples emphasize:
> "If you create sum, count or formula Logic Bank rules, then you MUST create a corresponding column in the data model."

### Training Pattern Categories

The `logic_training/` examples teach ChatGPT these patterns:

1. **Chain Up (Aggregation → Constraint)**
   - `emp_depts`: Department.total_salary = sum(Employee.salary); salary <= budget
   - `genai_demo`: Customer.balance = sum(orders); balance <= credit_limit

2. **Counts as Existence Checks**
   - `genai_demo`: Order.item_count = count(Items); can't ship if == 0
   - Creates both derivation AND validation

3. **Cardinality Patterns (Qualified Any)**
   - `products`: Total notices + severity 5 notices; constraint if orderable
   - `graduate`: Probation count + sick days; constraint for graduation
   - Pattern: Multiple counts (total + qualified) with complex conditions

4. **Ready Flag**
   - `ready_flag`: Multi-use-case with conditional aggregations
   - Customer.balance only sums orders where `ready == True AND date_shipped is None`
   - Product.total_ordered only sums items where `ready == True`
   - **Why `Ready` exists — min-cardinality vs. SAFRS cascade-add timing:** `Ready` was
     originally an engineering workaround, not a pure UX choice. Minimum-cardinality
     constraints ("an Order must have at least one Item") are supported via
     `Rule.commit_row_event` — but reliably enforcing them **at insert time**, through
     SAFRS, has never worked cleanly. When a client posts a parent + children in one
     nested request (Order + Items), the parent's PK is DB-computed (autoincrement).
     Each child needs that PK **cascade-added** — stamped into its own FK column — before
     it counts as "attached." The PK isn't assigned until flush, and SAFRS's nested-insert
     handling + LogicBank's row-logic timing don't reliably line up to guarantee the
     child-count check runs after cascade-add has stamped every child, while still early
     enough to reject the transaction atomically. (`nw_sample`'s own code comment
     confirms half of this: "the after_flush event makes Order.Id available" — even the
     parent's own PK isn't visible to rule code until after flush.)
     **The resolution:** don't enforce cardinality at insert — defer the check to an
     explicit, later state transition (`Ready`, or shipping). See
     `samples/nw_sample/logic/declare_logic.py:187-195` (`do_not_ship_empty_orders`, a
     commit event gated on `Ready == True` or `ShippedDate is not None`, checked against a
     reactive `Rule.count`). What started as a workaround for this SAFRS/cascade-add
     limitation was then recognized as better UX in its own right — orders naturally want
     a draft/staging phase before being finalized for shipping. Full writeup:
     `samples/nw_sample/review.md` ("Origin Story: Min-Cardinality Constraints and Why
     Ready Exists").
   - **`nw_sample` doubles as Val's manual pre-release regression test for LogicBank
     itself** (run before every LB release) — not just a teaching/demo project. This
     means patterns in `nw_sample`'s domain code that look like tech debt (single large
     `declare_logic.py` instead of `logic_discovery/`, `as_exp=` string param, custom
     `calling=` Kafka function, wildcard imports) may be **deliberately preserved to keep
     exercising specific LogicBank code paths/timing across releases** — not oversights
     to clean up. Same likely applies to the `Ready`/cascade-add pattern above and to
     `test/api_logic_server_behave/features/place_order.feature`'s scenarios (probably
     the actual pass/fail gate, not just documentation). Do not modify `nw_sample`'s
     domain logic, models, or admin.yaml without checking with Val first — see
     `samples/nw_sample/review.md` ("Also: LB Regression Test") for the full caveat.

5. **Chain Down (Copy/Formula)**
   - Item.unit_price = copy(Product.unit_price)
   - Item.ready = Order.ready (formula propagation)

### CLI Commands Using This System

**Create from natural language:**
```bash
genai-logic create --project-name=my_system --using="<natural language>"
# Internally: assembles prompts → ChatGPT → parses WGResult → generates project
```

**Translate logic (existing DB):**
```bash
genai-logic logic-translate --project-name=. --using-file=docs/logic
# Uses logic_translate.prompt to convert NL in docs/logic → rules in logic/logic_discovery/
```

### Fine-Tuning Files

**Training Data:** `logic_training/ft.jsonl`
- JSONL format for ChatGPT fine-tuning
- Generated from prompt/response pairs
- ~374KB with all pattern examples

**Script:** `logic_training/create_json_l.py`
- Converts `*.prompt` + `*.txt` → JSONL entries
- Format: system message, user message (prompt), assistant message (response)

### Common Pitfalls (Why Corrections Exist)

Several `*_corrected_prompt.txt` files show typical AI mistakes:

1. **Wrong cardinality:**
   - `airport.prompt`: Asked for "airplane's passengers" but meant "flight's passengers"
   - AI can't count passengers on an Airplane (no direct relationship)
   - Correction: Count passengers on Flight, constrain by Airplane.seating_capacity

2. **Constraint depends on derived flag:**
   - `products.prompt` initially: "product is orderable IF no severity 5 notices"
   - Problem: Makes orderable a derived value, then uses it in constraint
   - Correction: "RAISE ERROR if orderable == True AND has severity 5 notices"
   - Pattern: Flag is input, constraint uses it (not derived from constraint conditions)

3. **Negative condition logic:**
   - Must use: `not(row.flag and bad_condition)`
   - Not: `row.flag → requires good_condition` (harder for AI to translate)

### Why This Architecture?

**Traditional GenAI code generation problems:**
- Generates 200+ lines of procedural code
- Misses corner cases (foreign key changes, cascading updates)
- Creates technical debt (unmaintainable spaghetti)

**Declarative GenAI solution:**
- Generates **specifications** (5 rules), not code (200 lines)
- Rules executed by proven engine (40+ years, 6,000+ deployments)
- Engine handles ALL change paths automatically (no corner cases missed)
- Natural language → DSL → Runtime engine (not NL → procedural code)

**Critical difference:** The AI doesn't need to "think through" all possible change paths. It translates requirements to rules, and the engine provides correctness guarantee through automatic dependency analysis and chaining.

&nbsp;

## � Python Environment: How venv, PYTHONPATH, and the SRA Work

> **Scope:** Simple generated projects (standard Manager-child layout). Advanced configs (Azure, Docker, iCloud paths, custom venv locations) have additional complexity covered separately.

### Design objective: Manager owns the shared venv; projects inherit it

The standard layout is:

```
ApiLogicServer/          ← Manager (owns the venv)
├── venv/                ← ONE shared venv for all projects
├── basic_demo/          ← child project  (uses ../venv)
├── customs_app/         ← child project  (uses ../venv)
└── my_project/          ← child project  (uses ../venv)
```

**Why:** venv setup is a frequent source of user error and confusion — wrong Python version, missing activation, packages installed in the wrong environment. The shared-venv design eliminates that entire class of problem: users install once into the Manager's venv, and every child project inherits it automatically. There is nothing per-project to install, activate, or get wrong.

**How it's wired:** The generator writes `python.defaultInterpreterPath: "${workspaceFolder}/../venv/bin/python"` (Mac/Linux) or the Windows equivalent into each project's `.vscode/settings.json`. The `"python"` key in each server launch config in `.vscode/launch.json` is the literal VS Code variable `${command:python.interpreterPath}` — no generator substitution needed. VS Code resolves this at runtime from the workspace's selected interpreter (driven by `python.defaultInterpreterPath`), making it fully platform-agnostic.

**When it doesn't apply:** If a project is nested more than one level below the Manager (e.g., `Manager/custom_apps/my_project/`), the `../venv` reference in `settings.json`'s `python.defaultInterpreterPath` resolves incorrectly. The user must manually adjust it to the correct depth (e.g., `"${workspaceFolder}/../../venv/bin/python"`). Since `launch.json` derives its interpreter via `${command:python.interpreterPath}` from `settings.json`, fixing `settings.json` is sufficient — no separate `launch.json` edit needed. Documented in `Project-Env.md`.

### The one rule: get the venv Python binary right — everything else follows

When VS Code (or a terminal) launches `python api_logic_server_run.py` using the venv's Python binary, the venv's `site-packages` are already on `sys.path` automatically (Python's standard activation). The server then does:

```python
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_path)                # adds project dir for relative imports
```

That is all that is needed. There is **no need to set `PYTHONPATH`, `VIRTUAL_ENV`, or `PATH`** as environment variables — they were never read by the server.

### How VS Code resolves the interpreter (four separate mechanisms)

| Mechanism | File | What it controls |
|---|---|---|
| `python.defaultInterpreterPath` | `.vscode/settings.json` | Default shown in status-bar picker; used by Pylance |
| `"python"` key in launch config | `.vscode/launch.json` | Interpreter actually used by F5 / debugpy |
| `python.terminal.activateEnvironment` | `.vscode/settings.json` | Auto-activates venv in every new terminal |
| `python.envFile` → `.env` | `.env` | Env vars injected before launch — **not** interpreter selection |

**The status-bar picker** sets `python.defaultInterpreterPath`. Without a `"python"` key in `launch.json`, F5 also uses this (via a per-machine cache). On a new or moved machine the cache is empty → VS Code falls back to system Python → `import flask_sqlalchemy` fails. Pinning `"python"` in `launch.json` eliminates this failure mode entirely.

**The root `.env` file** (generated by `api_logic_server.py`) was historically written with `VIRTUAL_ENV`, `PATH`, and `PYTHONPATH`. These have no effect on interpreter selection and actively break `PATH` on some platforms because `.env` has no variable substitution (`$PATH` is passed as a literal string). The fix is to stop generating those lines — or stop generating `.env` at all (see `proposed_env_changes_drop_env.md`).

### App configuration: `config/default.env`

The running server loads `config/default.env` via `python-dotenv` in `config/config.py`:

```python
load_dotenv(path.join(basedir, "default.env"))
```

This is where `SECURITY_ENABLED`, `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, etc. live. The root `.env` is irrelevant to the server.

### How the Admin App (SRA) is located

`ui/admin/admin_loader.py` → `get_sra_directory()` resolves in this order:

1. **Env override** — `os.environ.get("APILOGICPROJECT_SRA", 'ui/safrs-react-admin')` (unusual; only set in special configs)
2. **Local project copy** — `ui/safrs-react-admin/robots.txt` exists (project has its own SRA copy)
3. **Venv — the normal case** — `from api_logic_server_cli.create_from_model import api_logic_server_utils`; the SRA static files are inside the `api_logic_server_cli` package in `site-packages`

Step 3 is just a normal Python import — it works because **the venv Python binary is running**, so `api_logic_server_cli` is already on `sys.path`. No `PYTHONPATH` setting, no `APILOGICPROJECT_APILOGICSERVERHOME` needed.

The `except` fallback (tries `APILOGICSERVER_HOME` → `args.api_logic_server_home` → `HOME`) handles environments where the CLI is **not** installed in the venv (certain Azure/Docker configs). Not the normal dev case.

### Design decision: pin `"python"` in `launch.json` using `${command:python.interpreterPath}` (Feb 2026)

> **Reversed from earlier note.** Testing confirmed that `python.defaultInterpreterPath` alone does not reliably drive F5 on new or moved projects — the picker cache is empty, VS Code falls back to system Python, and `import flask_sqlalchemy` fails.

All five server launch configs in `prototypes/base/.vscode/launch.json` use the literal VS Code variable `"python": "${command:python.interpreterPath}"` — no generator substitution. VS Code resolves this at runtime from the workspace's selected interpreter (which comes from `python.defaultInterpreterPath` in `settings.json`).

**Why this works cross-platform:** `${command:python.interpreterPath}` derives from `python.defaultInterpreterPath`, which is already substituted with the platform-correct path at creation time in `settings.json`. No `bin` vs `Scripts` distinction needed in `launch.json`.

**Why not `sys.executable`:** `sys.executable` is the absolute path of the Python used to run the generator — baked in at creation time, breaks on any other machine.

**Subfolder caveat:** If `settings.json`'s `python.defaultInterpreterPath` is wrong (project nested deeper than one level below the Manager), `${command:python.interpreterPath}` will also resolve incorrectly. Fix `settings.json` — `launch.json` follows automatically. Documented in `Project-Env.md`.

**Do add `"python": "${command:python.interpreterPath}"` to all server launch configs in `launch.json` templates** — no generator substitution needed; the value is a literal VS Code variable.

### Known cosmetic issue: `python.analysis.extraPaths` in pre-created samples

The template correctly contains the placeholder `"ApiLogicServerVenvSitePackages"` which the generator substitutes with the correct absolute path at creation time. Pre-created sample projects committed to the repo (e.g., `basic_demo`) have the generating machine's absolute path baked in. On another machine this causes Pylance red squiggles (unresolved imports in the editor) but has **zero runtime impact** — F5 and the server are unaffected.

**Leave this alone.** Fixing it in committed samples risks introducing errors for cosmetic gain. Regenerating the project on any machine produces the correct value automatically.

### `terminal.integrated.profiles.*` removed (Feb 2026, tested)

The custom `"venv"` terminal profile that sourced `venv_init.sh` on startup has been **removed** from `prototypes/base/.vscode/settings.json` and the generator no longer creates `venv_init.sh`. Verified working in `basic_demo`: terminal opens with venv active, F5 works.

**Replacement:** `"python.terminal.activateEnvironment": true` (already present) does the same job without the fragility. The old custom profile broke on any path containing spaces because VS Code expands `${workspaceFolder}` before passing the string to the shell's `-c` flag, and the shell then splits on spaces.

### Template files to keep accurate

This understanding should be reflected in two source files in `org_git/ApiLogicServer-src/`:

| File | What to verify |
|---|---|
| `api_logic_server_cli/api_logic_server.py` | `.env` generation: should not write `VIRTUAL_ENV`/`PATH`/`PYTHONPATH` (gated by `if create_env_file := False`) |
| `api_logic_server_cli/prototypes/base/.vscode/settings.json` | No `terminal.integrated.profiles.*` (breaks paths with spaces); `python.defaultInterpreterPath` = `ApiLogicServerPython` placeholder; no `python.envFile` |

&nbsp;

## �🔄 Development Workflow

**Source Repository:** https://github.com/ApiLogicServer/ApiLogicServer-src

**Local Dev Path:** `/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src`

**Workflow:**
1. Edit framework code in `org_git/ApiLogicServer-src/`
2. Run BLT from Seminal Manager (rebuilds, tests, regenerates this workspace)
3. Test with sample projects in this workspace
4. Sync templates back to `ApiLogicServer-src`
5. Push to GitHub

**🚨 CRITICAL Exception - README Files:**
- **Gold source:** `org_git/Docs/docs/` - NOT ApiLogicServer-src prototypes
- **Affected:** readme_vibe.md, readme_ai_mcp.md, Tutorial.md, Sample-Integration.md, etc.
- **Why:** Users read docs without installing; copy_md() fetches from Docs on project creation
- **copy_md() transformations** (mkdocs → standard markdown):
  - Relative image paths `images/foo.png` → full GitHub raw URLs
  - `!!! pied-piper` / `!!! note` admonitions → `>` blockquotes or plain text
  - `{:target="_blank"}` link attributes stripped
  - Result written to project `readme.md` on project creation
- **Source file naming:** Docs source filename = project readme source, declared in front matter `source:` field
  - e.g., `org_git/Docs/docs/Sample-Basic-EAI.md` → `demo_eai/readme.md`
  - e.g., `org_git/Docs/docs/Sample-Basic-Demo.md` → `basic_demo/readme.md`
- **Editing rule:** Always edit the Docs source in **mkdocs format** — never edit the generated `readme.md` for permanent changes (it is overwritten on project creation)
- **Workflow for README changes:**
  1. Edit in `org_git/Docs/docs/` (e.g., `Sample-Basic-EAI.md`) using mkdocs syntax
  2. Test locally (mkdocs serve)
  3. Commit to Docs repo
  4. Run BLT - copy_md() will fetch updated docs and regenerate readme.md
  5. Test generated projects have correct READMEs

**🚨 Demo readme mapping (`Manager-readme.md` front-matter) — ⚠️ tricky, easy to get wrong:**
- Demo projects (`demo_customs_clvs`, `demo_customs_surtax`, `demo_allo_*`, `basic_demo_*`, etc.) get a **project-specific** readme instead of the generic one — driven entirely by data, not code
- **`org_git/Docs/docs/Manager-readme.md`** front-matter has a table of `<prefix>: <readme-basename>` lines, e.g.:
  ```yaml
  demo_customs: Customs-readme
  demo_customs_surtax: Customs-readme-surtax
  demo_allo: Sample_Allo_Dept_GL_readme
  basic_demo: Sample-Basic-Demo
  ```
- **`create_readme.py`** (`read_mgr_readme()` + `create_readme()`) reads this table, **sorts by prefix length descending**, and uses the **first prefix where `project_name.startswith(prefix)`** — renames the project's `readme.md` → `readme_standard.md`, then `copy_md()`s `<readme-basename>.md` over it
- **The trap:** `startswith()` matching means a new project whose name extends an existing prefix (e.g. `demo_customs_surtax` extends `demo_customs`) will **silently** match the old, shorter prefix's readme — wrong content, no error. This is exactly how `demo_customs_surtax` ended up with the CLVS readme for months.
- **Checklist when adding a demo whose name extends an existing prefix:**
  1. Create its specific gold readme in `org_git/Docs/docs/<New-Readme>.md`
  2. Add a **new, longer** prefix line to `Manager-readme.md` (e.g. `demo_customs_surtax: Customs-readme-surtax`) — do **not** rename/remove the shorter existing entry, other projects may rely on it as a fallback
  3. No code change needed in `create_readme.py` — length-descending sort + first-match-wins already prefers the more specific entry
  4. Regenerate the affected project's `readme.md` (via `copy_md()`, or by hand-applying its mkdocs→markdown transforms) and verify the new mapping resolves
- **See also:** [Architecture-Internals.md#docs-used-in-project-creation](https://apilogicserver.github.io/Docs/Architecture-Internals/#docs-used-in-project-creation)

**BLT (Build-Load-Test):**
- Rebuilds API Logic Server from dev source
- Creates ~18 test projects with validation
- Critical smoke test before pushing to GitHub
- Results in `tests/results.txt` and `tests/failures.txt`

**⚠️ Post-BLT: warm the bytecode cache (Python 3.13 + oracledb 2.5+)**

After BLT reinstalls packages, the first `genai-logic` invocation takes 20-30s while Python compiles `.pyc` files for new Cython extensions (oracledb, sqlalchemy). On macOS this is compounded by Gatekeeper verifying new `.so` files. Run this once after BLT to pre-warm everything:
```sh
python -m compileall venv/lib/python3.13/site-packages/api_logic_server_cli/ \
  venv/lib/python3.13/site-packages/sqlalchemy/ \
  venv/lib/python3.13/site-packages/oracledb/ \
  -q -x "fragments|genai/reference"
```
After this, `genai-logic` starts instantly. Only needed once per BLT.

**🎯 CRITICAL: Prototype System & Project Creation**

**How Projects Are Created:**

When you run `genai-logic create`, the CLI reads **templates (prototypes)** from the installed package:

```
venv/lib/python3.13/site-packages/api_logic_server_cli/
├── prototypes/
│   ├── base/                    # Template for all projects (genai-logic create)
│   │   ├── .github/
│   │   │   └── .copilot-instructions.md    # 740+ lines - Context Engineering
│   │   ├── logic/
│   │   ├── api/
│   │   ├── database/
│   │   └── docs/training/       # Universal training materials
│   ├── basic_demo/              # Special tutorial project template
│   │   ├── .github/
│   │   │   └── .copilot-instructions.md    # Tutorial-specific version
│   │   └── tutor.md             # AI-guided tour
│   └── manager/                 # Manager workspace template
│       ├── .github/
│       │   └── .copilot-instructions.md    # 86 lines - Creating projects
│       └── samples/basic_demo_sample/      # add-cust content
```

**The Flow:**
1. **Dev Source:** `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/`
2. **BLT Install:** Copies to `venv/lib/.../api_logic_server_cli/prototypes/`
3. **Runtime:** `genai-logic create` reads from **venv location**, copies to new project
4. **Result:** New project contains `.copilot-instructions.md` + `docs/training/` from venv prototypes

**Why This Matters:**

- ✅ **Immediate testing:** Edit venv prototypes → test instantly with `genai-logic create`
- ✅ **No BLT required:** Changes in venv take effect immediately for project creation
- ⚠️ **Temporary:** Changes in venv lost on next BLT run (must propagate to dev source)

**Pattern Propagation Impact:**

Your architectural choices in prototypes become templates for all future projects:
- ✅ **Proven patterns propagate:** Get schema design, logic architecture, or API patterns right once → all created projects benefit
- ❌ **Anti-patterns replicate:** Mistakes in prototypes (no autoincrement, procedural events, custom APIs without audit) copy to every new project
- 🎯 **Training material updates spread:** Improve CE in prototypes/base/docs/training/ → all new projects get better guidance

**Development Workflow for CE Changes:**

1. **Quick iteration / venv test (NOW):**
   Edit directly in the installed venv — changes take effect immediately, no BLT required.  This applies to any file under `venv/lib/python3.13/site-packages/api_logic_server_cli/`, including:
   - Prototypes: `prototypes/base/.github/.copilot-instructions.md`, `prototypes/base/.vscode/launch.json`, `prototypes/base/.vscode/settings.json`, etc.
   - Generator: `api_logic_server.py`
   - Any other CLI source file

   Test: `genai-logic create --project-name=test_project --db_url=...`

   ⚠️ **Risk:** Changes in venv are lost on next BLT run.  Propagate back to `org_git/ApiLogicServer-src/` before running BLT.

2. **Permanent propagation (LATER):**
   - Copy changes to: `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/.github/.copilot-instructions.md`
   - Run BLT: Reinstalls to venv, propagates everywhere
   - Commit to GitHub: Survives future BLT runs

**Special Cases:**
- **basic_demo:** Has its own prototype with tutorial-specific CE (must update separately)
- **docs/training/:** Universal materials, same for all projects (update in prototypes/base/)
- **README files:** Exception - come from Docs repo via copy_md(), NOT from prototypes

**Propagating Changes to Source:**
- **Copilot Instructions:** Use `system/ApiLogicServer-Internal-Dev/propagate_copilot_changes.py`
  - Copies changes from `tests/ApiLogicProject/.github/.copilot-instructions.md` → source prototype
  - Usage: `python3 build_and_test/ApiLogicServer/system/ApiLogicServer-Internal-Dev/propagate_copilot_changes.py`
  - Extracts sections between title and "Key Technical Points"
  - Ensures edits propagate to future project creations
- **README Files:** Manual update required in Docs repo (see above)
- **Other Files:** Copy manually or create similar propagation scripts in `system/ApiLogicServer-Internal-Dev/`

&nbsp;

### 🌐 WebGenAI (WG) — Separate Build Cycle

**What WG is:** A web app for business users (not devs) to create projects from natural language descriptions. Users define a data model and logic; WG generates, runs, and hosts the project. Projects can be exported as a full ALS project folder for developer extension.

**How it creates projects:** WG invokes the same `api_logic_server_cli` generator internally — same prototypes, same `.vscode/settings.json` template, same CE files. But WG has its own installed copy of the generator inside its own environment.

**Key gotcha: WG has its own build/deploy cycle.** 
Running BLT updates the ALS CLI in the local `venv/` — but **does NOT update WG**. After making generator changes (e.g., fixing `settings.json`, dropping `.env`), WG must be rebuilt separately for those changes to affect WG-created/exported projects.

- Exported projects (e.g., `AcademicManagementSystem/`) were generated by whichever WG version was installed at export time
- If an exported project has old-style terminal profiles / `.env`, it just means WG was not yet rebuilt
- Fix: rebuild WG after BLT

**WG build scripts** (in `org_git/ApiLogicServer-src/docker/webgenie_docker/`):
- **Local build** (for testing): `build_web_genie_local_license.sh`
- **Deploy to Docker Hub**: `build_web_genie.sh`

**Required fixes to make a WG-exported project run locally (until WG template is fixed):**

In `.vscode/settings.json`:
1. Fix `python.defaultInterpreterPath` → `"${workspaceFolder}/../venv/bin/python"` (WG bakes in `/usr/local/bin/python`, the Docker path)
2. Remove `python.envFile` line (no `.env` exists locally; causes VS Code warning)
3. Remove `terminal.integrated.profiles.osx/linux` blocks (source `venv_init.sh` which hardcodes `/usr/local/bin/activate` — fails on Mac)
4. Remove `terminal.integrated.defaultProfile.osx/linux` lines
5. Remove `python-envs.defaultEnvManager: ms-python.python:system` and `python-envs.pythonProjects: []` lines (overrides interpreter selection, fights with `defaultInterpreterPath`)

Also: delete root `.env` if present (all lines are commented out but `python.envFile` warning is annoying).

In `.vscode/launch.json` — add `"python": "${command:python.interpreterPath}"` to each server configuration (`ApiLogicServer`, `ApiLogicServer DEBUG`, verbose variants). `python.defaultInterpreterPath` in settings is NOT sufficient for F5 — the `"python"` key in launch.json is required and **confirmed working (Feb 2026)**. The `${command:python.interpreterPath}` variable derives from `python.defaultInterpreterPath` at runtime; no hardcoded path, no platform issues.

Open a **new terminal** after saving — existing terminals retain the old broken profile.

**WG-specific prototype overlay:** `prototypes/genai_demo/` is merged on top of `prototypes/base/` for WG projects. Triggered by env var `APILOGICPROJECT_IS_GENAI_DEMO` or `project_name == 'genai_demo'`.

**BLT workspace layout:**
```
build_and_test/ApiLogicServer/
├── webgenai/
│   ├── webg_projects/    # WG-managed projects (by-ulid, public, wgadmin)
│   ├── webg_config/
│   └── webg_temp/
├── AcademicManagementSystem/  # example WG-exported project
```

&nbsp;

## 🏛️ Governance Layer (May 2026)

Three generated report types that together provide full traceability from NL requirements through to test execution. All generated from code — no manual documentation effort.

### The Three Reports

**1. Logic Flow** (`logic_flow_<req>.md`) — "what does this system do?"
- Audience: developer onboarding, code review, stakeholder communication
- Content: NL spec (from module docstring) + inline SVG diagram + numbered rule summary
- Generator: `system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py`
- Output: `docs/requirements/<req>/logic_flow_<req>.md` (scoped) or `docs/requirements/logic_flow_<project>.md` (full)
- SVG artifacts in: `docs/requirements/<req>/logic_diagrams/`
- Trigger: `python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py <project> [<req>]`
  or: `python docs/training/logic_diagrams/generate_logic_diagram.py [<req>]` (from project)

**2. Vital Signs** (`health_check.md`) — "is it implemented correctly?"
- Audience: developer self-check, AI-assisted code review
- Checks: rule adoption, dependency tracking, docstring hygiene, missing `calling=` docstrings
- Trigger: say "vital signs" or "health check" to AI in project context
- Training: `docs/training/health_check.md`

**3. Behave Test Reports** — "did it work as specified?"
- Audience: QA, compliance, traceability proof
- Content: requirement → test → rules fired → execution trace
- Training: `docs/training/testing.md`

### Key Convention: `calling=` Function Docstrings

Every function wired via `Rule.formula(calling=my_func)` or `Rule.early_row_event(calling=my_func)` **MUST** have a one-line docstring:

```python
def _clvs_eligible(row, old_row, logic_row):
    """Derive clvs_eligible: 1 if shipment meets all CLVS criteria, else 0."""
    ...
```

- **Why:** The first docstring line appears in Logic Flow diagrams and Vital Signs reports
- **Without it:** diagram shows only the function name — no intent visible
- **With it:** `clvs_eligible = _clvs_eligible(row) — "1 if shipment meets all CLVS criteria"`
- **Vital Signs:** flags missing docstrings as ⚠️ `-1` finding
- **CE source:** `docs/training/logic_bank_api.md` — "CRITICAL — DOCSTRING ON EVERY calling= FUNCTION"

### Logic Diagram Generator — Key Design Decisions

After a BLT or on a new machine, these decisions need to be re-established:

- **Output structure:** `docs/requirements/<req>/logic_flow_<req>.md` + `logic_diagrams/*.svg`
- **Left ports (`_w`):** copy, sum, count — hierarchy flow lane (left side of tables)
- **Right ports (`_e`):** formula cross-table deps — derivation lane (right side of tables)
- **Intra-table arcs:** Graphviz silently drops self-loop edges on spline layouts. Solution: record as `// INTRA:table:src:dst:seq:idx` comments in `.dot`, inject as SVG bezier paths in post-processor. Multiple arcs fan out at staggered bulge distances (22, 46, 70px).
- **`rankdir=TB`:** parents at top (`rank=min`), trigger/children at bottom (`rank=max`)
- **Legend removed from diagram:** rule summary carried in `logic_flow_*.md` instead
- **NL spec source:** module-level docstring of each `logic/logic_discovery/*.py` file (via `ast.get_docstring`)
- **Requires:** `brew install graphviz` (macOS) — one-time install, not in venv

### File Locations (post-BLT)

```
system/ApiLogicServer-Internal-Dev/
  logic_diagram_gv.py              ← generator (Manager tool — not per-project)
  dev-architecture.md              ← this file

prototypes/base/docs/training/
  logic_diagrams/
    logic_diagram.md               ← reading guide (v1.4)
    generate_logic_diagram.py      ← per-project convenience wrapper
  logic_bank_api.md                ← includes calling= docstring CRITICAL rule
  health_check.md                  ← includes missing-docstring vital sign check

prototypes/manager/system/ApiLogicServer-Internal-Dev/
  logic_diagram_gv.py              ← propagated here by BLT (same as above)
```

**Gold source for generator:** `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager/system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py`

**After BLT:** generator is reinstalled to venv automatically. Per-project docs (`logic_diagram.md`, `generate_logic_diagram.py`) are propagated to all created projects via `prototypes/base/docs/training/logic_diagrams/`.

### Dependency Security Scanning

**Tool:** `pip-audit` — scans installed packages against known CVE databases.

**Run from Manager root (output to file):**
```bash
venv/bin/pip-audit 2>&1 | tee pip-audit-report.txt
```

**When to run:** before any BLT / release cut, or after bumping a dependency.

**Where fixes go:**
- `org_git/ApiLogicServer-src/requirements.txt` — dev install
- `org_git/ApiLogicServer-src/pyproject.toml` — published package (keep in sync with requirements.txt)
- `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/venv_setup/requirements-no-cli.txt` — base prototype (propagates to all created projects via BLT)
- All other `venv_setup/requirements-no-cli.txt` files in `prototypes/manager/samples/*/` — bump these too (use `grep -rln` + `sed -i`)

**Last scan (2026-05-26):** 5 vulnerabilities in 2 packages:
- `pip 25.1.1` — 4 CVEs (CVE-2025-8869, CVE-2026-1703, CVE-2026-3219, CVE-2026-6357); fix: `pip 26.1`
- `python-dotenv 0.15.0` — CVE-2026-28684; fixed → bumped to `1.2.2` in all requirements files

&nbsp;

### Optimistic Locking Fixes (Jun 2026) — GitHub #113, #114

**Gold source:** `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/api/system/opt_locking/opt_locking.py`

Two bugs reported against the same ~30-line block, fixed together:

**#113 — non-deterministic checksum.** `checksum()` used Python's built-in `hash()`, which is seed/build/platform-dependent for `str`/`bytes` (`PYTHONHASHSEED`). Different processes (replicas, restarts, mixed-arch nodes, Python minor-version bumps) compute different checksums for the same row → spurious `409 Sorry, row altered by another user` on valid updates. The repo's `PYTHONHASHSEED=0` pin in `run.sh`/`launch.json` only covers entrypoints ALS controls — lost under gunicorn/uvicorn/k8s/custom Docker `CMD`.
- **Fix:** `checksum()` now uses `hashlib.sha256(repr(tuple(real_tuple)).encode()).hexdigest()` — deterministic everywhere, no `PYTHONHASHSEED` dependency. No migration: the checksum is computed at read-time only, never persisted.

**#114 — `S_CheckSum` null on POST (insert) responses.** The checksum is stamped exclusively by a `loaded_as_persistent` SQLAlchemy event listener, which structurally cannot fire for a row created in the same request (SAFRS's POST response re-fetch hits a row already in the session's identity map — it triggers `refresh`, not `loaded_as_persistent`). Result: `S_CheckSum` is `null` in the `201` body, while a subsequent `GET` on the same row returns a populated checksum. Under `opt_locking=required`, a client that echoes the POST response on its first `PATCH`/`DELETE` gets a spurious lock failure — it must round-trip an extra `GET` first.
- **Fix:** Added an `after_flush` listener inside `opt_locking_setup()` that stamps `_check_sum_property` on every instance in `session.new`, mirroring the existing read-time listener. `_check_sum_property` is an unmapped Python attribute (not a column), so it survives the subsequent commit-expiration and is present when SAFRS re-serializes the row. Guarded with `except NoInspectionAvailable` for non-mapped objects that might land in `session.new`.
- **Known minor inefficiency (not a bug):** `after_flush` fires on every flush cycle within a transaction (e.g. LogicBank multi-pass derivation), so a still-new row's checksum gets recomputed redundantly across cycles. Functionally correct — the final pre-commit flush sees fully-derived values — just extra work. Not worth optimizing unless profiling shows it matters.

**Propagation:** Fixed in `prototypes/base/` gold source only. Next BLT run reinstalls to venv and regenerates all sample/test projects with the fix automatically — no other files to touch.

&nbsp;

### Optimistic Locking — Decimal/float checksum mismatch (Jul 2026)

**Gold source:** `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/api/system/opt_locking/opt_locking.py`

**Bug:** every PATCH to a row containing a `DECIMAL`/`Numeric` column (e.g. `Item.amount`, `Item.unit_price`) failed optimistic locking — `409 Sorry, row altered by another user` — even with a single user, zero concurrency, and no intervening write. Reproduced live in `basic_demo`: PATCH `Item.quantity` failed 3 times in a row across two browsers; DB confirmed no other writer touched the row.

**Root cause:** `checksum()` hashes `repr(tuple(column_values))`. The GET-time read path (`checksum_row`, live ORM instance) returns `float` for a `DECIMAL` column (e.g. `300.0`); LogicBank's `old_row` snapshot at PATCH time (`checksum_old_row`) returns `Decimal` (e.g. `Decimal('300')`). `Decimal('300') == 300.0` is `True`, but `repr()` differs (`'300.0'` vs `"Decimal('300')"`), so `checksum()` — which hashes on `repr()`, not equality — produced two different hashes for the identical value. Confirmed directly: hashing `(6, 6, 1, 2, 300.0, 150.0)` vs `(6, 6, 1, 2, Decimal('300'), Decimal('150'))` gives different SHA256 output, and the "wrong" hash exactly matched the `old_row_checksum` logged in the failing request.

**Fix:** in `checksum()`, normalize any `Decimal` entry to `float` before appending to the hashed tuple:
```python
if isinstance(each_entry, Decimal):
    real_tuple.append(float(each_entry))
```
Placed as the first branch in the existing `isinstance` chain (before `list`/`set`/`dict`), in the same three locations `#113`/`#114` were fixed: `basic_demo/api/system/opt_locking/opt_locking.py` (test project), the venv-installed `prototypes/base` copy, and this `org_git/ApiLogicServer-src` gold source.

**Verified:** restarted `basic_demo`, confirmed GET → PATCH → GET → PATCH round-trips return `200` with correct rule cascades (amount/amount_total/balance recalculated), zero opt-lock errors.

**Propagation:** Fixed in `prototypes/base/` gold source. Next BLT reinstalls to venv and regenerates sample/test projects automatically. Sample-project pre-baked copies under `prototypes/manager/samples/*/api/system/opt_locking/opt_locking.py` are downstream snapshots (not templates) — not patched individually; only worth doing if a specific sample project is being actively used/demoed and hits this.

&nbsp;

### F5 Simple Browser auto-open (`serverReadyAction`) — Manager-only (Jul 2026)

**Symptom:** F5 ("Run Project (start server)") reliably auto-opens Simple Browser in the **Manager** workspace. In a **freshly opened project workspace** (new VS Code window), the same launch config sometimes opens Simple Browser to "server not available" on the very first F5 — one manual refresh then works, and every subsequent F5 in that same window is fine from then on.

**Root cause — ruled out, then confirmed:** Not a cold Python/venv issue (venv already warm, no first-run `.pyc` compile tax) and not interpreter resolution (correct venv interpreter already selected in the fresh window). Traced `api_logic_server_run.py`: all app setup (`server_setup.api_logic_server_setup()` — model discovery, LogicBank rule bank init, admin loader) completes *before* `flask_app.run(...)`; `use_reloader` is off (no `debug=True`), so there's no second reloader-fork process either — by the time Werkzeug prints "Running on http://...", the app is fully warm and the socket is genuinely ready. The gap is in VS Code itself: `serverReadyAction` opens Simple Browser the instant its regex matches the debug-console stream, with no retry if that first connection loses the race. A freshly opened window's debug-console/output-channel pipeline has enough one-time startup latency (extension host, debug adapter, output streaming all spinning up for the first time in that window) that the very first F5 can occasionally win the regex-match race before the OS-level listener is truly ready to accept — a long-lived, already-warm window (the Manager, after its first-ever F5) doesn't pay that latency again, so it stays reliable indefinitely. Matches the observed pattern exactly.

**Fix:** removed the `serverReadyAction` block from all 5 server-launch configs (`Run Project (start server)`, `Run Project DEBUG`, VERBOSE, No Security, No Security VERBOSE) in `prototypes/base/.vscode/launch.json` (gold source + venv + `basic_demo`). **Left untouched:** Manager root `.vscode/launch.json` and `prototypes/manager/.vscode/launch.json` (venv + org_git) — the Manager window is the one place the warm-window assumption holds, by design.

**User-facing effect:** F5 in any created/sample project starts the server without auto-opening Simple Browser; user opens it manually once (readme/CE already documents the URL). No more "server not available" on first F5 in a new project window.

**Not fixable from this codebase's side** — Werkzeug already prints "Running on" only once genuinely bound with full app init done first. Any future fix would have to live in VS Code's `serverReadyAction` retry behavior, not here.

&nbsp;

### Multi-Relationship Fix (LogicBank) — Jun 2026

**Gold source:** `org_git/LogicBank` (sibling clone) — fix landed in commit `92954a7` (1.31.03) and `38f2287` (1.31.04, cleanup). Pin already bumped: `requirements.txt`, `pyproject.toml` → `LogicBank>=1.31.04`. `prototypes/base/venv_setup/requirements-no-cli.txt` still pins `>=1.30.01` — bump this too on next dependency pass (same pattern as the pip-audit fixes above: grep + sed across all `requirements-no-cli.txt` files).

**Bug:** `Rule.sum` (and related: `Rule.count`, `Rule.copy`, `Rule.formula` cascade, `LogicRow.link()`) could silently pick the wrong relationship — or crash — when a child class has 2+ relationships to the same parent class (e.g. `Employee.works_for_dept` and `Employee.on_loan_dept`, both → `Department`). Root causes (multiple, found incrementally — see LogicBank's own `system/LogicBank-Internal-Dev/multi-relationship-bug.md`, v4.1, GitHub issue #20, for the full investigation trail):
- `Sum` never honored an explicit `child_role_name` (only `Count` did) — always fell through to relationship auto-detection, which raised "Ambiguous Relationship" or silently matched the wrong one.
- `get_child_role_name()` only matched legacy `backref`, not SQLAlchemy 2.0 `back_populates`/`key`.
- A null-but-legitimately-optional parent FK (e.g. no `on_loan` assignment) crashed the aggregate adjustor instead of being treated as "nothing to adjust."
- `get_referring_children()` reset its accumulator *inside* the per-relationship loop, so only the last-declared `Rule.formula` role ever cascaded correctly — the other was silently dead.
- `Rule.copy` and `LogicRow.link()` had no `child_role_name` parameter at all — no way to disambiguate.

**Fix:** All of the above now correctly honor `child_role_name` (added to `Copy`/`link()`, fixed precedence in `Sum`), match `back_populates`/`key`, distinguish "FK validly null" from "FK references a missing parent," and reset the referring-children accumulator once per role, not per loop iteration. New regression suite: `examples/multi_relns/` in LogicBank (21 tests, dedicated Department/Employee model with two distinct relationships).

**CE gap closed:** `child_role_name` existed on `Rule.sum`/`count` for a long time but was **never documented** in the user-facing Rosetta Stone (`prototypes/base/docs/training/logic_bank_api.md`) — an AI assistant translating an NL prompt with multiple relationships between the same two classes had no CE guidance to reach for it, and would hit "Ambiguous Relationship" with no idea why. Added:
- `child_role_name` parameter docs on `Rule.sum`, `Rule.count`, `Rule.copy` docstrings
- A new "CRITICAL — child_role_name REQUIRED..." callout with a worked Department/Employee example (mirrors the LogicBank test fixture), placed after the FK-derivation anti-pattern section

**Propagation:** `logic_bank_api.md` is universal CE (same file for all created projects) — already in `prototypes/base/docs/training/`, no further propagation needed beyond the usual BLT reinstall. Bump the stray `requirements-no-cli.txt` pin (see above) on the next dependency-sync pass.

**Sample/test code for this pattern:** `org_git/LogicBank/examples/multi_relns/` — dedicated Department/Employee fixture with two distinct relationships (`works_for_dept`, `on_loan_dept`), exercising `Rule.sum`/`count`/`copy`/`formula`/`link()` disambiguation across 21 tests (`tests/test_sum_count.py`, `test_copy_ambiguous.py`, `test_formula_cascade.py`, `test_null_optional_fk.py`, `test_reparent.py`, `test_delete.py`, `test_link_disambiguation.py`). `logic/rules_bank.py` is the working declaration this CE example was distilled from — read it directly for the full picture (live-formula cascade on both roles, copy with disambiguator) when the doc's single worked example isn't enough.

&nbsp;

---

### README Broken-Link Check (create_codespaces_mgr.py) — Jun 2026

**Gold source:** `org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager/.devcontainer-codespaces/create_codespaces_mgr.py` — new `check_broken_links()`, gates Step 3 (commit+push) when run with `--push`/`--release`. Plain sync-only mode (no flag) does not check, since nothing is being published.

**Why this exists:** a README.md link review (replacing TODO placeholders with real paths) kept producing links that looked plausible but pointed at files that don't exist in **this** Manager (`build_and_test/genai-logic`, the BLT-built "local mgr") — wrong sample directory name, missing `.md` extension, stale Docs site path. Manual review missed several; a mechanical check catches all of them.

**Critical scoping lesson — two failed attempts before this worked:**
1. **First attempt:** scanned every `*.md` under the synced target, flagged any non-`samples/`-prefixed relative link as out of scope. Wrong on both axes — excluded genuine local links elsewhere in README.md, and the "out of scope" carve-out was supposed to be for mkdocs bare-page references (`Logic#anchor`), not all non-`samples/` paths.
2. **Second attempt:** scanned every `*.md` in the **entire local-mgr tree** (`target.rglob("*.md")`). Produced 236 hits — almost all false positives from `tests/`, `dockers/`, `system/` content: directories `create_codespaces_mgr.py` never even syncs to cs-mgr (see `SYNC_PATHS`/`COPY_EXCLUDES` at the top of that file), plus genuinely pre-existing, out-of-scope gaps (ungenerated Behave reports, images not yet created, mkdocs bare-page anchors like `../Integration-MCP/`).
3. **What actually works:** scope the check to **`README.md` only** — that's the actual ask ("check this readme"), not a repo-wide link audit. Against just README.md the same logic produces 5-6 genuine hits, zero noise.

**What the check does (current, working version):** for every `[text](link)` in `README.md`:
- `https://apilogicserver.github.io/Docs/...` → live HEAD request; 404 = broken.
- starts with `http://`/`https://` (anything else) → skipped, not this check's job (GitHub image URLs, etc.).
- bare page reference with no file extension and no trailing `/` (e.g. `Logic#declaring-rules`) → skipped; mkdocs resolves these at site-build time, they were never meant to resolve on a filesystem.
- everything else (`samples/...`, `genai_demo_fixup_required/...`, etc.) → must exist relative to README.md's own directory, or it's broken.

**One known non-fixable false positive:** `genai_demo_fixup_required/docs/fixup/` (README.md line ~628) — this is a forward reference to output the *reader* generates by running an earlier command in the same walkthrough (`genai-logic genai --repaired-response=...`), not a pre-built sample. The checker can't distinguish "doesn't exist yet because you haven't run the command" from "broken" — left as a known, accepted gap rather than chased further.

**Recurring fix pattern found while clearing real hits:** README links sometimes point at `samples/prompts/*.prompt` (missing the `.md` LogicBank/ApiLogicServer-src actually writes — `*.prompt.md`), or at an older/renamed sample directory (`customs_demo` → `customs_demo_clvs`, `readme.md` → `readme_reqmts.md`). Don't assume a broken `samples/...` link means the sample is missing — check for a name-drift sibling first.

**See also:** [[project_local_mgr_is_user_truth]] memory — verify against `build_and_test/genai-logic`, not `clean/ApiLogicServer` (a different, stale BLT output), when checking "does this file exist for users."

&nbsp;

---

### Type Hierarchy Pattern (Jul 2026)

Three standard approaches exist for modeling entity subtypes (e.g. Employee → Hourly, Salaried, Commissioned):

| Approach | Description | Tradeoff |
|---|---|---|
| **STI — Single Table Inheritance** | One table, all columns, `type TEXT` discriminator, subtype columns nullable | Simple queries/inserts; table gets wide; subtype cols sparse |
| **Joined CTI** | Base table + per-subtype tables joined by FK | Normalized; requires joins + custom API endpoints for insert/list |
| **Concrete CTI** | Fully separate table per subtype, no shared base | No joins; shared columns duplicated; no unified "all employees" query |

**GenAI-Logic prefers STI** because the full stack works without customization:
- `GET /api/Employee/` returns all subtypes in one call — no joins, no custom endpoint
- `POST /api/Employee/` with a `type` value inserts any subtype in one call
- Admin UI `show_when: type == 'hourly'` hides/shows subtype fields — no split UI sections needed
- Joined/concrete CTI require custom API endpoints for insert and list — significant extra effort for no practical gain in this stack

**🚨 Platform constraint — STI at the DATA level only. Do NOT add SQLAlchemy polymorphic subclasses:**

`rebuild-from-database` generates a plain base class (e.g. `Employee`) with no `__mapper_args__`. Leave it that way. Adding `__mapper_args__` + ORM subclasses (`HourlyEmployee`, `CommissionedEmployee`, etc.) hits two confirmed bugs:

1. **LogicBank** dispatches rules by the row's exact mapped class — a `Rule.formula` declared on `models.Employee` silently never fires for rows inserted as a subclass instance (`HourlyEmployee(...)`). Derived columns stay NULL/default with no error.
2. **SAFRS** cannot build JSON:API URLs for polymorphic STI instances — `GET /api/Employee/` raises `BuildError: Could not build url for endpoint 'HourlyEmployeeId'` because SAFRS derives the endpoint name from the row's runtime subclass but relationship metadata points at the base class.

**Correct STI implementation:**
- One `Employee` class, plain `type TEXT` column, no `__mapper_args__`, no subclass definitions
- All LogicBank rules declared on `models.Employee`; type-branching goes inside the `calling=` function body (`if row.type == 'hourly': ...`)
- Seed data uses `Employee(type='hourly', ...)` — not `HourlyEmployee(...)`
- Admin UI `show_when` entries written for all subtype-specific fields (auto-generated in Method 4)

**Inferred constraints (add automatically, no prompt needed):**
- Null-exclusion: `Rule.constraint` that subtype-specific columns are NULL for other types
- Zero-default: type-guarded formulas return `0`/`Decimal(0)` not `None` for non-applicable rows

**Key constraint:** any column that participates in a cross-subtype aggregate (e.g. `Department.total_payroll = sum of Employee.weekly_pay`) must live on the **base** table, not only on a subtype table.

**CE location:** project CE `Step 4d` (v3.21+) + manager CE STEP 4 checklist item `4d`. Detection phrase: "X are Y with Z" / "X is a type of Y" / "subtypes of Y include X, Z".

&nbsp;

---

**📖 Remember:** This file provides orientation. For comprehensive technical understanding, read **[Architecture-Internals.md](https://apilogicserver.github.io/Docs/Architecture-Internals/)** - it's written for both AI assistants and human collaborators.

