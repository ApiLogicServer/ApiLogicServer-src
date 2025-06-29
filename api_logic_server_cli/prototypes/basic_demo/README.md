---
title: Instant Microservices - with Logic and Security
notes: gold is proto (-- doc); alert for apostrophe
version: 0.21 from pip
---

See how to build a complete database system -- in minutes instead of weeks or months:

1. **An API**, and, we'll add ui and logic to make it a microservice...
2. **Logic and Security:** multi-table constraints and derivations, role-based security, and application integration
3. **An Admin App:** a multi-page, multi-table web app 
4. **Customizable:** use your IDE to customize with declarative rules and standard Python

&nbsp;

We'll illustrate [API Logic Server](https://www.genai-logic.com/product/key-features){:target="_blank" rel="noopener"} basic GenAI-Logic operation: creating projects from new or existing databases, adding logic and security, and customizing your project using your IDE and Python.

The entire process takes 20 minutes, instead of several weeks using traditional development.

You can use this article in several ways:

* Conceptual Overview - the main article focuses on the concepts and basic process.  Operational details are moved to the Appendix to retain focus.

* Self-demo - [install](Install-Express.md){:target="_blank" rel="noopener"} and create this system yourself.

* Self-demo with video - you can also use [this video](https://www.youtube.com/watch?v=sD6RFp8S6Fg) (it's the same system, but the database is created with ChatGPT).

&nbsp;

## 1. Automation: Project Creation

API Logic Server can create projects from existing databases, or use GenAI to create projects with new databases.  See the sub-sections below.

&nbsp;
### Create From Existing Database

This project was created with a command like:

```bash
$ ApiLogicServer create --project_name=basic_demo --db_url=basic_demo
```

> Note: the `db_url` value is [an abbreviation](https://apilogicserver.github.io/Docs/Data-Model-Examples/){:target="_blank" rel="noopener"} for a test database provided as part of the installation.  You would normally supply a SQLAlchemy URI to your existing database.

This creates a project by reading your schema.  The database is Customer, Orders, Items and Product, as shown in the Appendix.

&nbsp;

### Create With New Database

You can create a project from a prompt using GenAI, either by [WebGenAI](WebGenAI.md), or the the [GenAI CLI](WebGenAI-CLI.md){:target="_blank" rel="noopener"} as shown here.

Use the GenAI CLI with or without signup:

1. If you have signed up (see *Obtain a OpenAI API Key*, below), this will create and open a project called `genai_demo` from `genai_demo.prompt` (available in left Explorer pane):

```bash
als genai --using=system/genai/examples/genai_demo/genai_demo.prompt --project-name=genai_demo
```

  

2. ***Or,*** you can simulate the process (no signup) using:

```bash

als genai --repaired-response=system/genai/examples/genai_demo/genai_demo.response_example --project-name=genai_demo

```

&nbsp;
### Open in your IDE and Run

You can open with VSCode, and run it as follows:

1. **Create Virtual Environment:** as shown in the Appendix.

2. **Start the Server:** F5 (also described in the Appendix).

3. **Start the Admin App:** either use the links provided in the IDE console, or click [http://localhost:5656/](http://localhost:5656/).  The screen shown below should appear in your Browser.

The sections below explore the system that has been created (which would be similar for your own database).
<br><br>

!!! pied-piper ":bulb: Automation: Instant API, Admin App (enable UI dev, agile collaboration)"

    ### a. API with Swagger

    The system creates an API with end points for each table, with filtering, sorting, pagination, optimistic locking and related data access -- **[self-serve](https://apilogicserver.github.io/Docs/API-Self-Serve/), ready for custom app dev.**

    <img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/api-swagger.jpeg?raw=true">

    ### b. Admin App

    It also creates an Admin App: multi-page, multi-table -- ready for **[business user agile collaboration](https://apilogicserver.github.io/Docs/Tech-AI/),** and back office data maintenance.  This complements custom UIs created with the API.

    You can click Customer 2, and see their Orders, and Items.

    <img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/admin-app-initial.jpeg?raw=true">

&nbsp;

## 2. Declare Logic And Security

While API/UI automation is a great start, it's critical to enforce logic and security.  You do this in your IDE.  Here's how.

The following `add_customizations` process simulates:

* Adding security to your project, and
* Using your IDE to declare logic and security in `logic/declare_logic.sh` and `security/declare_security.py`.

> Declared security and logic are shown in the screenshots below.<br>It's quite short - 5 rules, 7 security settings.

To add customizations, in a terminal window for your project:

**1. Stop the Server** (Red Stop button, or Shift-F5 -- see Appendix)

**2. Add Customizations**

```bash
als add-cust
```
&nbsp;

### Declare Security

The `add_customizations` process above has simulated the `ApiLogicServer add-auth` command, and using your IDE to declare security in `logic/declare_logic.sh`.

To see security in action:

**1. Start the Server**  F5

**2. Start the Admin App:** [http://localhost:5656/](http://localhost:5656/)

**3. Login** as `s1`, password `p`

**4. Click Customers**

&nbsp;

!!! pied-piper ":bulb: Security: Authentication, Role-based Filtering, Logging"

    #### 1. Login now required

    #### 2. Role-Based Filtering

    Observe you now see fewer customers, since user `s1` has role `sales`.  This role has a declared filter, as shown in the screenshot below.

    #### 3. Transparent Logging

    The screenhot below illustrates security declaration and operation:

    * The declarative Grants in the upper code panel, and

    *  The logging in the lower panel, to assist in debugging by showing which Grants (`+ Grant:`) are applied:

    <img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/security-filters.jpeg?raw=true">

&nbsp;

### Declare Logic

Logic (multi-table derivations and constraints) is a significant portion of a system, typically nearly half.  API Logic server provides **spreadsheet-like rules** that dramatically simplify and accelerate logic development.

Rules are declared in Python, simplified with IDE code completion.  The screen below shows the 5 rules for **Check Credit Logic.**

The `add_customizations` process above has simulated the process of using your IDE to declare logic in `logic/declare_logic.sh`.

To see logic in action:

**1. In the admin app, Logout (upper right), and login as admin, p**

**2. Use the Admin App to add an Order and Item for `Customer 1`** (see Appendix)

Observe the rules firing in the console log, as shown in the next screenshot.

Logic provides significant improvements over procedural logic, as described below.

&nbsp;

!!! pied-piper ":bulb: Logic: Multi-table Derivations and Constraint Rules, 40X More Concise"

    #### a. Chaining

    The screenshot below shows our logic declarations, and the logging for inserting an `Item`.  Each line represents a rule firing, and shows the complete state of the row.

    Note that it's a `Multi-Table Transaction`, as indicated by the indentation.  This is because - like a spreadsheet - **rules automatically chain, *including across tables.***

    <img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/logic-chaining.jpeg?raw=true">

    #### b. 40X More Concise

    The 5 spreadsheet-like rules represent the same logic as 200 lines of code, [shown here](https://github.com/valhuber/LogicBank/wiki/by-code).  That's a remarkable 40X decrease in the backend half of the system.
    <br><br>

    #### c. Automatic Re-use

    The logic above, perhaps conceived for Place order, applies automatically to all transactions: deleting an order, changing items, moving an order to a new customer, etc.  This reduces code, and promotes quality (no missed corner cases).
    <br><br>

    #### d. Automatic Optimizations

    SQL overhead is minimized by pruning, and by elimination of expensive aggregate queries.  These can result in orders of magnitude impact.
    <br><br>

    #### e. Transparent

    Rules are an executable design.  Note they map exactly to our natural language design (shown in comments) - readable by business users.  

    Optionally, you can use the Behave TDD approach to define tests, and the Rules Report will show the rules that execute for each test.  For more information, [click here](https://apilogicserver.github.io/Docs/Behave-Logic-Report/).

&nbsp;

## 3. Iterate with Rules and Python

Not only are spreadsheet-like rules 40X more concise, they meaningfully simplify maintenance.  Let's take an example:

>> Give a 10% discount for carbon-neutral products for 10 items or more.

&nbsp;

The following `add_iteration` process simulates an iteration:

* acquires a new database with `Product.CarbonNeutral`

* issues the `genai-logic rebuild-from-database` command that rebuilds your project (the database models, the api), while preserving the customizations we made above.

* acquires a revised `ui/admin/admin.yaml` that shows this new column in the admin app

* acquires this revised logic - in `logic/declare_logic.py`, we replaced the 2 lines for the `models.Item.Amount` formula with this (next screenshot shows revised logic executing with breakpoint):

```python
    def derive_amount(row: models.Item, old_row: models.Item, logic_row: LogicRow):
        amount = row.Quantity * row.UnitPrice
        if row.Product.CarbonNeutral and row.Quantity >= 10:
           amount = amount * Decimal(0.9)  # breakpoint here
        return amount

    Rule.formula(derive=models.Item.Amount, calling=derive_amount)
```

&nbsp;

To add this iteration, repeat the process above - in a terminal window for your project:

**1. Stop the Server** (Red Stop button, or Shift-F5 -- see Appendix)

**2. Add Iteration**

```bash
als add-cust
```
&nbsp;

**3. Set the breakpoint as shown in the screenshot below**

**4. Test: Start the Server, login as Admin**

**5. Use the Admin App to update your Order by adding 12 `Green` Items**

At the breakpoint, observe you can use standard debugger services to debug your logic (examine `Item` attributes, step, etc).

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/logic-debugging.jpeg?raw=true">

&nbsp;

This simple example illustrates some significant aspects of iteration, described in the sub-sections below.

!!! pied-piper ":bulb: Iteration: Automatic Invocation/Ordering, Extensible, Rebuild Preserves Customizations"

    ### a. Dependency Automation

    Along with perhaps documentation, one of the tasks programmers most loathe is maintenance.  That's because it's not about writing code, but it's mainly archaeology - deciphering code someone else wrote, just so you can add 4 or 5 lines that will hopefully be called and function correctly.

    Rules change that, since they **self-order their execution** (and pruning) based on system-discovered dependencies.  So, to alter logic, you just "drop a new rule in the bucket", and the system will ensure it's called in the proper order, and re-used over all the Use Cases to which it applies.  Maintenance is **faster, and higher quality.**
    <br><br>

    ### b. Extensibile with Python

    In this case, we needed to do some if/else testing, and it was convenient to add a pinch of Python. Using "Python as a 4GL" is remarkably simple, even if you are new to Python.

    Of course, you have the full object-oriented power of Python and its many libraries, so there are *no automation penalty* restrictions.  
    <br>

    ### c. Debugging: IDE, Logging

    The screenshot above illustrates that debugging logic is what you'd expect: use your IDE's debugger.  This "standard-based" approach applies to other development activities, such as source code management, and container-based deployment.
    <br><br>

    ### d. Customizations Retained

    Note we rebuilt the project from our altered database, illustrating we can **iterate, while *preserving customizations.***

&nbsp;

## 4. API Customization: Standard

Of course, we all know that all businesses the world over depend on the `hello world` app.  This is provided in `api/customize_api`.  Observe that it's:

* standard Python

* using Flask

* and, for database access, SQLAlchemy.  Note all updates from custom APIs also enforce your logic.

&nbsp;

### Messaging With Kafka

Along with APIs, messaging is another technology commonly employed for application integration.  See the screenshot below; for more information, see [Sample Integration](Sample-Integration.md##produce-ordershipping-message){:target="_blank" rel="noopener"}.

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/order-to-shipping.jpg?raw=true">

&nbsp;

## 5. Deploy Containers: Collaborate

API Logic Server also creates scripts for deployment.  While these are ***not required at this demo,*** this means you can enable collaboration with Business Users:

1. Create a container from your project -- see `devops/docker-image/build_image.sh`
2. Upload to Docker Hub, and
3. Deploy for agile collaboration.

&nbsp;

## Summary

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/summary.jpeg?raw=true">

!!! pied-piper ":bulb: Instant Creation, Rules, Open Standards"
    
    In minutes - not days or weeks - you've used API Logic Server to convert an idea into **working software**, customized using **rule-based logic and security**, and **iterated** to meet new requirements.
    
    To dive deeper, you can install [API Logic Server](https://apilogicserver.github.io/Docs) and execute this demo - or create a system from your own databases.

&nbsp;

---

## Appendix: Database Schema

Initial version:

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/basic_demo_data_model.jpeg?raw=true" width="500">

End version:

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/basic_demo_data_model_end.png?raw=true" width="500">

&nbsp;

## Appendix: Quick Basic Demo

This is a "cheat sheet" for experienced ALS users, e.g., to show your colleagues:

```bash title="Quick Basic Demo"

# Microservice Automation
# Admin App, API, Project
als create --project-name=basic_demo --db-url=basic_demo

# Logic, Security and MCP example
# see logic (logic/declare_logic.py, logic/cocktail-napkin.jpg);  add an Order and Item
# see security (security/declare_security.py); compare customers, s1 vs. admin
als add-cust
als add-auth --db_url=auth

# Python Extensibility, Kafka Integration, Rebuild Iteration
# see logic/declare_logic.py (breakpoint for Kafka)
# Swagger: ServicesEndPoint.OrderB2B
als add-cust
als rebuild-from-database --db_url=sqlite:///database/db.sqlite
```

&nbsp;

## Appendix: Procedures

Specific procedures for running the demo are here, so they do not interrupt the conceptual discussion above.

You can use either VSCode or Pycharm.

&nbsp;

**1. Establish your Virtual Environment**

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

**2. Start and Stop the Server**

Both IDEs provide Run Configurations to start programs.  These are pre-built by `ApiLogicServer create`.

For VSCode, start the Server with F5, Stop with Shift-F5 or the red stop button.

For PyCharm, start the server with CTL-D, Stop with red stop button.

&nbsp;

**3. Entering a new Order**

To enter a new Order:

1. Click `Customer 1``

2. Click `+ ADD NEW ORDER`

3. Set `Notes` to "hurry", and press `SAVE AND SHOW`

4. Click `+ ADD NEW ITEM`

5. Enter Quantity 1, lookup "Product 1", and click `SAVE AND ADD ANOTHER`

6. Enter Quantity 2000, lookup "Product 2", and click `SAVE`

7. Observe the constraint error, triggered by rollups from the `Item` to the `Order` and `Customer`

8. Correct the quantity to 2, and click `Save`


**4. Update the Order**

To explore our new logic for green products:

1. Access the previous order, and `ADD NEW ITEM`

2. Enter quantity 11, lookup product `Green`, and click `Save`.

&nbsp;

## Appendix: Add Database Column

The database here is SQLite.  You can use the SQLite CLI to add a column using the terminal window of your IDE:

```bash
$ sqlite3 database/db.sqlite
>   alter table Products Add CarbonNeutral Boolean;
>   .exit
```

The SQLite DBMS is installed with API Logic Server, but the **CLI** is not provided on all systems.  If it's not installed, [you can install it like this](https://apilogicserver.github.io/Docs/Database-Connectivity/#sqlite).

## Appendix: Setup Codespaces

Codespaces enables you to run in the cloud: VSCode via your Browser, courtesy GitHub.  You can use codespaces on your GenAI project:

__1. Open your project on GitHub__

![API Logic Server Intro](images/sample-ai/genai/open-github.png)

__2. Open it in Codespaces (takes a minute or 2):__

![API Logic Server Intro](images/sample-ai/genai/start-codespaces.png)

> You will now see your project - running in VSCode, _in the Browser._  But that's just what you _see..._

> Behind the scenes, Codespaces has requisitioned a cloud machine, and loaded your project - with a _complete development environment_ - Python, your dependencies, git, etc.  

> You are attached to this machine in your Browser, running VSCode.

> :trophy: Pretty remarkable.

__3. Start the Server and open the App in the Browser__

* Use the pre-defined Launch Configuration

![API Logic Server Intro](images/git-codespaces/start-codespaces.png)


We think you'll find Codespaces pretty amazing - check it out!

&nbsp;

## Appendix: Obtain an OpenAI ApiKey

To obtain a ChatGPT API Key
<br>GenAI-Logic uses OpenAI, which requires an Open API Key:

1. Obtain one from [here](https://platform.openai.com/account/api-keys) or [here](https://platform.openai.com/api-keys)

2. Authorize payments [here](https://platform.openai.com/settings/organization/billing/overview)