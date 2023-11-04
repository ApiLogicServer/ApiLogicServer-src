---
title: Instant Microservices - with Logic and Security
notes: gold is proto (-- doc)
---

Learn how build a complete database system -- in minutes instead of weeks or months:

1. **An API**, and, we'll add ui and logic to make it a microservice...
2. **Logic and Security:** multi-table constraints and derivations, and role-based security
3. **An Admin App:** and finally, a multi-page, multi-table web app

We'll use API Logic Server, providing:

| Key Feature | Providing | Why It Matters|
| :--- |:---|:---|
| **Automation** | Instant Project Creation, providing...<br>An API and an Admin web app  | Unblock UI App Dev<br>Instant Agile Collaboration |
| **Customization** | Declarative logic and security <br> 5 rules vs. 200 lines of Python | Half the effort reduced 40X |
| **Iteration** | Revising the data model, and <br>Adding rules plus Python | Iterative development <br> Extensiblity with Python |

The entire process takes 5 minutes, instead of several weeks using traditional  development.

&nbsp;

## 1. Automation: Instant Project

This project was created with a command like:

```bash
$ ApiLogicServer create --project_name=basic_demo --db_url=basic_demo
```

> Note: the `db_url` value is [an abbreviation](https://apilogicserver.github.io/Docs/Data-Model-Examples/).  You would normally supply a SQLAlchemy URI.

This creates a project you can open with VSCode by reading your schema.  The database is Customer, Orders, Items and Product, as shown in the Appendix.

You can run as follows:

1. **Virtual Environment:** create one as shown in the Appendix.

2. **Start the Server:** also described in the Appendix

3. **Start the Admin App:** either use the links provided in the IDE console, or click [http://localhost:5656/](http://localhost:5656/)

The sections below describe what has been created.

&nbsp;

### API with Swagger

The system creates an API with end points for each table, with filtering, sorting, pagination, optimistic locking and related data access -- **[self-serve](https://apilogicserver.github.io/Docs/API-Self-Serve/), ready for custom app dev.**

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/api-swagger.jpeg?raw=true">

### Admin App

It also creates an Admin App: multi-page, multi-table apps -- ready for **[business user agile collaboration](https://apilogicserver.github.io/Docs/Tech-AI/),** and back office data maintenance.  This complements custom UIs created with the API.

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/admin-app-initial.jpeg?raw=true">

## 2. Customize in your IDE

While automation is always welcomed, it's critical to add logic and security.  Here's how.

&nbsp;

### Declare Security

To add security:

**1. Stop the Server** (see Appendix)

**2. Add Security**

In a terminal window for your project:

```bash
ApiLogicServer add-auth --project_name=. --db_url=auth
```
&nbsp;

At this point, you'd use your IDE to declare grants and filters.  Simulate this as follows:

**3. Declare Grants:** Copy `customomizations/declare_security` over `security/declare_security`

To see security in action:

**4. Start the Server**

**5. Start the Admin App:** either use the links provided in the IDE console, or click [http://localhost:5656/](http://localhost:5656/)

**6. Login** as `s1`, password `p`

**7. Click Customers**

In the IDE Console Log, observe the logging assists in debugging:

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/security-filters.jpeg?raw=true">

&nbsp;

### Declare Logic

Logic (multi-table derivations and constraints) is typically a significant portion of a system, nearly half.  API Logic server provides spreadsheet-like rules that dramatically simplify and accelerate logic development.

Rules are declared in Python, simplified with IDE code completion.  Simulate this as follows:

**1. Stop the Server**

At this point, you'd use your IDE to declare grants and filters.  Simulate this as follows:

**2. Declare Logic:** Copy `customomizations/declare_logic` over `logic/declare_logic`

Rules are an executable design.  Use your IDE (code completion, etc), to replace 280 lines of code with the 5 spreadsheet-like rules in `logic/declare_logic.py`.  Note they map exactly to our natural language design.

**3. Test using the Admin App - add an Order and Item**

Observe the rules firing in the console log, as shown in the next screen shot.

Logic provides significant improvements over procedural logic, as described below.

&nbsp;

#### a. Complexity Scaling

The screen below shows our logid declarations, and the logging for inserting an `Item`.  Each line represents a rule firing, and shows the complete state of the row.

Note that it's `Multi-Table Transaction`, as indicating by the indentation.  This is because **rules automatically chain, *including across tables.***

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/logic-chaining.jpeg?raw=true">

#### b. 40X More Concise

Spreadsheet-like rules [40X more concise](https://github.com/valhuber/LogicBank/wiki/by-code).

&nbsp;

#### c. Automatic Re-use

The logic above, perhaps conceived for Place order, applies automatically to all transactions: deleting an order, changing items, moving an order to a new customer, etc.

&nbsp;

#### d. Automatic Optimizations

SQL overhead is minimized by pruning, and by elimination of expensive aggregate queries.  These can result in orders of magnitude impact.

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
           amount = amount * Decimal(0.9)  # breakpoint here
       return amount

   Rule.formula(derive=models.Item.Amount, calling=derive_amount)
```

&nbsp;

This simple example illustrates some significant aspects of iteration, described in the sub-sections bdelow.

&nbsp;

### a. Maintenance Automation

Along with perhaps documentation, one of the tasks programmers most loathe is maintenance.  That’s because it’s not about writing code, but it’s mainly archaeology - deciphering code someone else wrote, just so you can add 4 or 5 lines they’ll hopefully be called and function correctly.

Rules change that, since they self-order their execution (and pruning) based on system-discovered dependencies.  So, to alter logic, you just “drop a new rule in the bucket”, and the system will ensure it’s called in the proper order, and re-used over all the Use Cases to which it applies.

&nbsp;

### b. Extensibile with Python

In this case, we needed to do some if/else testing, and it was more convenient to add a dash of Python.  While you have the full object-oriented power of Python, this is simpler -- more like Python as a 4GL.  

What’s important is that once you are in such functions, you can utilize Python libraries, invoke shared code, make web service calls, send email or messages, etc.  You have all the power of rules, plus the unrestricted flexibility of Python.

&nbsp;

### c. Debugging: IDE, Logging

The screen shot above illustrates that debugging logic is what you’d expect: use your IDE's debugger.

In addition, the Logic Log lists every rule that fires, with indents for multi-table chaining (not visible in this screenshot).  Each line shows the old/new values of every attribute, so the transaction state is transparent.

&nbsp;

### d. Customizations Retained

Note we rebuilt the project from our altered database, illustrating we can **iterate preserving customizations.**

&nbsp;

## API Customization: Standard

Of course, we all know that all businesses the world over depend on the `hello world` app.  This is provided in `api/customize_api`.  Observe that it's:

* standard Python

* using Flask

* and, for database access, SQLAlchemy.  Note all updates from custom APIs also enforce your logic.

&nbsp;

## Summary

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/summary.jpeg?raw=true">

In minutes, you've used API Logic Server to convert an idea into working software, deployed for collaboration, and iterated to meet new requirements.

&nbsp;

## Appendix: Database Schema

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/basic_demo_data_model.jpeg?raw=true" width="500">

&nbsp;

## Appendix: Procedures

You can use either VSCode or Pycharm.  You will need to:

&nbsp;

**Establish your Virtual Environment**

Python employs a virtual environment for project-specific dependencies.  Create one as shown below, depending on your IDE.

For VSCode:

Establish your `venv`, and run it via the first pre-built Run Configuration.  To establish your venv:

```bash
python -m venv venv; venv\Scripts\activate     # win
python3 -m venv venv; . venv/bin/activate      # mac/linux
pip install -r requirements.txt
```

For PyCharm, you will get a dialog requesting to create the `venv`; say yes.

See [here](https://apilogicserver.github.io/Docs/Install-Express/) for more information.

&nbsp;

**Start and Stop the Server**

Both IDEs provide Run Configurations to start programs.  These are pre-built by `ApiLogicServer create`.

For VSCode, start the Server with F5, Stop with Shift-F5 or the red stop button.

For PyCharm, start the server with CTL-D, Stop with red stop button.

&nbsp;

## Appendix: Containerize, Deploy for Collaboration

API Logic Server also creates scripts for deployment.  While these are ***not required at this demo,*** this means you can enable collaboration with Business Users:

1. Create a container from your project -- see `devops/docker-image/build_image.sh`
2. Upload to Docker Hub, and
3. Deploy for agile collaboration.

