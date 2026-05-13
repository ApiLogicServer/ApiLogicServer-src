# Manager Workspace — Claude Code Instructions

## ⚠️ NEVER run `genai-logic genai`
It is not the preferred approach. Do not run it, even for prompt files.

## Creating a project from a prompt (System Creation Services)

When user says **"implement project `<name>` from `<prompt-file>`"** (or similar):

1. Read `<prompt-file>` fully — hold it in context
2. Run: `source venv/bin/activate && genai-logic create --project-name=<name> --db_url=sqlite:///samples/dbs/starter.sqlite`
3. Read these files silently (do NOT display them):
   - `<name>/.github/.copilot-instructions.md`
   - `<name>/docs/training/implement_requirements.md`
   - `<name>/docs/training/logic_bank_api.md`
   - `<name>/docs/training/logic_bank_patterns.md`
   - `<name>/docs/training/RequestObjectPattern.md`
4. Analyze the prompt — derive the schema FROM the logic (do this before any DDL):
   - What calculations exist? → what derived columns are needed?
   - What lookup entities exist? → what FK integer columns are needed?
   - What rates/thresholds/dates exist? → what SysConfig columns are needed?
5. Write DDL, run `cd <name> && genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite`, seed, write rules
6. Write `<name>/docs/requirements/readme.md` (creation provenance) and `<name>/docs/requirements/ad-libs.md`
7. Tell the user the project is done

**Do not stop after step 2. Do not ask "would you like me to add rules?". The scaffold is not the deliverable — the working system with rules is.**

## Creating a project from an existing database

```bash
genai-logic create --project-name=<name> --db_url=sqlite:///samples/dbs/<db>.sqlite
```

## Running a sample

```bash
genai-logic run --project-name=samples/basic_demo_sample
```
