---
version info: 0.7 (9/15/2024)
---
## Welcome to API Logic Server

1. ***Instant microservices*** (APIs and Admin Apps) from a database or **GenAI prompt** -- 1 command

2. ***Customize*** with **Rules** and Python in your IDE: created projects use standard Python libraries (Flask, SQLAlchemy)

</br>

> **Evaluation Guide:** open *"1. Existing Database - pre-installed sample database"*, below.

You are in the [API Logic Server Manager](https://apilogicserver.github.io/Docs/Manager/).  This is a good place to manage projects, create notes and resources, etc.

<details markdown>

<summary>How to Run Projects from the Manager </summary>

<br>You typically run projects by opening an IDE on the project folder, using provided Run Configurations.

For a quick preview, you can also run from the Manager; there are 2 ways:

1. Use ***another instance of VSCode.***  You can *examine* them in this current instance, but *run* them in their own instance.

    * To do so, you probably want to acquire this extension: `Open Folder Context Menus for VS Code`. It will enable you to open the sample, tutorial or your own projects in another instance of VSCode.

    * This option provides more Run/Debug options (e.g., run without security, etc),

2. Or, use the Run/Debug Entry: `API Logic Server Run (run project from manager)`

</details>
</br>

<details markdown>

<summary>How API Logic Server provides GenAI Microservice Automation </summary>

&nbsp;

## Using GenAI Microservice Automation

Use the CLI (Command Language Interface, in your IDE) to create projects from either existing databases, or GenAI prompts.  This creates a project you can open, run and customize in your IDE.

[![GenAI Automation](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/copilot/genai-automation-video.png?raw=true)](https://www.youtube.com/watch?v=LSh7mqGiT0k&t=5s "Microservice Automation")

&nbsp;

## What Is API Logic Server

It's an open source Python project consisting of a CLI to create projects, and runtime libraries to execute them.

[![Architecture](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/Architecture-What-Is.png?raw=true)](https://apilogicserver.github.io/Docs/Architecture-What-Is/#runtimes-and-cli)

&nbsp;

## Modern Scalable Runtime Architecture

Created projects use standard Flask and SQLAlchemy; automation is provided by Logic Bank (the rule engine) and SAFRS (JSON:APIs).  Scripts are provided to containerize projects, and deploy to Azure.

[![Architecture - Runtime](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/Architecture-Runtime-Stack.png?raw=true)](https://apilogicserver.github.io/Docs/Architecture-What-Is/#key-runtime-components)

&nbsp;

</details>

&nbsp;

## Explore Pre-created Samples

<details markdown>

<summary> Explore Pre-created Samples</summary>

<br>The `samples` folder has pre-created important projects you will want to review at some point (Important: look for **readme files**):

* [nw_sample_nocust](https://apilogicserver.github.io/Docs/Tutorial/) - northwind (customers, orders...) database

    * This reflects the results you can expect with your own databases

* [nw_sample](https://apilogicserver.github.io/Docs/Sample-Database/) - same database, but with ***with [customizations](https://apilogicserver.github.io/Docs/IDE-Customize/) added***.  It's a great resource for exploring how to customize your projects.

    * Hint: use your IDE to search for `#als`

* [tutorial](https://apilogicserver.github.io/Docs/Tutorial/) - short (~30 min) walk-through of using API Logic Server using the northwind (customers, orders...) database

</br>

<details markdown>

<summary>You can always re-create the samples</summary>

<br>Re-create them as follows:

1. Open a terminal window (**Terminal > New Terminal**), and paste the following CLI command:

```bash
ApiLogicServer create --project-name=samples/tutorial --db-url=
ApiLogicServer create --project-name=samples/nw_sample --db-url=nw+
ApiLogicServer create --project-name=samples/nw_sample_nocust --db-url=nw
```
</details>


</details>


&nbsp;

##  Explore Creating Projects

Click on the disclosure buttons, below.  (Important: look for **readme files.**)
</br>

<details markdown>

<summary> 1. Existing Database - pre-installed sample databases </summary>

<br>For a self-demo, use the CLI (**Terminal > New Terminal**), and try the pre-installed [**Basic Demo**](https://apilogicserver.github.io/Docs/Sample-Basic-Demo/):

```
als create --project-name=basic_demo --db-url=basic_demo
```

<br>To create a larger project, try the pre-installed [**northwind database**](https://apilogicserver.github.io/Docs/Tutorial/) (imagine your own database here):

```
als create --project-name=nw_sample_nocust --db-url=sqlite:///nw.sqlite
```

<br>See **with customizations** in the [pre-created sample apps](#important-pre-created-sample-apps).  This is an **important learning resource**.

Then, try your own databases [(db-url examples here)](https://apilogicserver.github.io/Docs/Database-Connectivity/), or experiment with [these Docker databases](https://apilogicserver.github.io/Docs/Database-Docker/).

</details>
</br>

<details markdown>

<summary> 2. New Database - using GenAI Microservice Automation (Experiment with AI - Signup optional)</summary>

<br>You can do this with or without signup:

1. If you have signed up, this will create and open a project called `genai_demo` from `genai_demo.prompt` (available in left Explorer pane):

```bash
als genai --using=system/genai/examples/genai_demo/genai_demo.prompt
```


2. ***Or,*** you can simulate the process (no signup) using:


```bash
als genai --using=genai_demo.prompt --repaired-response=system/genai/temp/chatgpt_retry.response
```
</br>

<details markdown>

<summary> What Just Happened? &nbsp;&nbsp;&nbsp;Next Steps...</summary>

<br>`genai` processing is shown below (internal steps denoted in grey):

1. You create your.prompt file, and invoke `als genai --using=your.prompt`.  genai then creates your project as follows:

    a. Submits your prompt to the `ChatGPT API`

    b. Writes the response to file, so you can correct and retry if anything goes wrong

    c. Extracts model.py from the response

    d. Invokes `als create-from-model`, which creates the database and your project

2. Your created project is opened in your IDE, ready to execute and customize.  

    a. Review `Sample-Genai.md`, Explore Customizations.

![GenAI Automation](system/images/genai.png)

</details>
</br>


<details markdown>

<summary> You can iterate</summary>

<br>You can add new columns/tables, while keeping the prior model intact:

```bash title="Iterate"
als genai --project-name='genai_demo_conversation' --using=system/genai/examples/genai_demo/genai_demo_conversation
# open Docs/db.dbml
```
</details>
</br>

<details markdown>

<summary> You can also execute directly, and iterate</summary>

<br>You can add new columns/tables, while keeping the prior model intact:

```bash title="Iterate"
# create project without creating a file...
als genai-create --project-name='customer_orders' --using='customer orders'

als genai-iterate --using='add Order Details and Products'
# open Docs/db.dbml
```

</details>
</br>

<details markdown>

<summary> AI somtimes fails - here's how to recover</summary>

<br>AI results are not consistent, so the model file may need corrections.  You can find it at `system/genai/temp/model.py`.  You can correct the model file, and then run:

```bash
als create --project-name=genai_demo --from-model=system/genai/temp/create_db_models.py --db-url=sqlite
```

Or, correct the chatgpt response, and

```bash
als genai --using=genai_demo.prompt --repaired-response=system/genai/temp/chatgpt_retry.response
```

We have seen failures such as:

* duplicate definition of `DECIMAL`
* unclosed parentheses
* data type errors in test data creation
* wrong engine import: from logic_bank import Engine, constraint
* bad test data creation: with Engine() as engine...
* Bad load code (no session)

</details>
</br>

<details markdown>

<summary> Postgresql Example </summary>

You can test this as follows:

1. Use [our docker image](https://apilogicserver.github.io/Docs/Database-Docker/):
2. And try:

```bash
als genai --using=system/genai/examples/postgres/genai_demo_pg.prompt --db-url=postgresql://postgres:p@localhost/genai_demo
```

Provisos:

* You have to create the database first; we are considering automating that: https://stackoverflow.com/questions/76294523/why-cant-create-database-if-not-exists-using-sqlalchemy

</details>
</details>
</br>

<details markdown>

<summary> 3. New Database - using Copilot (Signup optional) </summary>

<br>You can use Copilot chat (if extension installed; if not, skip to step 3):

1. Create a model, eg:

<details markdown>

<summary> Show Me How to Use Copilot </summary>

<br>>Paste this into the Copilot prompt:

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

</details>
</br>

<details markdown>

<summary> 4. New Database - using ChatGPT in the Browser (Signup not required)</summary>

<br>A final option for GenAI is to use your Browser with ChatGPT.

Please see [this doc](https://apilogicserver.github.io/Docs/Sample-AI-ChatGPT/)

</details>

&nbsp;

&nbsp;

## Appendix: Quick Basic Demo

This is a "cheat sheet" for experienced ALS users, e.g., to show your colleagues.

<details markdown>

<summary>Quick Basic Demo - Instructions</summary>

<br>This demo creates and customizes a project, starting from a database:

```bash title="Quick Basic Demo"

# Microservice Automation
# Admin App, API, Project
als create --project-name=basic_demo --db-url=basic_demo

# Logic and Security
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

</details>


&nbsp;

## Appendix: GenAI Demo

This is a "cheat sheet" for experienced ALS users, e.g., to show your colleagues.

<details markdown>

<summary>Quick GenAI Demo - Instructions</summary>

<br>This demo creates and customizes a project, starting from a prompt:

```bash title="Quick GenAI Demo"

# Microservice Automation from GenAI Prompt
# Admin App, API, Project
als genai --using=system/genai/examples/genai_demo/genai_demo.prompt

# Or, Microservice Automation from Saved Response
# Admin App, API, Project
als genai --using=genai_demo.prompt --repaired-response=system/genai/temp/chatgpt_retry.response

# Logic and Security
#   - see logic (logic/declare_logic.py, logic/cocktail-napkin.jpg);  add an Order and Item
#   - see security (security/declare_security.py); compare customers, s1 vs. admin
# Python Extensibility, Kafka Integration, Rebuild Iteration
#   - see logic/declare_logic.py (breakpoint for Kafka)
#   - Swagger: ServicesEndPoint.OrderB2B
als add-cust
```

</details>
