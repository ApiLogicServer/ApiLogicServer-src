# Quick Start

## Create from existing database

Try the demo:

```bash
ApiLogicServer create --project-name=sample_ai --db-url=sqlite:///sample_ai.sqlite
```

Or, the tutorial (lots of code & logic samples):
```bash
ApiLogicServer create --project-name=sample_ai --db-url=sqlite:///sample_ai.sqlite
```

Then, try your own databases

* Find [database url examples here](https://apilogicserver.github.io/Docs/Database-Connectivity/)


## Create new database from AI

You can use Copilot Chat to create databases.

### AI-Created Models

You can use Copilot chat (if extension installed):

![copilot](images/copilot.png)

1. Create a model, eg:

<details markdown>

<summary> Copilot prompt </summary>

After installing, you can optionally run the first demo, above.  The key training activities are:
```
Use SQLAlchemy to create a sqlite database named sample_ai.sqlite, with customers, orders, items and product

Hints: use autonum keys, allow nulls, Decimal types, foreign keys, no check constraints.

Include a notes field for orders.

Create a few rows of only customer and product data.

Enforce the Check Credit requirement (do not generate check constraints):

1. Customer.Balance <= CreditLimit
2. Customer.Balance = Sum(Order.AmountTotal where date shipped is null)
3. Order.AmountTotal = Sum(Items.Amount)
4. Items.Amount = Quantity * UnitPrice
5. Store the Items.UnitPrice as a copy from Product.UnitPrice
```
2. Paste the copilot response into a new `sample_ai.py` file
3. Create your project:

```bash
als create --project-name=sample_ai --from-model=sample_ai.py --db-url=sqlite
```
</details>

4. This will create your database, create an API Logic Project from it, and launch your IDE.

&nbsp;

### AI-Created Databases

1. Create a database script, eg:
```
create a sqlite database of Employees and Skills
```
2. Paste the copilot response into a new `models.py` file
3. Run `models.py` to create the `employee_skills.db` database
4. Create your project:

```bash
als create  --project-name=copilot --db-url=sqlite:///employee_skills.db
```

&nbsp;

## Environment Variables

Check:
1. `APILOGICSERVER_AUTO_OPEN` - set to code
2. `APILOGICSERVER_VERBOSE`
