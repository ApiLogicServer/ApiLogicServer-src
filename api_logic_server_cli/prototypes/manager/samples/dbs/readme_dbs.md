See https://apilogicserver.github.io/Docs/Data-Model-Examples/

These are pre-installed sqlite databases.  These allow you to explore creating projects from existing databases.

For example, create Northwind and basic_demo like this (more connectivity shown in [../readme_samples.md](../readme_samples.md)):

```bash
genai-logic create  --project_name=nw --db_url=sqlite:///samples/dbs/nw.sqlite

genai-logic create --project_name=basic_demo --db_url=sqlite:///samples/dbs/basic_demo.sqlite
```

Or, create database with just a `SysConfig` table, and then use [Subsystem Creation](https://apilogicserver.github.io/Docs/Project-Structure/#subsystem-creation-in-proj) in the created project:

```bash
genai-logic create  --project_name=customs_app --db_url=sqlite:///samples/dbs/starter.sqlite
```

Config tables are analogous to config files, enabling you to outboard constants from your code.  Since they are tables, they can be managed with the Admin app and APIs.

You can make config tables easy to access by including a foreign key in your domain table, with the value 1.  This enables you to code rules like:

```python
    Rule.formula(derive=OrderDetail.Amount,  # compute diccounted price * qty
        as_expression=lambda row: row.UnitPrice * row.Quantity * SysConfig.discount_rate)
```