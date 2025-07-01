See https://apilogicserver.github.io/Docs/Data-Model-Examples/

These files are symbolic links to pre-installed sqlite databases.  These allow you to explore creating projects from existing databases.

For example, create Northwind like this:

```bash
genai-logic create  --project_name=nw --db_url=sqlite:///samples/dbs/nw.sqlite
```

> Note: If the symbolic links are missing, it is probably due to permission issues, e.g., on windows you must run the Shell with Admin privileges.  You can continue using the abbeviations instead of a standard SQLAlchemy database uri.