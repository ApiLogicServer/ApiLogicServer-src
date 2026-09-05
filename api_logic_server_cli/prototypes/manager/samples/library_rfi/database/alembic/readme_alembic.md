You can push changes to `database/models.py' to your database automatically, or manually.

<br>

## Automatic

Use:

```bash
python database/alembic/alembic_run.py [--non-interactive]
```

<br>

## Manual

The diagram below illustrates a path for enacting changes to the data model, and using [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) to automate the database changes:

1. Update `database/models.py` (e.g., add columns, tables)
2. Use alembic to compute the revisions
```bash
cd database
export APILOGICPROJECT_NO_FLASK=True
alembic revision --autogenerate -m "Added Tables and Columns"
```
3. **Edit the revision file** to signify your understanding (see below)
4. Activate the change
```bash
alembic upgrade head 
unset APILOGICPROJECT_NO_FLASK
```

![alembic example](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/database/alembic/alembic-overview.png?raw=true)


To update your admin app, run `rebuild-from-model`.  For more information, see [Database Design Changes](https://apilogicserver.github.io/Docs/Database-Changes/).