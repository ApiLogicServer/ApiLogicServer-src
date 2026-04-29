# Test Data — Seed Your Database

## Canonical Approach — `alp_init.py` (Flask context + LogicBank active)

Run from project root:
```bash
cd /path/to/your_project
PROJECT_DIR=$(pwd) python database/test_data/alp_init.py
```

This runs with Flask app context so **LogicBank rules fire on insert** — all computed/derived fields are populated correctly. No duplicated calculation logic.

The file already has the required path fix at line 4:
```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # ensure project root on path
```

Edit the `seed_<name>_data(session)` function in `alp_init.py` to customize your seed data.

## Alternative — `test_data_preamble.py` (TestBase + LogicBank.activate, no Flask)

Copy `test_data_preamble.py` to a new file and add your data after `LogicBank.activate()`. Rules fire, no Flask required.

> **Note:** `test_data_preamble.py` writes to `database/test_data/db.sqlite` (a test copy), not the live `database/db.sqlite`. Change `db_url` if targeting the live database.

## Common Failures

| Error | Root cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'config'` | Project root not on `sys.path` | Ensure `sys.path.insert(0, str(Path(__file__).parent.parent.parent))` is the first lines |
| All computed fields are 0 | `APILOGICPROJECT_NO_FLASK=1` set but `LogicBank.activate()` never called | Add `LogicBank.activate(session=session, activator=declare_logic.declare_logic)` after session creation |
| Shell heredoc garbled | Terminal tool mangles multi-line heredocs | Write a `.py` file, run `python script.py` — never `sqlite3 db << 'SQL'` |

## WebGenAI CLI (WebGenAI projects only)

```bash
als genai-utils --rebuild-test-data
```

This reads `docs/*.response` JSON files from the WebGenAI pipeline and generates `test_data_code.py`. **For WebGenAI projects only** — does not work for AI-generated or hand-crafted projects.

You can explore the generated `database/test_data/test_data_code.py` to understand the generated data structure.
