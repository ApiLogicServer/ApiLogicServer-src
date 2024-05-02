Welcome the the [API Logic Server Manager](https://apilogicserver.github.io/Docs/Manager/).  This is a good place to manage projects, create notes and resources, etc.

We always recommend creating the [Tutorial](https://apilogicserver.github.io/Docs/Tutorial/) - handy reference for code and logic examples.  

1. Open a terminal window (**Terminal > New Terminal**), and paste the following CLI command:

```bash
ApiLogicServer create --project-name= --db-url=
```

&nbsp;

>  Next, create projects by clicking one of the disclure buttons, below:

<br>

<details markdown>

<summary> Existing Database - pre-installed demo </summary>

<br>To create a project, **press F5**, or use the CLI (**Terminal > New Terminal**) and try the pre-installed [**Demo**](https://apilogicserver.github.io/Docs/Sample-AI/) (original created from AI using Copilot):

```
als create --project-name=sample_ai --db-url=sqlite:///sample_ai.sqlite
```

Then, try your own databases [(db-url examples here)](https://apilogicserver.github.io/Docs/Database-Connectivity/), or experiment with [these Docker databases](https://apilogicserver.github.io/Docs/Database-Docker/).

</details>

&nbsp;

<details markdown>

<summary> New Database - using GenAI Automation (Signup optional)</summary>

<br>This will create and open a project called `genai_demo` from `genai_demo.prompt`:

```bash
als genai --using=genai_demo.prompt
```

This command calls the ChatGPT API to generate the model, which is then automatically submitted to `als create from-model`.  At this point, you should be able to open the project, and run it.

<details markdown>

<summary> AI somtimes fails - here's how to recover</summary>

<br>AI results are not consistent, so the model file may need corrections.  You can find it at `system/genai/temp/model.py`.  You can correct the model file, and then run:

```bash
als create --project-name=genai_demo --from-model=system/genai/temp/model.py --db-url=sqlite
```

Or, correct the chatgpt response, and

```bash
als genai --using=genai_demo.prompt --gen-using-file=system/genai/temp/chatgpt_retry.txt
```

We have seen failures such as:

* duplicate definition of `DECIMAL`
* use of `Decimal` vs. `DECIMAL` (latter required, work-around in place)
* unclosed parentheses
* data type errors in test data creation
* wrong engine import: from logic_bank import Engine, constraint
* bogus test data creation: with Engine() as engine...
* Numeric --> String (fixed product bug)
* Bad load code (no session)

</details>

&nbsp;

** Postgresql Example**

Works, with provisos:

* You have to create the database first, but perhaps we can do that: https://stackoverflow.com/questions/76294523/why-cant-create-database-if-not-exists-using-sqlalchemy

</details>

&nbsp;

<details markdown>

<summary> New Database - using Copilot (Signup required) </summary>

<br>You can use Copilot chat (if extension installed):

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

&nbsp;

<details markdown>

<summary> New Database - using ChatGPT in the Browser </summary>

<br>ChatGPT in the Browser

Please see [this doc](https://apilogicserver.github.io/Docs/Sample-AI-ChatGPT/)

</details>
