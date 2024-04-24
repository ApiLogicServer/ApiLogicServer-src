Welcome the the API Logic Server Manager.

## Create API Logic Projects From *Existing* Databases

To create a project, **press F5**, or use the CLI (**Terminal > New Terminal**) and try some pre-installed samples:

* [**Demo:** ](https://apilogicserver.github.io/Docs/Sample-AI/) created from AI (Copilot)

```
als create --project-name=sample_ai --db-url=sqlite:///sample_ai.sqlite
```


* [**Tutorial:** ](https://apilogicserver.github.io/Docs/Tutorial/) lots of code & logic samples:
```
ApiLogicServer create --project-name= --db-url=
```

Then, try your own databases [(db-url examples here)](https://apilogicserver.github.io/Docs/Database-Connectivity/), or experiment with [these Docker databases](https://apilogicserver.github.io/Docs/Database-Docker/).

&nbsp;

## Create API Logic Projects From *New* Databases, with Copilot

You can use Copilot chat (if extension installed):

1. Create a model, eg:

<details markdown>

<summary> Show Me How to Use Copilot </summary>

&nbsp;

Paste this into the Copilot prompt:

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

![copilot](system/images/copilot.png)
</details>

<br>

2. Paste the copilot response into a new `sample_ai.py` file

3. Create your project:

```bash
als create --project-name=sample_ai --from-model=sample_ai.py --db-url=sqlite
```

4. This will create your database, create an API Logic Project from it, and launch your IDE.

&nbsp;


&nbsp;

## Notes

The [API Logic Server Manager](https://apilogicserver.github.io/Docs/Manager/) simplifies creating and managing projects.



### Environment Variables

Check:
1. `APILOGICSERVER_AUTO_OPEN` - set to code
2. `APILOGICSERVER_VERBOSE`

&nbsp;

### Managing Your Projects

Created projects will show up here as directories.  (You create projects anywhere, and move them; this is just the default).

If you want to customize/run the project, do so in *another instance* of VSCode.  You may find it helpful to acquire this extension: `Open Folder Context Menus for VS Code`.  It will enable you to open the project in another instance of VSCode.

&nbsp;

### Add Notes, Resources

This is a good place to add text notes and resources for using API Logic Server, Python, Flask, SQLAlchemy, etc.