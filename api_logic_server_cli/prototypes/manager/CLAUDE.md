# Manager Workspace — Claude Code Instructions

## ⚠️ NEVER run `genai-logic genai`
Not the preferred approach. Do not run it, even for prompt files.

---

## ⚠️ PATH RULE for Manager root
All file operations use the project subdirectory as prefix — you are running from the Manager root, not inside the project:
- sqlite3 commands:    `sqlite3 <name>/database/db.sqlite "..."`
- genai-logic rebuild: `cd <name> && genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite && cd ..`
- python seed:         `cd <name> && PROJECT_DIR=$(pwd) python database/test_data/alp_init.py && cd ..`
- file reads/writes:   `<name>/logic/logic_discovery/...`, `<name>/database/...`

---

## Follow the Manager CE (Method 4)
For all domain project creation, follow the Method 4 sequence in `.github/.copilot-instructions.md` exactly — STEP 1 through STEP 5, uninterrupted.

⚠️ STEP 5 is mandatory — do not skip it. Write `<name>/docs/requirements/readme.md` (provenance) and `<name>/docs/requirements/ad-libs.md` (every assumption or guess made beyond the prompt spec) before telling the user the project is done.
