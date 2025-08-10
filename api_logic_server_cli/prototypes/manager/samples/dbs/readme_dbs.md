See https://apilogicserver.github.io/Docs/Data-Model-Examples/

These are pre-installed sqlite databases.  These allow you to explore creating projects from existing databases.

For example, create Northwind and basic_demo like this:

```bash
genai-logic create  --project_name=nw --db_url=sqlite:///samples/dbs/nw.sqlite

genai-logic create --project_name=basic_demo --db_url=sqlite:///samples/dbs/basic_demo.sqlite
```
