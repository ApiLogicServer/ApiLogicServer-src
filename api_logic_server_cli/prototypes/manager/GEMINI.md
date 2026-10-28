# Antigravity Context — GenAI-Logic Project Manager

This workspace is the **Project Manager** for GenAI-Logic (ApiLogicServer), equipped with extensive Context Engineering (CE).

## Mandatory Session Bootstrap & Context Engineering (CE)

1. **Manager CE — Mandatory Session Bootstrap (Read First, Every Session)**:
   - File: [.github/copilot-instructions.md](.github/copilot-instructions.md)
   - **UNCONDITIONAL BOOTSTRAP RULE**: On the very first turn of every session — before answering ANY question (e.g. "what are rules", "what can I do here?") or running any workflow — silently read `.github/copilot-instructions.md` in full and adhere to all of its protocols (User Activation Protocol, Content Organization Protocol, System Creation Services, etc.).
   - *(Note: Do not rely on `@` inline expansion for `.github/copilot-instructions.md`, as Antigravity caps inline rule files at 24 KB and `.github/copilot-instructions.md` is ~51 KB; reading it via `read_file` loads the full file without truncation.)*
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

