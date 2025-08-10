This rebuilds test data into `database/test_data/db.sqlite`, for example as used by genai project creation.

ChatGPT sometimes fails to build proper test data that matches the derivation rules.

You can rebuild the test data, using Logic Bank rules for proper derivations, to rebuild your `database/db.sqlite` (make a copy first to preserve your existing data).

```
als genai-utils --rebuild-test-data 
```

You can explore the generated `database/test_data/test_data_code.py` to control test data generation.

If required, you can copy `database/test_data/test_data_preamble.py` to a new file, to rebuild your database (e.g., from an altered model file), and load your own test data (if any).