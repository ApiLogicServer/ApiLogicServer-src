# Antigravity Context — GenAI-Logic Project Manager

This workspace is the **Project Manager** for GenAI-Logic (ApiLogicServer), equipped with extensive Context Engineering (CE).

## Mandatory Context Engineering (CE) References

Whenever you are asked to create projects, declare logic rules, or run dev workflows, read and adhere to the relevant CE files:

1. **Manager CE (System Creation Services & Project Lifecycle)**:
   - File: [.github/copilot-instructions.md](.github/copilot-instructions.md)
   - Read this file when creating projects from prompts (Method 4 / System Creation Services), creating databases, or managing projects.
   - **Key Rules from Manager CE:**
     - **Active Project Context**: Always determine and announce the active project directory `<project_name>/`. Prefix all file paths and CLI commands with `<project_name>/`.
     - **Path Rule**: Run CLI commands from `<project_name>` or Manager root as specified in CE (e.g., `sqlite3 <project_name>/database/db.sqlite`, `cd <project_name> && genai-logic rebuild-from-database ...`).
     - **Logic Location**: `<project_name>/logic/declare_logic.py` is a generated STUB. Actual use-case logic belongs in `<project_name>/logic/logic_discovery/<use_case_name>.py`.
     - **Provenance**: Always write `project_creation_prompt.md`, `project_creation_report.md`, and `ad-libs.md` under `<project_name>/docs/requirements/` before declaring completion.

2. **Project CE (Inside created projects)**:
   - For an active project `<project_name>`, consult:
     - `<project_name>/.github/.copilot-instructions.md` (Project CE)
     - `<project_name>/docs/training/implement_requirements.md`
     - `<project_name>/docs/training/logic_bank_api.md`
     - `<project_name>/docs/training/logic_bank_patterns.md`
     - `<project_name>/docs/training/RequestObjectPattern.md`

3. **Developer Architecture (Internal Dev Only)**:
   - **Explicit trigger only:** If the user explicitly asks to "load dev architecture", "load dev-architecture.md", or equivalent, read `system/ApiLogicServer-Internal-Dev/dev-architecture.md` and follow its header sequence.
   - Confirmation must be ONE short line: `"Dev-architecture context loaded — gold-source workflow confirmed."`
   - **GOLD SOURCE RULE**: This workspace is a test bench. Edits made here to templates or prototypes must ALSO be reflected in gold source (`org_git/ApiLogicServer-src`, `org_git/Docs`).

