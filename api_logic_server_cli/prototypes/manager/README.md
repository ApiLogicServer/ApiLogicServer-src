---
title: Welcome
Description: Instant mcp-enabled microservices, standard projects, declarative business logic
Source: docs/Manager-readme (this is copy version: api_logic_server_cli/prototypes/manager/README.md)
version info: 16.00.00 (02/09/2026)
do_process_code_block_titles: True
Used: Manager Readme
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>

# Welcome to GenAI-Logic

What is GenAI-Logic:

1. ***Instant mcp-enabled microservices*** (APIs and Admin Apps), from a database or **GenAI prompt** -- one command and you are ready for MCP, Vibe and Business User Collaboration.

2. ***Customize*** with **Declarative Rules** and Python in your IDE, standard container deployment

This is the start page for the [GenAI-Logic Manager](https://apilogicserver.github.io/Docs/Manager).  The Manager is a good place to manage projects, create notes and resources, etc.  

**🤖 Bootstrap Copilot by pasting the following into the chat:**
```bash title='🤖 Bootstrap Copilot by pasting the following into the chat'
Please load `.github/.copilot-instructions.md`.
```

> **Important:** be sure CoPilot is in "Agent" Mode.  "Ask" will not work.    Also, we get consistently good results with `Claude Sonnet 4.5`.

&nbsp;

---

# 🚀 First Time Here? Start with basic_demo

**Create basic_demo** (auto-opens with guided tour option):
```bash
genai-logic create --project_name=basic_demo --db_url=sqlite:///samples/dbs/basic_demo.sqlite
```

**Inside the project:** Say to your AI assistant: *"Guide me through basic_demo"* (30-45 min hands-on tour)

This tour teaches you the product basics: API creation, declarative rules, security, and Python customization. It's fail-safe (uses add-cust to restore if you make mistakes) and is the recommended starting point.

**For detailed self-paced exploration:** See [Sample-Basic-Demo](https://apilogicserver.github.io/Docs/Sample-Basic-Demo/)

&nbsp;

---

# 📚 Demo Catalog

## 0. Product Basics (Start Here)

Learn core concepts with the guided tour:

| Demo | Command | What You'll Learn | Duration |
|------|---------|-------------------|----------|
| **Basic Governed MCP Server** <br> basic_demo_ai_mcp_copilot | genai-logic create --project_name=basic_demo_ai_mcp_copilot --db_url=sqlite:///samples/dbs/basic_demo.sqlite | test rules via Copilot access to MCP Server | |

&nbsp;

## 1. Strategic Use Cases (From [genai-logic.com](https://www.genai-logic.com))

Explore the three key use cases from our home page:


| Use Case | Command | What You'll Learn |
|----------|---------|-------------------|
| **[Use Case 1: AI Rules](https://www.genai-logic.com/#h.no4671ezsiit)**<br> `basic_demo_ai_rules_supplier` | genai-logic create --project_name=basic_demo_ai_rules_supplier --db_url=sqlite:///samples/dbs/basic_demo.sqlite | Optimal Supplier |
| **[Use Case 2: Governed MCP Server](https://www.genai-logic.com/#h.n2vpyctb5xv)** <br>basic_demo_mcp_send_email | genai-logic create --project_name=basic_demo_mcp_send_email --db_url=sqlite:///samples/dbs/basic_demo.sqlite | Bus Users compose new service to send email to overdue customers, <br>subject to email opt-out |
| **[Use Case 3: Vibe Dev Backend](https://www.genai-logic.com/#h.75s0zu9xo7sa)** <br> basic_demo_vibe | genai-logic create --project_name=basic_demo_vibe --db_url=sqlite:///samples/dbs/basic_demo.sqlite | Cars and Maps |
| **[Use Case 4: Business Users](https://www.genai-logic.com/#h.68i3e948ivkl)** <br> webgenai | See [WebGenAI](webgenai/README.md) | WebG + download |

&nbsp;

## 2. Additional Demos

Advanced examples and specialized patterns:

| Demo | Command | What You'll Learn |
|------|---------|-------------------|
| **nw_integration** | genai-logic create --project_name=nw_integration --db_url=nw- | Kafka messaging (with docker setup) |
| **mcp_ai** | *TBD* | • Advanced MCP patterns<br>• Complex AI integrations<br>• Production MCP deployment |


&nbsp;

---

#  Explore GenAI CLI

<br>

<details markdown>

<summary>1. New Database - using GenAI Microservice Automation (Experiment with AI - Signup optional)</summary>

<br>You can do this with or without signup:

1. If you have signed up (see *Get an OpenAI Key*, below), this will create a new database and project called `genai_demo`, and open the project.  It's created using `genai_demo.prompt`, visible in left Explorer pane:

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

<summary> What Just Happened? &nbsp;&nbsp;&nbsp;Next Steps...</summary>

<br>`genai` processing is shown below (internal steps denoted in grey):

1. You create your.prompt file, and invoke `als genai --using=your.prompt`.  genai then creates your project as follows:

    a. Submits your prompt to the `ChatGPT API`

    b. Writes the response to file, so you can correct and retry if anything goes wrong

    c. Extracts model.py from the response

    d. Invokes `als create-from-model`, which creates the database and your project

2. Your created project is opened in your IDE, ready to execute and customize.  

    a. Review `Tutorial`, Explore Customizations.

![GenAI Automation](system/https://github.com/ApiLogicServer/Docs/blob/main/docs/images/genai.png?raw=true)

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

**Iterate Business Logic:**
**Iterate Business Logic:**
**Iterate Business Logic:**
```bash title='Iterate Business Logic'
# Iterate with data model and logic
als genai --project-name='genai_demo_with_discount' --using=system/genai/examples/genai_demo/genai_demo_iteration_discount
# open Docs/db.dbml
```

<br>

You can perform **model iterations:** add new columns/tables, while keeping the prior model intact.  First, we create a project with no logic, perhaps just to see the screens (this step is optional, provided just to illustrate that iterations create new projects from existing ones):

**Iterate Without Logic:**
**Iterate Without Logic:**
**Iterate Without Logic:**
```bash title='Iterate Without Logic'
# Step 1 - create without logic
als genai --project-name='genai_demo_no_logic' --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt
# open Docs/db.dbml
```

Then, we would create another prompt in the docs directory with our model changes. We've already created these for you in `system/genai/examples/genai_demo/genai_demo_iteration` - we use that to alter the data model (see `system/genai/examples/genai_demo/genai_demo_iteration/004_iteration_renames_logic.prompt`):

**Iterate With Logic:**
**Iterate With Logic:**
**Iterate With Logic:**
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

**Informal Logic (no dot notation):**
**Informal Logic (no dot notation):**
**Informal Logic (no dot notation):**
```bash title="Informal Logic (no dot notation)"
als genai --using=system/genai/examples/genai_demo/genai_demo_informal.prompt --project-name=genai_demo_informal
```
</details>
</br>


<details markdown>

<summary> Multi-Rule Logic</summary>

<br>You can add new columns/tables, while keeping the prior model intact:

**Multi-Rule Logic:**
**Multi-Rule Logic:**
**Multi-Rule Logic:**
```bash title="Multi-Rule Logic"
als genai --using=system/genai/examples/emp_depts/emp_dept.prompt
```
</details>
</br>

<details markdown>

<summary> You can ask AI to suggest logic (great way to learn!)</summary>

<br>You can create a project, and ask GenAI for logic suggestions:

**1. Create Project, without Rules:**
**1. Create Project, without Rules:**
**1. Create Project, without Rules:**
```bash title='1. Create Project, without Rules'
# 1. Create Project, without Rules
als genai --project-name='genai_demo_no_logic' --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt
```

**2. Request Rule Suggestions:**
**2. Request Rule Suggestions:**
**2. Request Rule Suggestions:**
```bash title="2. Request Rule Suggestions"
# 2. Request Rule Suggestions
cd genai_demo_no_logic
als genai-logic --suggest
```

You can review the [resultant logic suggestions](genai_demo_no_logic/docs/logic_suggestions) in the `genai_demo_no_logic` project:

 * See and edit: `docs/logic_suggestions/002_logic_suggestions.prompt` (used in step 3, below)
    * This corresponds to the Logic Editor - Logic View in the WebGenAI web app

**3. See the rules for the logic:**
**3. See the rules for the logic:**
**3. See the rules for the logic:**
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

**4. Create a new project with the Rule Suggestions:**
**4. Create a new project with the Rule Suggestions:**
**4. Create a new project with the Rule Suggestions:**
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

**0. Create Project Requiring Fixup:**
**0. Create Project Requiring Fixup:**
**0. Create Project Requiring Fixup:**
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
**1. Run FixUp to add missing attributes to the fixup response data model:**
**1. Run FixUp to add missing attributes to the fixup response data model:**
**1. Run FixUp to add missing attributes to the fixup response data model:**
```bash title="1. Run FixUp to add missing attributes to the fixup response data model"
# 1. Run FixUp to add missing attributes to the data model
cd genai_demo_fixup_required
als genai-utils --fixup
```

Finally, use the created [fixup files](genai_demo_fixup_required/docs/fixup/) to rebuild the project:
**2. Rebuild the project from the fixup response data model:**
**2. Rebuild the project from the fixup response data model:**
**2. Rebuild the project from the fixup response data model:**
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

**Iterate:**
**Iterate:**
**Iterate:**
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

<summary> 2. New Database - using Copilot (Signup optional) </summary>

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

![copilot](system/https://github.com/ApiLogicServer/Docs/blob/main/docs/images/copilot.png?raw=true)
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

<summary> 3. New Database - using ChatGPT in the Browser (Signup not required)</summary>

<br>A final option for GenAI is to use your Browser with ChatGPT.

Please see [this doc](https://apilogicserver.github.io/Docs/Sample-AI-ChatGPT/)

</details>

<br>

<br>

# Appendices

### Procedures

<details markdown>

<summary>Quick Basic Demo - Cheat Sheet</summary>

<br>This demo creates and customizes a project, starting from a database:

**Quick Basic Demo:**
**Quick Basic Demo:**
**Quick Basic Demo:**
```bash title="Quick Basic Demo"

# Microservice Automation
# Admin App, API, Project
als create --project-name=basic_demo --db-url=basic_demo

# Logic and Securityf
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
<br>

<details markdown>

<summary>Quick GenAI Demo - Cheat Sheet</summary>

<br>This demo creates and customizes a project, starting from a prompt:

**Quick GenAI Demo:**
**Quick GenAI Demo:**
**Quick GenAI Demo:**
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
<br>

<details markdown>

<summary> Detail Procedures</summary>

<br>Specific procedures for running the demo are here, so they do not interrupt the conceptual discussion above.

You can use either VSCode or Pycharm.


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

</details>

&nbsp;

### Setup Codespaces

Codespaces enables you to run in the cloud: VSCode via your Browser, courtesy GitHub.  

<details markdown>

<summary> Using codespaces on your GenAI project</summary>

__1. Open your project on GitHub__

![API Logic Server Intro](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/genai/open-github.png?raw=true)

__2. Open it in Codespaces (takes a minute or 2):__

![API Logic Server Intro](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/genai/start-codespaces.png?raw=true)

> You will now see your project - running in VSCode, _in the Browser._  But that's just what you _see..._

> Behind the scenes, Codespaces has requisitioned a cloud machine, and loaded your project - with a _complete development environment_ - Python, your dependencies, git, etc.  

> You are attached to this machine in your Browser, running VSCode.

> :trophy: Pretty remarkable.

__3. Start the Server and open the App in the Browser__

* Use the pre-defined Launch Configuration

![API Logic Server Intro](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/git-codespaces/start-codespaces.png?raw=true)


We think you'll find Codespaces pretty amazing - check it out!

</details>

&nbsp;

### Get an OpenAI ApiKey

<br>GenAI-Logic uses OpenAI, which requires an OpenAI Key:

1. Obtain one from [here](https://platform.openai.com/account/api-keys) or [here](https://platform.openai.com/api-keys)

2. Authorize payments [here](https://platform.openai.com/settings/organization/billing/overview)

</details>

&nbsp;

### Pre-created Samples

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
