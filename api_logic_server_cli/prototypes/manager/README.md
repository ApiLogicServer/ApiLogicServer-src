---
version info: 1.0 (01/11/2025)
---
## Welcome to API Logic Server

1. ***Instant microservices*** (APIs and Admin Apps) from a database or **GenAI prompt** -- 1 command

2. ***Customize*** with **Rules** and Python in your IDE: created projects use standard Python libraries (Flask, SQLAlchemy)

</br>

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

##  Explore Creating Projects

**Evaluation Guide:** click on the disclosure buttons, below.  Important: look for **readme files.**
</br>

<details markdown>

<summary> 1. Existing Database - pre-installed sample databases </summary>

<br>For a self-demo, use the CLI (**Terminal > New Terminal**), and try the pre-installed [**Basic Demo**](https://apilogicserver.github.io/Docs/Sample-Basic-Demo/):

```
als create --project-name=basic_demo --db-url=basic_demo
```

<br>The basic_demo project provides:
1. A quick look at logic, security and integration
2. Integration includes Kafka and MCP (**[Model Context Protocol](https://apilogicserver.github.io/Docs/Integration-MCP/)**)

<br>To create a larger project, try the pre-installed [**northwind database**](https://apilogicserver.github.io/Docs/Tutorial/) (imagine your own database here):

```
als create --project-name=nw_sample_nocust --db-url=sqlite:///nw.sqlite
```

<br>See **with customizations** in the [pre-created sample apps](#explore-pre-created-samples).  This is an **important learning resource**.

Then, try your own databases [(db-url examples here)](https://apilogicserver.github.io/Docs/Database-Connectivity/), or experiment with [these Docker databases](https://apilogicserver.github.io/Docs/Database-Docker/).

</details>
</br>

<details markdown>

<summary> 2. New Database - using GenAI Microservice Automation (Experiment with AI - Signup optional)</summary>

<br>You can do this with or without signup:

1. If you have signed up (see *To obtain a ChatGPT API Key*, below), this will create a new database and project called `genai_demo`, and open the project.  It's created using `genai_demo.prompt`, visible in left Explorer pane:

```bash
als genai --using=system/genai/examples/genai_demo/genai_demo.prompt --project-name=genai_demo
```


2. ***Or,*** you can simulate the process (no signup) using:


```bash
als genai --repaired-response=system/genai/examples/genai_demo/genai_demo.response_example --project-name=genai_demo
```

Verify it's operating properly:

1. Run Configurations are provided to start the server
2. Verify the logic by navigating to a Customer with an unshipped order, and altering one of the items to have a very large quantity
3. Observe the constraint operating on the rollup of order amount_totals.
    * View the logic in `logic/declare_logic.py`
    * Put a breakpoint on the `as_condition`.  Observe the console log to see rule execution for this multi-table transaction.

</br>


<details markdown>

<summary> To obtain a ChatGPT API Key</summary>

<br>GenAI-Logic uses OpenAI, which requires an Open API Key:

1. Obtain one from [here](https://platform.openai.com/account/api-keys) or [here](https://platform.openai.com/api-keys)
2. Authorize payments [here](https://platform.openai.com/settings/organization/billing/overview)

</details>

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

    a. Review `Tutorial.md`, Explore Customizations.

![GenAI Automation](system/images/genai.png)

</details>
</br>

<details markdown>

<summary> You can iterate the logic and data model</summary>

<br>The approach for an iteration is to create a new project from an existing one:

1. add another prompt to an existing projects `docs` directory, specifying your changes
2. use `als genai`, specifying 
    * `--using` existing projects `docs` directory, and 
    * `--project-name` as the output project
 
 **Logic iterations** are particuarly useful.  For example, here we take the basic check-credit logic, and add:

> Provide a 10% discount when buying more than 10 carbon neutral products.<br><br>The Item carbon neutral is copied from the Product carbon neutral

Explore [genai_demo_iteration_discount](system/genai/examples/genai_demo/genai_demo_iteration_discount).  It's an iteration of basic_demo (see system/genai/examples/genai_demo/genai_demo_iteration_discount/002_create_db_models.prompt).  This will add carbon_neutral to the data model, and update the logic to provide the discount:

```bash title='Iterate Business Logic'
# Iterate with data model and logic
als genai --project-name='genai_demo_with_discount' --using=system/genai/examples/genai_demo/genai_demo_iteration_discount
# open Docs/db.dbml
```

<br>

You can perform **model iterations:** add new columns/tables, while keeping the prior model intact.  First, we create a project with no logic, perhaps just to see the screens (this step is optional, provided just to illustrate that iterations create new projects from existing ones):

```bash title='Iterate Without Logic'
# Step 1 - create without logic
als genai --project-name='genai_demo_no_logic' --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt
# open Docs/db.dbml
```

Then, we would create another prompt in the docs directory with our model changes. We've already created these for you in `system/genai/examples/genai_demo/genai_demo_iteration` - we use that to alter the data model (see `system/genai/examples/genai_demo/genai_demo_iteration/004_iteration_renames_logic.prompt`):

```bash title='Iterate With Logic'
# Iterate with data model and logic
als genai --project-name='genai_demo_with_logic' --using=system/genai/examples/genai_demo/genai_demo_iteration
# open Docs/db.dbml
```

Explore [genai_demo_iteration](system/genai/examples/genai_demo/genai_demo_iteration) - observe the `--using` is a *directory* of prompts.  These include the prompts from the first example, plus an *iteration prompt* (`004_iteration_renames_logic.prompt`) to rename tables and add logic.


</details>
</br>

<details markdown>

<summary> You can declare informal logic</summary>

<br>You can declare rules using dot notation, or more informally:

```bash title="Informal Logic (no dot notation)"
als genai --using=system/genai/examples/genai_demo/genai_demo_informal.prompt --project-name=genai_demo_informal
```
</details>
</br>


<details markdown>

<summary> Multi-Rule Logic</summary>

<br>You can add new columns/tables, while keeping the prior model intact:

```bash title="Multi-Rule Logic"
als genai --using=system/genai/examples/emp_depts/emp_dept.prompt
```
</details>
</br>

<details markdown>

<summary> You can ask AI to suggest logic (great way to learn!)</summary>

<br>You can create a project, and ask GenAI for logic suggestions:

```bash title='1. Create Project, without Rules'
# 1. Create Project, without Rules
als genai --project-name='genai_demo_no_logic' --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt
```

```bash title="2. Request Rule Suggestions"
# 2. Request Rule Suggestions
cd genai_demo_no_logic
als genai-logic --suggest
```

You can review the [resultant logic suggestions](genai_demo_no_logic/docs/logic_suggestions) in the `genai_demo_no_logic` project:

 * See and edit: `docs/logic_suggestions/002_logic_suggestions.prompt` (used in step 3, below)
    * This corresponds to the Logic Editor - Logic View in the WebGenAI web app

```bash title="3. See the rules for the logic"
# 3. See the rule code for the logic
als genai-logic --suggest --logic='*'
```

Important notes about suggestions and generated code:
* `--suggest --logic='*'` is intended to enable you to identify logic that does not translate into proper code
* The example above was pretty good, but sometimes the results are downright silly:
    * Just run suggest again, or
    * Repair `docs/logic_suggestions/002_logic_suggestions.prompt`

Also...
* It is not advised to paste the code into `logic/declare_logic.py`
    * The suggested logic may result in new data model attributes
    * These are created automatically by running `als genai` (next step)

The [logic suggestions directory](genai_demo_no_logic/docs/logic_suggestions) now contains the prompts to create a new project with the suggested logic.  
When you are ready to proceed:
1. Execute the following to create a *new project* (iteration), with suggested logic:

```bash title="4. Create a new project with the Rule Suggestions"
# 4. Create a new project with the Rule Suggestions
cd ..  # important - back to manager root dir
als genai --project-name='genai_demo_with_logic' --using=genai_demo_no_logic/docs/logic_suggestions
```

Observe:
1. The created project has the rule suggestions in `logic/declare_logic.py`
2. A revised Data Model in `database/models.py` that includes attributes introduced by the logic suggestions
3. Revised test database, initialized to reflect the derivations in the suggested logic

Internal Note: this sequence available in the run configs (s1/s4).

</details>

</br>

<details markdown>

<summary>Fixup - update data model with new attributes from rules</summary>

<br>Fixes project issues by updating the Data Model and Test Data:
when adding rules, such as using suggestions, you may introduce new attributes.
If these are missing, you will see exceptions when you start your project.

The `genai-utils --fixup` fixes such project issues by updating the Data Model and Test Data:

1. Collects the latest model, rules, and test data from the project. 
2. Calls ChatGPT (or similar) to resolve missing columns or data in the project.
3. Saves the fixup request/response under a 'fixup' folder.
4. You then use this to create a new project

***Setup***

After starting the [Manager](https://apilogicserver.github.io/Docs/Manager): 

```bash title="0. Create Project Requiring Fixup"
# 0. Create a project requiring fixup
als genai --repaired-response=system/genai/examples/genai_demo/genai_demo_fixup_required.json --project-name=genai_demo_fixup_required
```

If you run this project, you will observe that it fails with:
```bash
Logic Bank Activation Error -- see https://apilogicserver.github.io/Docs/WebGenAI-CLI/#recovery-options
Invalid Rules:  [AttributeError("type object 'Customer' has no attribute 'balance'")]
Missing Attrs (try als genai-utils --fixup): ['Customer.balance: constraint']
```
&nbsp;

***Fixup***

To Fix it:
```bash title="1. Run FixUp to add missing attributes to the fixup response data model"
# 1. Run FixUp to add missing attributes to the data model
cd genai_demo_fixup_required
als genai-utils --fixup
```

Finally, use the created [fixup files](genai_demo_fixup_required/docs/fixup/) to rebuild the project:
```bash title="2. Rebuild the project from the fixup response data model"
# 2. Rebuild the project from the fixup response data model
cd ../
als genai --repaired-response=genai_demo_fixup_required/docs/fixup/response_fixup.json --project-name=fixed_project
```
    
&nbsp;
The created project may still report some attributes as missing.  
(ChatGPT seems to often miss attributes mentioned in sum/count where clauses.)  To fix:

1. Note the missing attributes(s) from the log
2. Add them to `docs/003_suggest.prompt`
3. Rebuild the project: `als genai --project-name='genai_demo_with_logic' --using=genai_demo_no_logic/docs`


Internal Note: this sequence available in the run configs (f1/f2).

</details>


</br>

<details markdown>

<summary>Create from WebGenAI, and import (merge) subsequent changes</summary>

<br>You can use [WebGenAI](https://apilogicserver.github.io/Docs/WebGenAI/) to create a project, and export it.  

You (or colleagues) can make changes to both the WebGenAI project (on the web), and your downloaded project.  You can import the WebGenAI project, and the system will merge changes to the data model and rules automatically.  

This is possible since the logic is declarative, so ordering is automatic.  This eliminates the troublesome merge issues so prevalent in procedural code.  For more on import, [click here](https://apilogicserver.github.io/Docs/IDE-Import-WebGenAI/).

The Manager pre-installs a sample project you can use to explore import:

```bash
cd system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed
als genai-utils --import-genai --using=../wg_demo_no_logic_fixed
```
Observe:
1. The [data model](system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/database) contains `Customer.balance` and `Product.carbon_neutral`
2. The test data has been updated to include these attributes, with proper values

</details>

</br>

<details markdown>

<summary>Rebuild the test data</summary>

<br>Fixes project issues by rebuilding the database to conform to the derivation rules:

1. Create genai_demo: 
```
als genai --using=system/genai/examples/genai_demo/genai_demo.prompt --project-name=genai_demo
```
2. Rebuild:
```
cd genai_demo
als genai-utils --rebuild-test-data
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
als genai --repaired-response=system/genai/examples/genai_demo/genai_demo.response_example --project-name=genai_demo
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

5. Create business logic

    * You can create logic with either your IDE (and code completion), or Natural Language
    * To use Natural Language:

        1. Use the CoPilot chat,
        2. Paste the logic above
        3. Copy it to `logic/declare_logic.py` after `discover_logic()`
        
            * Alert:  Table and Column Names may require correction to conform to the model
            * Alert: you may to apply [defaulting](https://apilogicserver.github.io/Docs/Logic-Use/#insert-defaulting), and initialize derived attributes in your database

</details>
</br>

<details markdown>

<summary> 4. New Database - using ChatGPT in the Browser (Signup not required)</summary>

<br>A final option for GenAI is to use your Browser with ChatGPT.

Please see [this doc](https://apilogicserver.github.io/Docs/Sample-AI-ChatGPT/)

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

## Explore WebGenAI

In addition to the CLI examples above, you can use [WebGenAI](https://apilogicserver.github.io/Docs/WebGenAI/) - a web interface for creating projects from prompts.  You can install WebGenAI on a server, so that created projects are easy to review with colleagues.

To try WebGenAI:

```bash
cd webgenai
docker compose up
```

You will be directed to the registration process.  You will also require a ChatGPT API Key as described above.

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
als genai --repaired-response=system/genai/temp/chatgpt_retry.response

# Logic and Security
#   - see logic (logic/declare_logic.py, logic/cocktail-napkin.jpg);  add an Order and Item
#   - see security (security/declare_security.py); compare customers, s1 vs. admin
# Python Extensibility, Kafka Integration, Rebuild Iteration
#   - see logic/declare_logic.py (breakpoint for Kafka)
#   - Swagger: ServicesEndPoint.OrderB2B
als add-cust
```

</details>
