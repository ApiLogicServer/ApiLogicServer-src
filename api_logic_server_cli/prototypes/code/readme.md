Welcome the the API Logic Server Manager.


## Create API Logic Projects From Existing Databases

Create projects using **Terminal > New Terminal**.  Here are some pre-installed samples:

* **Demo:** 
`ApiLogicServer create --project-name=sample_ai --db-url=sqlite:///sample_ai.sqlite`

* **Tutorial** (lots of code & logic samples):
`ApiLogicServer create --project-name= --db-url=`

Then, try your own databases

* Find [database url examples here](https://apilogicserver.github.io/Docs/Database-Connectivity/)


## Create new databases from Copilot AI

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
</details>
2. Paste the copilot response into a new `sample_ai.py` file
3. Create your project:

```bash
als create --project-name=sample_ai --from-model=sample_ai.py --db-url=sqlite
```

4. This will create your database, create an API Logic Project from it, and launch your IDE.

&nbsp;


&nbsp;

## Environment Variables

Check:
1. `APILOGICSERVER_AUTO_OPEN` - set to code
2. `APILOGICSERVER_VERBOSE`

&nbsp;

## Managing Your Projects

Created projects will show up here as directories.  

If you want to customize/run the project, do so in another instance of VSCode.  You may find it helpful to acquire this extension: `Open Folder Context Menus for VS Code`.  It will enable you to open the project in another instance of VSCode.