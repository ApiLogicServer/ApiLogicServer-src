# Coordinating Parallel Dev Streams (**Multi-Team Development**)

This is the Diego Lo Giudice challenge: enable ongoing parallel development with both the LOB and Dev *teams.*  It's enabled by declarative technology, where the integration is done with software, not manual effort.

Please see [Import Documentation](https://apilogicserver.github.io/Docs/IDE-Import-WebGenAI/).

<br/>

# Exploring Import

<br/>

## Setup: Manager pre-installs Import Sample

When [you create the manager (**strongly recommended**)](https://apilogicserver.github.io/Docs/Manager/), the system installs 3 sample projects you can use to explore import.

1. **Base Project** is GenAI_no_logic.  No rule-based attributes.  See `system/genai/examples/genai_demo/wg_dev_merge/base_genai_demo_no_logic`.  It's not really used, just provided as a reference.

2. **Dev Project** was created with export-1, and has added rules for `carbon_neutral`.  It is ready for export-2.  See `system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed`

3. **WG project** has continued from export-1 to add our standard customer.balance rules.  It is ready for export-2.  See `system/genai/examples/genai_demo/wg_dev_merge/wg_demo_no_logic_fixed`.

    * It has an `docs/export/export.json`, which describes the data model and rules from the WG project.  This is used for import.

The naming convention is that these started with no rules, had rules added, and were **"fixed"** by Genai-Logic to update the data model.

<br/>

## Usage

Imports are performed from with the dev project, using the `import-genai` CLI command:

```bash
cd system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed
als genai-utils --import-genai --using=../wg_demo_no_logic_fixed
```

<br/>

### Restart option for failure recovery

It may fail, requiring either a **re-run** or an `import-resume`:

* **Re-run** is indicated if the data model is missing attributes, incorrect or imcomplete.
    1. make sure to get initial `system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/database/models.py` (eg, update from models_for_resume.py)
    2. delete or rename the `docs/import` directory.

* `import-resume` can be used if you can repair the file below, e.g., a minor syntax error.
    1. fix `system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/docs/import/create_db_models.py`
        * Note: you can run this standalone with your IDE to verify it.  It should create `create_db_models.sqlite` in your `docs/import` directory.
    2. make sure to get initial system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/database/models.py (eg, update from models_for_resume.py)

```bash
cd system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed
als genai-utils --import-genai --using=../wg_demo_no_logic_fixed --import-resume
```
