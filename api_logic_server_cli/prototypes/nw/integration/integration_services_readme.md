---
title: Declarative Application Integration
notes: pip
version: 0.01 from pip
---

# Purpose

Coming Soon -- see preview.

## System Requirements

This app illustrates using IntegrationServices for B2B integrations with APIs, and internal integration with messages.

We have the following **Use Cases:**

I. **Ad Hoc Requests** for information (Sales, Accounting) that cannot be anticipated in advance.

II. 2 **Two Transaction Sources:**

1. Order Entry UI for internal users
2. B2B partners post `OrderB2B` APIs in an agreed-upon format

The **Northwind API Logic Server** provides APIs *and logic* for both transaction sources:

1. **Self-Serve APIs**, to support

    1. Ad hoc Integration Requests
    2. UI developers to build the Order Entry UI

2. **Order Logic:** shared over both transaction sources, this logic

    1. Enforces database integrity (checks credit, reorders products)
    2. Provides Application Integration (alert shipping with a formatted Kafka message)

3. A **Custom API**, to match an agreed-upon format for B2B partners

The **Shipping API Logic Server** listens on kafka, and processes the message.

![overview](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/overview.jpg?raw=true)
&nbsp;

## Architecture Requirements

| Requirement | Poor Practice | Good Practice | Best Practice |
| :--- |:---|:---|:---|
| **Ad Hoc Integration** | ETL | APIs | **Automated** Self-Serve APIs |
| **UI App Dev** | Custom API Dev  | Self-Serve APIs | **Automated** Self-Serve APIs<br>**Automated Admin App** <br>.. (where applicable) |
| **Logic** | Logic in UI | Reusable Logic | **Declarative Business Rules**<br>.. extensible with Python |
| **Custom Integration** | | Custom APIs | Reusable integration services |

&nbsp;

### Ad Hoc Integration (vs. ETL)

It would be undesirable to require custom API development for ad integration: the inevitable series of requirements that do not stipulate an API contract.  So, our system should support **self-serve** APIs in addition to custom APIs.

Unlike Custom APIs which require server development, **Self-Serve APIs can be used directly by consumers to retrieve the attributes and related data they require.**  API consumers include:

* UI Developers - progress no longer blocked on custom server development

* Ad Hoc Integration - remote customers and organizations (Accounting, Sales) can similarly meet their own needs

&nbsp;

> **Avoid ETL:** Tradtional internal integration often involves ETL - Extract, Transfer and Load.  That is, each requesting system runs nightly programs to Extract the needed data, Transfer it to their location, and Load it for local access the next day.  This requires app dev for the extract, considerable bandwidth - all to see stale data.<br><br>In many cases, this might be simply to lookup a client's address.  For such requests, self-serve APIs can avoid ETL overhead, and provide current data.

&nbsp;

### UI App Dev on self-serve APIs

UI apps depend, of course, on APIs.  While these can be custom, the sheer number of such requests places a burden on the server team.  As for ad hoc integrations, a better approach is self-serve APIs.

In many systems, basic *"Admin"* UI apps can be automated, to address requirements when the UI needs are minimal.

&nbsp;

### Logic: Shared, Declarative

A proper architecture must consider where to place business logic (check credit, reorder products).  Such multi-table logic often consitutes nearly half the development effort.

> A poor practice is to place such logic on UI controller buttons.  It can be difficult or impossible to share this with the OrderB2B service, leading to duplication of efforts and inconsistency.

*Shared* logic is thus a requirement, to avoid duplication and ensure consistent results.  Ideally, such logic is declarative: much more concise, and automatically enforced, ordered and optimized.

&nbsp;

### Reusable Integration Services

Custom integrations require attribute map / alias services to transform data from remote formats to match our system objects.  In the sample here, this is required to transform incoming B2B APIs, and outgoing message publishing.

Ideally, our architecture can extract Integration Services for reuse, including attribute map / alias services, Lookups, and Cascade Add.  Details below.

&nbsp;

### Messaging

Note the integration to Shipping is via message, not APIs.  While both APIs and messages may can send data, there is an important difference:

* APIs are **synchronous**: if the remote server is down, the message fails.

* Messages are **async**: systems such as Kafka ensure that messages are delivered *eventually*, when the remote server is brought back online.

&nbsp;

# Development Overview

&nbsp;

## 1. Automation: Instant Project

This project was created with a command like:

```bash
$ ApiLogicServer create --project_name= db_url=nw-
```

> Note: the `db_url` value is [an abbreviation](https://apilogicserver.github.io/Docs/Data-Model-Examples/).  You would normally supply a SQLAlchemy URI.

This creates a project by reading your schema.  The database is Northwind (Customer, Orders, Items and Product), as shown in the Appendix.  

You can open with VSCode, and run it as follows:

1. **Create Virtual Environment:** as shown in the Appendix.

2. **Start the Server:** F5 (also described in the Appendix).

3. **Start the Admin App:** either use the links provided in the IDE console, or click [http://localhost:5656/](http://localhost:5656/).  The screen shown below should appear in your Browser.

The sections below explore the system that has been created (which would be similar for your own database).
<br><br>

!!! pied-piper ":bulb: Automation: Instant API, Admin App (enable UI dev, agile collaboration)"

    ### a. Self-Serve API, Swagger

    The system creates an API with end points for each table, with filtering, sorting, pagination, optimistic locking and related data access -- **[self-serve](https://apilogicserver.github.io/Docs/API-Self-Serve/), ready for ad hoc integration custom app dev.**

    <img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/api-swagger.jpeg?raw=true">

    ### b. Admin App

    It also creates an Admin App: multi-page, multi-table -- ready for **[business user agile collaboration](https://apilogicserver.github.io/Docs/Tech-AI/),** and back office data maintenance.  This complements custom UIs created with the API.

    You can click Customer 2, and see their Orders, and Items.

    <img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/admin-app-initial.jpeg?raw=true">

&nbsp;

## 2. Customize in your IDE

While API/UI automation is a great start, we now require Custom APIs, Logic and Security.  Here's how.

The following `apply_customizations` process simulates:

* Adding security to your project using a CLI command, and
* Using your IDE to:

    * declare logic in `logic/declare_logic.sh`
    * declare security in `security/declare_security.py`
    * implement custom APIs in `api/customize_api.py`, using <br>IntegrationServices declared in `integration/integration_services`

> These are shown in the screenshots below.<br>It's quite short - 5 rules, 7 security settings, and 120 lines for application integration.

To apply customizations, in a terminal window for your project:

**1. Stop the Server** (Red Stop button, or Shift-F5 -- see Appendix)

**2. Apply Customizations:**

```bash
ApiLogicServer add-cust
```

**3. Enable and Start Kafka:**

&nbsp;

<details markdown>

<summary>Enable and Start Kafka</summary>

To enable Kafka:

1. In `config.py`, find and comment out: `KAFKA_CONNECT = None  # comment out to enable Kafka`

2. Update your `etc/conf` to include the lines shown below (e.g., `sudo nano /etc/hosts`).

```
##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##

# for kafka
127.0.0.1       broker1
::1             localhost
255.255.255.255 broadcasthost
::1             localhost

127.0.0.1       localhost
# Added by Docker Desktop
# To allow the same kube context to work on the host and the container:
127.0.0.1 kubernetes.docker.internal
# End of section
```
3. Start Kafks: in a terminal window: `docker compose -f integration/kafka/docker_compose_start_kafka up`

</details>

### Declare Security

The `apply_customizations` process above has simulated the `ApiLogicServer add-auth` command, and using your IDE to declare security in `logic/declare_security.sh`.

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

    <img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/security-filters.jpeg?raw=true">

&nbsp;

### Declare Logic

Such logic (multi-table derivations and constraints) is a significant portion of a system, typically nearly half.  API Logic server provides **spreadsheet-like rules** that dramatically simplify and accelerate logic development.

Rules are declared in Python, simplified with IDE code completion.  The screen below shows the 5 rules for our **Check Credit Logic** noted in the initial diagram.

The `apply_customizations` process above has simulated the process of using your IDE to declare logic in `logic/declare_logic.sh`.

To see logic in action:

**1. In the admin app, Logout (upper right), and login as admin, p**

**2. Use the Admin App to add an Order and Item for `Customer 1`** (see Appendix), where the rollup of Item Amount to the Order exceed the credit limit.

Observe the rules firing in the console log, as shown in the next screenshot.

Logic provides significant improvements over procedural logic, as described below.

&nbsp;

!!! pied-piper ":bulb: Logic: Multi-table Derivation and Constraint Rules, 40X More Concise"

    #### a. Complexity Scaling

    The screenshot below shows our logic declarations, and the logging for inserting an `Item`.  Each line represents a rule firing, and shows the complete state of the row.

    Note that it's a `Multi-Table Transaction`, as indicated by the indentation.  This is because - like a spreadsheet - **rules automatically chain, *including across tables.***

    <img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/logic-chaining.jpeg?raw=true">

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

## 4. Iterate

**1. Set the breakpoint as shown in the screenshot below**

**2. Test: Start the Server, login as Admin**

At the breakpoint, observe you can use standard debugger services to debug your logic (examine `Item` attributes, step, etc).

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/logic-debugging.jpeg?raw=true">

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

## 4. Integration

TODO: pre-supplied integration services

![post order](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/post-orderb2b.jpg?raw=true)

![send order to shipping](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/order-to-shipping.jpg?raw=true)

```bash
ApiLogicServer curl "'POST' 'http://localhost:5656/api/ServicesEndPoint/OrderB2B'" --data '
{"meta": {"args": {"order": {
    "AccountId": "ALFKI",
    "Surname": "Buchanan",
    "Given": "Steven",
    "Items": [
        {
        "ProductName": "Chai",
        "QuantityOrdered": 1
        },
        {
        "ProductName": "Chang",
        "QuantityOrdered": 2
        }
        ]
    }
}}}'
```


&nbsp;

## 5. Deploy Containers: Collaborate

API Logic Server also creates scripts for deployment.  While these are ***not required at this demo,*** this means you can enable collaboration with Business Users:

1. Create a container from your project -- see `devops/docker-image/build_image.sh`
2. Upload to Docker Hub, and
3. Deploy for agile collaboration.

&nbsp;

# Status

12/02/2003 - runs, messaging is a TODO.

&nbsp;

# Appendix

## Apendix: Customizations

View them [here](https://github.com/ApiLogicServer/ApiLogicServer-src/tree/main/api_logic_server_cli/prototypes/nw).

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