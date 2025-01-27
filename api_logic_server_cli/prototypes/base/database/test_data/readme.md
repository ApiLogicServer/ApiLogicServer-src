ChatGPT sometimes fails to build proper test data that matches the derivation rules.

You can rebuild the test data, using Logic Bank rules for proper derivations, to rebuild your `database/db.sqlite` (make a copy first to preserve your existing data).


```
als genai-utils --rebuild-test-data 
```

You can explore the generated `database/test_data/test_data_code.py` to control test data generation.