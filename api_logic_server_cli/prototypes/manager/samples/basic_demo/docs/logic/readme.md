### Add Natural Language Logic to Your Project

You can add Natural Language logic files to this directory, e.g. in `genai_demo/docs/logic`: 

* `valid_names.prompt`: Customer and Product Names cannot be 'x'
* `valid_currency.prompt`: Customer credit limits cannot be negative; Product prices must be positive.

Then, use GenAI to create executable logic in your `logic/logic_discovery` directory, e.g.,

```bash
als genai-logic
```

Notes:

1. Ensure derived attributes exist in the data model (see [Database Design Changes](https://apilogicserver.github.io/Docs/Database-Changes/))
2. Be sure to initialize such attributes in your database
3. For more information, [click here](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-logic-to-existing-projects)
4. Consider renaming your logic files afterward (`valid_names.z-prompt`)so they are skipped on future runs
