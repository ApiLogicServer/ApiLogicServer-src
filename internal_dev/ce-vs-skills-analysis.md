# AI-Assisted Development: Always-On CE vs. On-Demand Skills

**Date:** March 2026  
**Context:** Comparing two approaches to delivering domain knowledge to AI coding assistants, using ApiLogicServer's Context Engineering (CE) and Thomas Pollet's `app_gen_playbook` (Codex skills) as concrete examples.

---

## The Two Approaches

### Approach A: Always-On Context Engineering (CE)
Domain knowledge is embedded in a file (`.copilot-instructions.md`) that is injected automatically into every AI session, passively and without invocation. The AI has the full knowledge base from the first message.

- **Example:** ApiLogicServer project-level `.copilot-instructions.md` (~740 lines) — LogicBank API reference, patterns, testing guide, security patterns — all loaded at session start.
- **Agent:** VS Code Copilot (Claude/GPT), interactive.
- **Trigger:** None. Always present.

### Approach B: On-Demand Skills
Domain knowledge is packaged in `SKILL.md` files with YAML frontmatter describing when they apply. An orchestrator or the AI loads a skill only when the current task matches the skill's declared domain.

- **Example:** `app_gen_playbook/skills/logicbank-rules-design/SKILL.md` — loaded only when the backend role touches rule mapping or write logic.
- **Agent:** OpenAI Codex, automated multi-role pipeline.
- **Trigger:** Task/role match against skill description.

---

## ApiLogicServer's Three Creation Modes (Important Context)

ApiLogicServer covers a wider spectrum than a simple CE vs. skills comparison implies. The Manager workspace supports three distinct creation modes, each with a different AI pattern:

| Method | Command | AI Pattern | Logic |
|---|---|---|---|
| **Method 1** — Existing DB | `genai-logic create --db_url=...` | No AI — scaffolding only | Rules added manually or conversationally in project |
| **Method 2** — GenAI (prompt → project) | `genai-logic genai --using=prompt` | Fine-tuned ChatGPT (PE, not CE) | Rules auto-generated from NL prompt |
| **Method 4** — System Creation Services (SCS) | `genai-logic create --db_url=starter.sqlite` then AI-driven | Always-on CE *during* structured creation sequence | Full schema + logic implemented by AI reading project CE inline |

Methods 1 and 2 represent the original design: create infrastructure in the Manager, then add/refine rules conversationally in the opened project workspace using always-on CE.

**Method 4 (SCS, added 2026)** is a hybrid: the user stays in the Manager, and the AI executes a structured mandatory sequence — create project, silently read `subsystem_creation.md` + `logic_bank_api.md` + `RequestObjectPattern.md` + `logic_bank_patterns.md`, complete pre-DDL analysis (constants, FK inventory, Request Pattern scan), then write schema, seed, and implement logic — all using CE-delivered knowledge but in a pipeline-like sequence. The output is a fully implemented project that then lives in the iterative world.

This means ApiLogicServer spans the full spectrum:

```
One-shot automated (Method 2)  →  AI-guided structured creation (Method 4 SCS)  →  Iterative agile (project CE)
       [ChatGPT PE]                    [CE + mandatory sequence]                    [always-on CE, conversational]
```

---

## Comparison Across Key Dimensions

### 1. Context Overhead

| | Always-On CE | On-Demand Skills |
|---|---|---|
| Token cost | Fixed per session (always present) | Variable (only loaded when relevant) |
| Wasted context | High if session is unrelated to the domain | Low — loaded only when needed |
| Risk of overflow | Higher in long automated pipeline runs | Lower — each role gets bounded context |

**Verdict:** On-demand skills are more token-efficient for multi-role automated pipelines. Always-on CE is acceptable for short interactive sessions with a focused domain.

---

### 2. Friction and Reliability

| | Always-On CE | On-Demand Skills |
|---|---|---|
| Invocation required | No | Yes (implicit or explicit) |
| Failure mode | Knowledge always present, even if unused | Knowledge absent if skill not triggered |
| Developer burden | Zero | Must know which skill applies, or trust orchestrator |

**Verdict:** Always-on CE is more reliable for end-user developers who don't know what they don't know. On-demand skills are reliable only when the triggering logic is well-tuned.

---

### 3. Iterative and Agile Development

This is the sharpest distinction between the two approaches.

**Software projects are not one-shot artifacts.** Like a book being written over months or years, a production application evolves continuously:
- Requirements change after users see the first working version
- Schema evolves (new tables, columns, migrations)
- Business rules are refined based on real data
- Security, integrations, edge cases are added incrementally
- New developers (or AI sessions) must work with what was already built

#### Always-On CE in an iterative context

Each new session re-reads the project's files (models, logic, tests) and has the full domain knowledge available immediately. The AI can:
- Make surgical changes to existing logic without regenerating anything
- Understand the *intent* of existing rules by reading them (declarative rules are self-documenting)
- Continue a conversation across many dev cycles without losing context about prior decisions (to the extent they are encoded in the files)

The declarative rule format (`Rule.sum`, `Rule.formula`, `Rule.constraint`) makes long-term iteration tractable: 5 rules written six months ago are readable and modifiable without understanding how they were generated.

#### On-Demand Skills in an iterative context

Thomas's playbook has an iteration mode (`--mode iterate --scope backend-only change_request.md`), but each run is a fresh pipeline pass:
- Each agent role re-reads durable artifact files (`rule-mapping.md`, `model-design.md`)
- No memory of *why* decisions were made — only what was decided
- Iteration is expressed as a **change request file**, not a conversation
- The AI has no model of the reasoning history, rejected alternatives, or business context behind prior decisions

This works well for **scoped, well-specified changes**. It becomes fragile for changes that require understanding the intent behind existing design decisions.

**Core asymmetry:** Always-on CE trades token efficiency for conversational continuity. On-demand skills trade conversational continuity for bounded, efficient per-role context. For iterative agile development — where the developer and AI are collaborating over many sessions across months — conversational continuity matters more.

---

### 4. Project Lifecycle Fit

| Phase | Always-On CE | Method 4 SCS (hybrid) | On-Demand Skills |
|---|---|---|---|
| Initial creation | Functional | Optimized (structured, stays in Manager) | Optimized (full pipeline) |
| First working version → user feedback | Good (conversational) | Good — output drops into iterative CE world | Awkward (requires new change request file) |
| Incremental rule refinement | Natural (surgical edits) | N/A — creation phase only | Possible but heavyweight |
| Schema evolution + migration | Natural (developer-driven) | N/A — creation phase only | Re-runs affected pipeline phases |
| Long-term maintenance (months later) | Good — declarative rules are readable | Good — project CE takes over after creation | Depends on artifact quality |
| New developer onboarding | Good — CE in project explains itself | Good — CE in project explains itself | Good — playbook is documented |

**Note on Method 4:** SCS is a creation-time tool. Once the project is created and F5 is confirmed working, the user opens the project as a workspace and the normal always-on project CE takes over for all subsequent iteration. The structured pipeline is used once; the conversational model owns the rest of the project's life.

---

### 5. State and Memory

| | Always-On CE | On-Demand Skills |
|---|---|---|
| State between sessions | In project files (logic, tests, models) | In durable artifact files under `runs/current/` |
| Reasoning history | Lost between sessions (unless in commit messages/docs) | Lost between runs (change request only records *what*, not *why*) |
| Conflict detection | AI reads existing files before editing | Re-run may overwrite without detecting conflict |

Both approaches share a fundamental limitation: neither preserves the *reasoning* behind decisions across sessions. This is an open problem in AI-assisted development generally.

---

### 6. Domain Knowledge Provenance

Both approaches can carry the same domain knowledge content (e.g., LogicBank rule patterns). The difference is purely in delivery mechanism. Content quality is independent of approach.

In practice, the `app_gen_playbook` skills for LogicBank are derived from ApiLogicServer's CE materials, restructured for the multi-role pipeline context.

---

## Summary

| Dimension | Always-On CE | On-Demand Skills |
|---|---|---|
| Token efficiency | Lower | Higher |
| Friction for developer | Zero | Requires invocation tuning |
| Best agent type | Interactive (VS Code Copilot) | Automated pipeline (Codex) |
| Iteration model | Conversational, surgical | Batch, change-request-driven |
| Agile development fit | High | Moderate |
| Long-running project fit | High | Moderate |
| One-shot project generation | Functional | Optimized |
| Context between sessions | Project files | Artifact files |

---

## Conclusion

The two approaches are not competing — they are optimized for different contexts:

- **On-demand skills** suit **automated multi-role generation pipelines** where context must be bounded per role, and the primary workflow is generating a new application from a brief.
- **Always-on CE** suits **interactive developer workflows** on **long-running projects** where the developer iterates conversationally over many sessions, making incremental changes to a living codebase.
- **Method 4 SCS (hybrid)** sits between: it uses CE-delivered knowledge to execute a structured creation sequence (pipeline-like) while remaining in a conversational agent — then hands off to the iterative CE model for all subsequent development.

The agile development lifecycle — continuous iteration driven by user feedback over the full life of a project — aligns more naturally with always-on CE, because the unit of work is a conversation, not a pipeline run, and the project artifact accumulates meaning over time rather than being regenerated from a brief.

ApiLogicServer's original design — create infrastructure in the Manager, add and refine rules conversationally in the opened project — still holds and remains the primary pattern. Method 4 extends it by allowing the AI to implement the full initial system (schema, seed, logic) before the user ever opens the project, without requiring a separate ChatGPT pipeline. The two creation modes (Method 2 automated ChatGPT, Method 4 AI-in-Manager) and the iterative project mode together cover the full software development lifecycle.

The choice of declarative rules (LogicBank) over generated procedural code amplifies the iterative advantage regardless of how the project was initially created: declarative specifications remain readable and modifiable by any AI session months later, making long-term iteration tractable in a way that generated imperative code is not.
