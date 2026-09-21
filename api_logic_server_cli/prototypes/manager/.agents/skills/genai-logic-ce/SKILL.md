---
name: genai-logic-ce
description: ApiLogicServer / GenAI-Logic Context Engineering (CE). Use when creating domain projects from prompts (Method 4 / System Creation Services), declaring business logic rules (LogicBank), configuring databases, running migrations, or managing projects.
---

# ApiLogicServer / GenAI-Logic Context Engineering (CE)

This skill activates the project creation, business logic, and architectural rules for ApiLogicServer / GenAI-Logic.

## Core Reference Files

Read the following authoritative files when performing tasks:

1. **Manager Workflow & Project Creation**:
   - `file:///.github/copilot-instructions.md` — Complete reference for Method 4 (System Creation Services), Socratic interview (Step 1a/1b), DDL generation, rebuild, and provenance requirements.
2. **Project CE & Training**:
   - `<project_name>/.github/.copilot-instructions.md` — Subsystem workflow for created projects.
   - `docs/training/logic_bank_api.md` — Declarative rule syntax (`declare_logic()`, formulas, constraints, parent/child derivations).
   - `docs/training/logic_bank_patterns.md` — Common patterns (allocation, audits, multi-table rollups).
   - `docs/training/implement_requirements.md` — Schema conventions, primary keys, foreign keys.
   - `docs/training/RequestObjectPattern.md` — Integration services (events, Kafka, AI requests).

## Golden Rules
- **Active Project Context**: Always track and announce the active project subdirectory `<project_name>/`. Prefix all paths and CLI commands accordingly.
- **Logic Location**: `<project_name>/logic/declare_logic.py` is only a stub. Put use-case logic in `<project_name>/logic/logic_discovery/<use_case_name>.py`.
- **Gold Source**: This workspace (`build_and_test/genai-logic`) is a test bench. Edits made to core templates, prototypes, or docs must also be copied to `org_git/ApiLogicServer-src`.

