# Basic Demo

This illustrates:

1. Automation - instant project providing API, Admin web app
2. Customize - add declarative security and logic
3. Iterate -  Rules and Python

&nbsp;

## 1. Automation - instant project providing API, Admin web app

This project was created with a command like:

```bash
$ ApiLogicServer create --project_name=basic_demo --db_url=basic_demo
```

> Note: the `db_url` value is [an abbreviation](https://apilogicserver.github.io/Docs/Data-Model-Examples/).  You would normally supply a SQLAlchemy URI.

This creates a project you can open with VSCode by reading your schema.  The database looks like this:

<img src="https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/basic_demo/images/basic_demo_data_model.jpeg?raw=true" height="400rm">

Establish your `venv`, and run it via the first pre-built Run Configuration.  To establish your venv:

```bash
python -m venv venv; venv\Scripts\activate     # win
python3 -m venv venv; . venv/bin/activate      # mac/linux
pip install -r requirements.txt
```

&nbsp;

### API with Swagger

The system creates an API with end points for each table, with filtering, sorting, pagination, optimistic locking and related data access -- self-serve, ready for custom app dev.

<img src="https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/basic_demo/images/api-swagger.jpeg?raw=true">

### Admin App

It also creates an Admin App: multi-page, multi-table apps -- ready for business user agile collaboration.  This complements custom UIs created with the API.

<img src="https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/basic_demo/images/admin-app-initial.jpeg?raw=true">

## 2. Customize - add declarative security and logic

While automation is always welcomed, it's critical to add logic and security.  Here's how.

&nbsp;

### Declare Security

In a terminal window for your project:

```bash
ApiLogicServer add-auth --project_name=. --db_url=auth
```
&nbsp;

At this point, you'd use your IDE to declare grants and filters.  Simulate this as follows:

1. Copy `customomizations/declare_security` over `security/declare_security`

&nbsp;

### Declare Logic

Logic (multi-table derivations and constraints) is typically a significant portion of a system, nearly half.  API Logic server provides spreadsheet-like rules that dramatically simplify and accelerate logic development.

Rules are declared in Python, simplified with IDE code completion.  Simulate this as follows:

1. Copy `customomizations/declare_logic` over `logic/declare_logic`

Rules are an executable design.  Use your IDE (code completion, etc), to replace 280 lines of code with the 5 spreadsheet-like rules in `logic/declare_logic.py`.  Note they map exactly to our natural language design.

&nbsp;

#### Re-use and Optimization

Declarative logic has significant advantages over procedural code:

1. ***Automatic* Reuse:** the logic above, perhaps conceived for Place order, applies automatically to all transactions: deleting an order, changing items, moving an order to a new customer, etc.

2. ***Automatic* Optimizations:** sql overhead is minimized by pruning, and by elimination of expensive aggregate queries.  These can result in orders of magnitude impact.

&nbsp;

## 3. Iterate with Rules and Python

Not only are spreadsheet-like rules 40X more concise, they meaningfully simplify maintenance.  Let’s take an example.

>> Give a 10% discount for carbon-neutral products for 10 items or more.

Automation still applies; we execute the steps below.

&nbsp;

**a. Add a Database Column**

```bash
$ sqlite3 database/db.sqlite
>   alter table Products Add CarbonNeutral Boolean;
>   .exit
```

The SQLite DBMS is installed with API Logic Server, but the **CLI** is not provided on all systems.  If it's not installed:

1. Copy `database/basic_demo.sqlite` over `database/db.sqlite`

&nbsp;

**b. Rebuild the project, preserving customizations**

```bash
cd ..  project parent directory
ApiLogicServer rebuild-from-database --project_name=ai_customer_orders --db_url=sqlite:///ai_customer_orders/database/db.sqlite
```

&nbsp;

**c. Update your admin app**

Use your IDE to merge `/ui/admin/admin-merge.yml` -> `/ui/admin/admin.yml`.`

&nbsp;


**d. Declare logic**

```python
   def derive_amount(row: models.Item, old_row: models.Item, logic_row: LogicRow):
       amount = row.Quantity * row.UnitPrice
       if row.Product.CarbonNeutral and row.Quantity >= 10:
           amount = amount * Decimal(0.9)
       return amount

   Rule.formula(derive=models.Item.Amount, calling=derive_amount)
```

&nbsp;

This simple example illustrates some significant aspects of iteration.

&nbsp;

### Maintenance: Logic Ordering

Along with perhaps documentation, one of the tasks programmers most loathe is maintenance.  That’s because it’s not about writing code, but it’s mainly archaeology - deciphering code someone else wrote, just so you can add 4 or 5 lines they’ll hopefully be called and function correctly.

Rules change that, since they self-order their execution (and pruning) based on system-discovered dependencies.  So, to alter logic, you just “drop a new rule in the bucket”, and the system will ensure it’s called in the proper order, and re-used over all the Use Cases to which it applies.

&nbsp;

### Extensibility: Rules Plus Python

In this case, we needed to do some if/else testing, and it was more convenient to add a dash of Python.  While you have the full object-oriented power of Python, this is simpler, more like Python as a 4GL.  

What’s important is that once you are in such functions, you can utilize Python libraries, invoke shared code, make web service calls, send email or messages, etc.  You have all the power of rules, plus the unrestricted flexibility of Python.

&nbsp;

### Debugging: IDE, Logging

The screen shot above illustrates that debugging logic is what you’d expect: use your IDE's debugger.

In addition, the Logic Log lists every rule that fires, with indents for multi-table chaining (not visible in this screenshot).  Each line shows the old/new values of every attribute, so the transaction state is transparent.

&nbsp;

### Rebuild: Customizations Preserved

Note we rebuilt the project from our altered database, without losing customizations.

&nbsp;

## Summary

<img src="https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/basic_demo/images/summary.jpeg?raw=true">

In minutes, you've used API Logic Server to convert an idea into working software, deployed for collaboration, and iterated to meet new requirements.


## Appendix: Containerize, Deploy for Collaboration

API Logic Server also creates scripts for deployment.  While these are ***not required at this demo,*** this means you can enable collaboration with Business Users:

1. Create a container from your project -- see `devops/docker-image/build_image.sh`
2. Upload to Docker Hub, and
3. Deploy for agile collaboration.

