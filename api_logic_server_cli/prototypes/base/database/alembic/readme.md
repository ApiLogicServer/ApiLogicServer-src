The diagram below illustrates a simple path for enacting changes to the data model, and using [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) to automate the database changes:

1. Update `database/models.py` (e.g., add columns, tables)
2. Use alembic to compute the revisions
```bash
cd database
alembic revision --autogenerate -m "Added Tables and Columns"
```
3. Edit the revision file to signify your understanding
4. Activate the change
```bash
alembic upgrade head 
```

![alembic example](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/database/alembic/alembic-overview.png?raw=true)


Then, run `rebuild-from-model`.  For more information, see [Database Design Changes](https://apilogicserver.github.io/Docs/Database-Changes/).