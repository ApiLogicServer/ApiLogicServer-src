GenAI often fails to build proper test data that matches the derivation rules.

You can rebuild the test data, using Logic Bank rules for proper derivations.

Envisioned support will create a new db.sqlite, with test data that reflects derivations.  
Review, and copy to your database/db.sqlite.

```
als genai-utils --rebuild-test-data 
```