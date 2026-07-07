<!--
title: Welcome - see end for instructions to hide this
Description: Instant mcp-enabled microservices, standard projects, declarative business logic
Source: docs/Manager-readme
version info: 17.00.12 (06/18/2026)
do_process_code_block_titles: True
Used: Manager Readme (via copy_md())
demo_customs: Customs-readme
demo_customs_surtax: Customs-readme-surtax
demo_kafka: Sample-Integration
demo_allo: Sample_Allo_Dept_GL_readme
demo_ai_rules: Sample-ai-rules
demo_mcp_send: Sample-Basic-Demo-MCP-Send-Email
demo_emp_types: Sample-Types
demo_eai: Sample-Basic-EAI
demo_vibe: Sample-Basic-Demo-Vibe
demo_copilot_mcp_discovery: Sample-ai-mcp
basic_demo: Sample-Basic-Demo
codespaces_patch: |
  create_codespaces_mgr.py injects a Codespaces-only browser note immediately after
  the "## 🚀 First Time Here?" heading (sentinel: do not rename that heading without
  updating the matching logic in create_codespaces_mgr.py). The note warns Safari users to
  switch to Chrome/Edge. This avoids forking the README for Codespaces.
-->
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>

# Welcome to GenAI-Logic

One prompt — or your existing database — builds a working API and Admin App, then you declare business logic in **5 readable rules instead of ~200 lines of AI-generated code** to enforce it.

You'll see that enforcement yourself in a few minutes: those rules run at **one commit point**, no matter which path the transaction came in on — API, MCP, agent, Kafka. **No bypass.**

And you're not alone: your AI assistant is your partner throughout. Ask it anything — architecture, rules, debugging, deployment, or how the system works.

This is the start page for the [GenAI-Logic Manager](https://apilogicserver.github.io/Docs/Manager) — where you manage projects, create notes and resources, etc.

&nbsp;

## 🤖 AI Assistance

<details markdown>
<summary>First select your AI assistant, then paste the prompt below</summary>

&nbsp;

We get consistently good results with **Claude Sonnet 4.6** (GitHub Copilot or Claude Code extension). "Ask" mode will not work — use **Agent mode**.

To select Sonnet 4.6 in the Copilot chat panel: click **Agent** → the **gear icon** → choose **Claude Sonnet 4.6**.

For more information, see [AI-Enabled Projects](https://apilogicserver.github.io/Docs/Project-AI-Enabled/) or [click here](https://apilogicserver.github.io/Docs/Manager-readme/).

</details>

&nbsp;

```
Please load `.github/.copilot-instructions.md`.
```

&nbsp;

## 🚀 First Time Here?
<!-- CODESPACES-INSERT-POINT: create_codespaces_mgr.py injects browser note here — do not rename this heading -->

<details>
<summary>⚡ Try Prompt → System — then ask: is this maintainable?</summary>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;1. Create — API, Admin App and business logic from a prompt (existing db)</summary>

<br>Say this to your AI assistant (allow 2-3 mins):

```
Create basic_demo from samples/dbs/basic_demo.sqlite (customers, orders, products).

Include a notes field for orders.

On Placing Orders, Check Credit    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped is not None.
```

<details markdown>
<summary>Starting from a new database instead?</summary>

&nbsp;

The prompt above starts from an existing database — the common real-world case, and much faster (no schema design step). You *could* have AI design a new database from scratch instead — drop the `from samples/dbs/basic_demo.sqlite` clause from the first line above (allow 8-10 mins).

</details>

&nbsp;

You've probably seen AI generate code before. The difference here: this produces *models*, not code — each artifact declares structure or policy rather than procedure, so there's no logic buried in the wiring:

1. **Data model** — `database/models.py`
2. **Full JSONAPI** — Swagger, pagination, optimistic locking (`api/expose_api_models.py` — 52 lines, zero per-table code)
3. **Admin App** — multi-table, with navigations and lookups (`ui/admin/admin.yaml`)
4. **Business logic** — `logic/logic_discovery/place_order/check_credit.py` *(more on this in step 5)*

Each small, readable, yours. Plain Python — standard tooling applies.

Security is opt-in, not default — bootstrap RBAC anytime with `genai-logic add-auth`.

</details>

<br>

<details markdown>
<summary>&emsp;&emsp;2. Run it — F5, then open the Admin App</summary>

<br>Press F5 using "API Logic Server Run (run project from manager)", and open the Admin App. Explore the API via Swagger, browse the data, and follow the relationships — all auto-generated from the data model.

</details>

<br>

<details markdown>
<summary>&emsp;&emsp;3. Trigger the logic</summary>

<br>In the Admin App, open an **unshipped** Order for Alice, edit the Widget item:

```
Change the quantity to a very large number. Save.
```

<details markdown>
<summary>&emsp;&emsp;&emsp;&emsp;Detail Instructions -- Screen Shots</summary>

<br>Alter the quantity for an *unshipped* item:

1. Show the Customer List
2. Show the first Customer
3. Show first Order
4. Edit the Item
5. Set the quantity

![credit-check](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/credit-check.png?raw=true?raw=true)

</details>

<br>

The save fails - note the dialog box. But, *why...?*

> Auditable, not just shown: [sample trace](samples/basic_demo_logic_gov/logs/als-sample.log) of this rule chain firing.

</details>

<br>

<details markdown>
<summary>&emsp;&emsp;4. Your AI assistant can explain the dialog</summary>

<br>

```
Eeks, why did that save fail?
```

Your AI explains the credit-limit rule and shows where it lives.

Notice: you didn't *place* an order, you *edited* one — and the rule still caught it. Hmm....

</details>

<br>

<details markdown>
<summary>&emsp;&emsp;5. Now let's see... what's really going on with the logic?</summary>

<br>Let's compare 2 approaches for implementing the check-credit requirement:

* Compare **standard AI-generated code** - open [procedural/credit_service.py](samples/basic_demo_logic_gov/logic/procedural/credit_service.py)

* With the **rule-based version** - open [logic_discovery/place_order/check_credit.py](samples/basic_demo_logic_gov/logic/logic_discovery/place_order/check_credit.py) - same requirement, same AI.  5 rules. No bugs.

Well, *that's* different... what's up with that? Ask your AI:

```
What are rules?
```

<details markdown>
<summary>&emsp;&emsp;&emsp;&emsp;No AI handy?</summary>

<br>Rules enforce business policy — multi-table derivations, constraints, and actions like messaging. **LogicBank**, the rule engine, hooks SQLAlchemy's commit event to run them on every transaction — authored as plain Python functions in `logic/logic_discovery/`, readable, version-controlled, owned like any other source file.

But unlike procedural code, they're **declarative**:

| Property | What it means | Why it matters |
|---|---|---|
| **Auto-reused** | `Customer.balance = sum of unpaid orders` — declared once, enforced over every change path | No per-path handlers to write or miss |
| **Auto-invoked** | Rules fire at every commit, from every caller — you never call them | Can't be forgotten, can't be bypassed |
| **Auto-ordered** | The engine computes dependency order at startup | Add a rule anywhere, it finds its place |

Think of a spreadsheet: `B10 = SUM(B1:B9)` isn't called, it *reacts* — change any input cell, it recalculates. Rules react the same way to changes in what they depend on — that's what makes 5 declarative rules replace ~200 lines of procedural code with zero missed paths, as you just saw above.

Full writeup: [declarative/procedural comparison](samples/basic_demo_logic_gov/logic/procedural/declarative-vs-procedural-comparison.md).

</details>

<br>

> But here's the part that matters beyond line count: with procedural code, even if you find the right passage — how do you know it's called for *every* transaction source? API, MCP, agent, Kafka, a future caller you haven't written yet? With thousands of code paths, you can't know. That's not a testing gap; it's a representation problem. <br><br>Rules solve it structurally — declared once, fired at one commit point, from every caller, with no bypass possible. The 40x reduction in code isn't the point. The verifiable coverage is: ***you can read the rules, and trust they are being enforced.  Always.***

<br>

</details>

<br>

<details markdown>
<summary>&emsp;&emsp;6. Iterate — ask for a new rule in plain English</summary>

<br>Try:
```
Customers should not be able to create new orders if they have unresolved past due letters.
```
Notice what just happened — two things, easy to miss:

**1. What the AI did.** There was no `Letter` (past-due notice) table in the model — the AI had to add the table and its relationship to `Customer`, then declare two rules: a `count` of unresolved letters, and a `constraint` blocking new orders when that count is non-zero. A schema change and two rules, from one sentence.

**2. The implications:**

- **You didn't do archaeology.** No opening `check_credit.py` to find where this belongs, no tracing the other 5 rules to check for conflicts. Auto-ordering means there's no maintenance hunt — you declare the rule, the engine places it.

- **AI-only would have to rebuild — and that cost scales with rule count.** Without the engine, an AI rewriting procedural code from scratch would have to re-read and re-touch all existing rules to check for dependencies — more surface area for a missed path, more tokens spent doing it. At 5 rules that's a nuisance; **at 500, the re-read is the bottleneck and the missed-path risk compounds.** Here, the engine resolves dependencies at load time, so adding this rule doesn't touch the rest — no regeneration, no regression risk, at any scale.

</details>

</details>

&nbsp;

<details markdown>
<summary>🚀 How does this lead to enterprise-class systems?</summary>

<br>

Quick recap: you created a system from prompt, ran it, triggered a rule, watched it chain across three tables, driven by 5 lines of code, then added a new one from one sentence — without touching the existing rules.

That's the second distinction from AI-generated code: the business logic is *rules*, not procedures. A procedure answers "what happens when X?" — so every new path needs a new procedure. A rule declares a fact about data — it's automatically re-used over every path, including ones that don't exist yet. Step 5 showed this working; step 6 showed it not breaking when you added one. That property is what scales.

How does this lead to enterprise-class systems?

**We add key *enterprise architecture* integration:**

- **Enterprise Integration (EAI)** — the demo above showed ***Publish** the Order to Kafka topic*. For the **subscribe** side, see [samples/basic_demo_eai/readme.md](samples/basic_demo_eai/readme.md): B2B orders from partner systems, via a Custom API or Kafka subscriber, including *lookups* so partners send `"Account": "Alice"` (not internal IDs).

- **MCP** — your API is **MCP-discoverable** out of the box (`/.well-known/mcp.json`).
Copilot, Claude, or ChatGPT can find the schema and answer natural-language queries against it.  There's no discovery layer for you to write — see [samples/basic_demo_ai_rules-supplier/readme_ai_mcp.md](samples/basic_demo_ai_rules-supplier/readme_ai_mcp.md)

- **AI Rules** — rules that call AI for genuinely judgment-call decisions (e.g. picking a supplier under disrupted shipping lanes).  Such AI "proposals" are governed by the deterministic rules to ensure results conform to business policy — see [samples/basic_demo_ai_rules-supplier/readme.md](samples/basic_demo_ai_rules-supplier/readme.md)

That combination — AI, logic automation, and that enterprise architecture — is what enables ***Executable Requirements***: AI building real enterprise-class systems, from formats you already are familiar with, not a new syntax to learn:

- **Gherkin-style scenarios** — [business description](samples/demo_customs_clvs/readme.md), and the [actual requirements](samples/demo_customs_clvs/docs/requirements/customs_demo/requirements.md) used by AI to create the system.

- The **short prompt that built a system straight from an actual government tariff regulation** (Canada, CBSA) — [the prompt](samples/demo_customs_surtax/readme.md), and [the rules it produced](samples/demo_customs_surtax/logic/logic_discovery/cbsa_steel_surtax.py)

    > So, simply by referencing the regs, you get a complete enterprise system — including governed logic you can audit, trust, and maintain.

&nbsp;

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/architecture/logic-architecture-exec.png?raw=true" alt="Design and Runtime funnels into one governed Rules Engine" height="380" width="380" align="right">

The architecture that makes this work: two funnels, converging on one engine. All requirement formats, and all transaction sources, passing through **the same commit point. No bypass.**

**What AI delivers, once logic is off its plate: entire, *governed* systems from requirements** — not just code that becomes instant tech debt. It is this approach that **caught an 8-figure compliance exposure** a major logistics company's hand-coded system missed for months. [Full writeup →](https://apilogicserver.github.io/Docs/Tech-Ent-AI)

</details>

&nbsp;

<details markdown>
<summary>🔧 An LLM trained on procedural code — how'd it end up writing rules, not code?</summary>

<br>

It didn't figure that out on its own. It was told to, in detail, by **Context Engineering** — the same files driving this conversation right now:

- **Directs rules, not code.** When you ask for business logic, CE steers the AI toward the *right* rule type (sum vs. count vs. Allocate vs. Request Pattern) for what you actually asked for, instead of letting it default to the procedural code it's seen a million times in training.

- **Trains the AI to automate everything above, and to help you when it breaks.** EAI's 2-message Kafka pattern, the AI/Request Pattern wiring, Executable Requirements' pre-coding schema assessment — all of it is documented training material (`docs/training/*`) the AI reads *before* writing your code, not generic knowledge it's guessing from. Ask "what are rules?" or "how do rules work?" — or, without an AI handy, just read [samples/basic_demo_logic_gov/logic/readme_logic.md](samples/basic_demo_logic_gov/logic/readme_logic.md) — same material.

  <details markdown>
  <summary>The AI was trained on this material — can you trust its answers?</summary>

  <br>Don't take them on faith. Ask the same question a different way, or ask something not covered here — like where this architecture breaks down. If it just recites the same lines back, you've caught it. If it reasons, that's the test passing.

  </details>

**The "can't be bypassed" claim, named:** rules aren't called from your code — they're wired into a single SQLAlchemy `before_flush` listener, installed once at server start. Every write, from any path — API, custom endpoint, Kafka consumer, agent — passes through that one listener before it commits. There's no second door.

This is why the same prompt produces a governed system, not a working-but-ungoverned demo. Details: [3-Legged Stool](https://apilogicserver.github.io/Docs/Customs-readme-full/#3-legged-stool).

**Have some questions before we get started?** Ask your AI assistant directly — it has the same materials we just walked through:

- Is this really infrastructure, like a database?
- Is this a black box? How do I debug a rule chain?
- What does it take to migrate off this if we ever wanted to?
- How does this perform at scale?
- What does this integrate with — APIs, workflows, agents, MCP?
- Does this work with my existing database?

More background: [Eval Guide](https://apilogicserver.github.io/Docs/Eval/).

</details>

&nbsp;

<details markdown>
<summary>🔑 Why not just let AI write the code?</summary>

<br>

Even if AI generates perfect procedural code — and it doesn't, reliably — you still have a governance problem.

5 declarative rules are readable. Auditable. The next developer can understand them, compliance can sign off on them, and when something goes wrong you can debug them. That's not a convenience — it's a requirement.

Our A/B test on a 3-table system measured this directly: 5 declarative rules vs. ~200 lines of AI-generated procedural code — a ~40X reduction. That reduction compounds: a larger system needs proportionally more procedural code to cover the same change paths, while the rule count grows with the requirements, not with the paths. Code nobody can read, verify, or safely change. Unreadable at scale is ungovernable at scale.

And there's a structural problem underneath: procedural code cannot represent transitive dependencies reliably. The AI diagnosed this itself — *"Business logic is not a coding problem. It's a dependency graph problem."* That's not a capability gap. No amount of AI capability fixes a representation problem.

You already saw the evidence for this above — [the two files side by side](samples/basic_demo_logic_gov/logic/procedural/credit_service.py). This is why that comparison exists.

The full case — with the A/B test, the governance argument, and the scalability problem — is at [Why GenAI-Logic](https://www.genai-logic.com/#h.yo3meupszav4).

</details>

&nbsp;

<details markdown>
<summary>🔨 Go deeper — 30-45 min guided tour</summary>

&nbsp;

**Create basic_demo** (auto-opens with guided tour option):
```bash
genai-logic create --project_name=basic_demo --db_url=sqlite:///samples/dbs/basic_demo.sqlite
```

**Inside the project:** Say to your AI assistant: *"Guide me through basic_demo"* (30-45 min hands-on tour).

> Teaches API creation, declarative rules, security, and Python customization. Fail-safe — scripts ensure no coding errors.

</details>

&nbsp;

&nbsp;

## 📚 Build It Yourself — Demo Catalog

The section above showed you pre-built samples to browse. These are the same use cases, but as commands you run yourself — paste one into your AI assistant and it builds that project for you, live.

> Tip: every project is AI-enabled — once it's built, ask your AI assistant how it works

&nbsp;

## 1. Strategic Use Cases (From [genai-logic.com](https://www.genai-logic.com))

Explore the key use cases from our home page:


| Use Case | Say to your AI / Run | What You'll Learn |
|----------|---------|-------------------|
| **[Allocation with AI Rules](samples/allocate_dept_account_demo/docs/requirements/logic_flow_allocate_dept_account_demo.md)** <br> demo_allo_dept_gl | create demo_allo_dept_gl from samples/prompts/allocation.prompt.md <br> or genai-logic create --project_name=demo_allo_dept_gl --db_url=sqlite:///samples/dbs/starter.sqlite | - [Cascade Allocation (Costs to Depts/GL)](https://apilogicserver.github.io/Docs/Sample_Allo_Dept_GL_full) <br> - AI Rules for fuzzy match to project |
| **[Use Case 1: AI Rules](samples/basic_demo_ai_rules-supplier/readme.md)**<br> demo_ai_rules_supplier | genai-logic create --project_name=demo_ai_rules_supplier --db_url=sqlite:///samples/dbs/basic_demo.sqlite | - Use AI Rules (req pattern) to choose Optimal Supplier, per world conditions |
| **[Use Case 2: Governed MCP Server](https://apilogicserver.github.io/Docs/Sample-Basic-Demo-MCP-Send-Email)** <br>demo_mcp_send_email | genai-logic create --project_name=demo_mcp_send_email --db_url=sqlite:///samples/dbs/basic_demo.sqlite | - Bus Users compose new service to send email to overdue customers, subject to email opt-out rules<br>- Create custom API with NL<br>- Create an email service (req pattern) |
| **[EAI: Enterprise App Integration](samples/basic_demo_eai/readme.md)** <br>demo_eai | genai-logic create --project_name=demo_eai --db_url=sqlite:///samples/dbs/basic_demo.sqlite | - Executable Requirements<br>- Create custom API with NL<br>- Create Kafka Listener with NL |
| **[Use Case 4: Vibe Dev Backend](https://apilogicserver.github.io/Docs/Sample-Basic-Demo-Vibe)** <br> demo_vibe | genai-logic create --project_name=demo_vibe --db_url=sqlite:///samples/dbs/basic_demo.sqlite | - UI elements, eg, Cards, Maps, Trees... |
| **[Use Case 5: Business Users](https://www.genai-logic.com/#h.69d2voz8q5r1)** <br> webgenai | See `webgenai/` in this Manager | - Create systems from browser, with logic, sample data and derived attributes |
| **[Customs CLVS](samples/requirements/customs_demo_clvs/docs/requirements/customs_demo/requirements.md)** <br> demo_customs_clvs | genai-logic create  --project_name=demo_customs_clvs --db_url=sqlite:///samples/requirements/customs_demo_clvs/database/customs.sqlite | - Governed Business Systems<br> - EAI (using XML), textual requirements |
| **[Customs Surtax](samples/prompts/customs_cbsa.prompt.md)** <br> demo_customs_surtax | implement project demo_customs_surtax from samples/prompts/customs_cbsa.prompt.md | - New Business System from Regulations |

&nbsp;

> **Running a cloned project?** F5 won't work until the venv is set up — see [Project-Env](https://apilogicserver.github.io/Docs/Project-Env/) for options (`genai-logic run`, symlink, or local venv).

&nbsp;

## 2. Additional Demos

Advanced examples and specialized patterns:

| Demo | Say to your AI / Run | What You'll Learn |
|------|---------|-------------------|
| **Executable Requirements** | See [samples/requirements/readme_reqmts.md](samples/requirements/readme_reqmts.md) | Create from Gherkin requirements <br>implement reqs <path> |
| **New system from prompt** | genai-logic genai --using=samples/prompts/genai_demo.prompt | Create systems from prompt<br>Like WebGenAI, but from IDE |
| **Coding Samples** | code samples/nw_sample | Useful code examples<br>Search: `#als` |
| **MCP Discovery** <br> demo_copilot_mcp_discovery | genai-logic create --project_name=demo_copilot_mcp_discovery --db_url=sqlite:///samples/dbs/basic_demo.sqlite | test rules via Copilot access to MCP Server | 


**Copy Snippets for venv:**
```bash title="Copy Snippets for venv"
source venv/bin/activate       # windows: venv\Scripts\activate
source ../venv/bin/activate    # windows: ../venv\Scripts\activate
python -m venv venv            # may require python3 -m venv venv
```

&nbsp;


# Appendices

## GenAI CLI (requires an OpenAI key)

Everything above — the walkthrough, the samples, Demo Catalog — runs through your AI assistant (Copilot/Claude), no separate signup. The `genai-logic genai` CLI commands below predate that: they call OpenAI's API directly, which means you need your own OpenAI account and key (see *Get an OpenAI Key*, below) and pay for usage.

That's real friction most readers don't need to take on — the AI-assistant path covers the same ground. This section is kept for completeness: scripted/CI use, or specific model-iteration workflows the AI-assistant path doesn't (yet) replicate.

<br>

<details markdown>

<summary>1. New Database - using GenAI Microservice Automation (Experiment with AI - Signup optional)</summary>

<br>You can do this with or without signup:

1. If you have signed up (see *Get an OpenAI Key*, below), this will create a new database and project called `genai_demo`, and open the project.  It's created using `genai_demo.prompt`, visible in left Explorer pane:

```bash
genai-logic genai --using=system/genai/examples/genai_demo/genai_demo.prompt --project-name=genai_demo
```


2. ***Or,*** you can simulate the process (no signup) using:


```bash
genai-logic genai --repaired-response=system/genai/examples/genai_demo/genai_demo.response_example --project-name=genai_demo
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

1. You create your.prompt file, and invoke `genai-logic genai --using=your.prompt`.  genai then creates your project as follows:

    a. Submits your prompt to the `ChatGPT API`

    b. Writes the response to file, so you can correct and retry if anything goes wrong

    c. Extracts model.py from the response

    d. Invokes `genai-logic create-from-model`, which creates the database and your project

2. Your created project is opened in your IDE, ready to execute and customize.  

    a. Review `Tutorial`, Explore Customizations.

![GenAI Automation](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/genai.png?raw=true)

</details>
</br>

<details markdown>

<summary> You can iterate the logic and data model</summary>

<br>The approach for an iteration is to create a new project from an existing one:

1. add another prompt to an existing projects `docs` directory, specifying your changes
2. use `genai-logic genai`, specifying 
    * `--using` existing projects `docs` directory, and 
    * `--project-name` as the output project
 
 **Logic iterations** are particularly useful.  For example, here we take the basic check-credit logic, and add:

> Provide a 10% discount when buying more than 10 carbon neutral products.<br><br>The Item carbon neutral is copied from the Product carbon neutral

Explore [genai_demo_iteration_discount](system/genai/examples/genai_demo/genai_demo_iteration_discount).  It's an iteration of basic_demo (see system/genai/examples/genai_demo/genai_demo_iteration_discount/002_create_db_models.prompt).  This will add carbon_neutral to the data model, and update the logic to provide the discount:

**Iterate Business Logic:**
```bash title='Iterate Business Logic'
# Iterate with data model and logic
genai-logic genai --project-name='genai_demo_with_discount' --using=system/genai/examples/genai_demo/genai_demo_iteration_discount
# open Docs/db.dbml
```

<br>

You can perform **model iterations:** add new columns/tables, while keeping the prior model intact.  First, we create a project with no logic, perhaps just to see the screens (this step is optional, provided just to illustrate that iterations create new projects from existing ones):

**Iterate Without Logic:**
```bash title='Iterate Without Logic'
# Step 1 - create without logic
genai-logic genai --project-name='genai_demo_no_logic' --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt
# open Docs/db.dbml
```

Then, we would create another prompt in the docs directory with our model changes. We've already created these for you in `system/genai/examples/genai_demo/genai_demo_iteration` - we use that to alter the data model (see `system/genai/examples/genai_demo/genai_demo_iteration/004_iteration_renames_logic.prompt`):

**Iterate With Logic:**
```bash title='Iterate With Logic'
# Iterate with data model and logic
genai-logic genai --project-name='genai_demo_with_logic' --using=system/genai/examples/genai_demo/genai_demo_iteration
# open Docs/db.dbml
```

Explore [genai_demo_iteration](system/genai/examples/genai_demo/genai_demo_iteration) - observe the `--using` is a *directory* of prompts.  These include the prompts from the first example, plus an *iteration prompt* (`004_iteration_renames_logic.prompt`) to rename tables and add logic.


</details>
</br>

<details markdown>

<summary> You can declare informal logic</summary>

<br>You can declare rules using dot notation, or more informally:

**Informal Logic (no dot notation):**
```bash title="Informal Logic (no dot notation)"
genai-logic genai --using=system/genai/examples/genai_demo/genai_demo_informal.prompt --project-name=genai_demo_informal
```
</details>
</br>


<details markdown>

<summary> Multi-Rule Logic</summary>

<br>You can add new columns/tables, while keeping the prior model intact:

**Multi-Rule Logic:**
```bash title="Multi-Rule Logic"
genai-logic genai --using=system/genai/examples/emp_depts/emp_dept.prompt
```
</details>
</br>

<details markdown>

<summary> You can ask AI to suggest logic (great way to learn!)</summary>

<br>You can create a project, and ask GenAI for logic suggestions:

**1. Create Project, without Rules:**
```bash title='1. Create Project, without Rules'
# 1. Create Project, without Rules
genai-logic genai --project-name='genai_demo_no_logic' --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt
```

**2. Request Rule Suggestions:**
```bash title="2. Request Rule Suggestions"
# 2. Request Rule Suggestions
cd genai_demo_no_logic
genai-logic genai-logic --suggest
```

You can review the [resultant logic suggestions](genai_demo_no_logic/docs/logic_suggestions) in the `genai_demo_no_logic` project:

 * See and edit: `docs/logic_suggestions/002_logic_suggestions.prompt` (used in step 3, below)
    * This corresponds to the Logic Editor - Logic View in the WebGenAI web app

**3. See the rules for the logic:**
```bash title="3. See the rules for the logic"
# 3. See the rule code for the logic
genai-logic genai-logic --suggest --logic='*'
```

Important notes about suggestions and generated code:
* `--suggest --logic='*'` is intended to enable you to identify logic that does not translate into proper code
* The example above was pretty good, but sometimes the results are downright silly:
    * Just run suggest again, or
    * Repair `docs/logic_suggestions/002_logic_suggestions.prompt`

Also...
* It is not advised to paste the code into `logic/declare_logic.py`
    * The suggested logic may result in new data model attributes
    * These are created automatically by running `genai-logic genai` (next step)

The [logic suggestions directory](genai_demo_no_logic/docs/logic_suggestions) now contains the prompts to create a new project with the suggested logic.  
When you are ready to proceed:
1. Execute the following to create a *new project* (iteration), with suggested logic:

**4. Create a new project with the Rule Suggestions:**
```bash title="4. Create a new project with the Rule Suggestions"
# 4. Create a new project with the Rule Suggestions
cd ..  # important - back to manager root dir
genai-logic genai --project-name='genai_demo_with_logic' --using=genai_demo_no_logic/docs/logic_suggestions
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
```bash title="0. Create Project Requiring Fixup"
# 0. Create a project requiring fixup
genai-logic genai --repaired-response=system/genai/examples/genai_demo/genai_demo_fixup_required.json --project-name=genai_demo_fixup_required
```

If you run this project, you will observe that it fails with:
```bash
Logic Bank Activation Error -- see https://apilogicserver.github.io/Docs/WebGenAI-CLI/#recovery-options
Invalid Rules:  [AttributeError("type object 'Customer' has no attribute 'balance'")]
Missing Attrs (try genai-logic genai-utils --fixup): ['Customer.balance: constraint']
```
&nbsp;

***Fixup***

To Fix it:
**1. Run FixUp to add missing attributes to the fixup response data model:**
```bash title="1. Run FixUp to add missing attributes to the fixup response data model"
# 1. Run FixUp to add missing attributes to the data model
cd genai_demo_fixup_required
genai-logic genai-utils --fixup
```

Finally, use the created [fixup files](genai_demo_fixup_required/docs/fixup/) to rebuild the project:
**2. Rebuild the project from the fixup response data model:**
```bash title="2. Rebuild the project from the fixup response data model"
# 2. Rebuild the project from the fixup response data model
cd ../
genai-logic genai --repaired-response=genai_demo_fixup_required/docs/fixup/response_fixup.json --project-name=fixed_project
```
    
&nbsp;
The created project may still report some attributes as missing.  
(ChatGPT seems to often miss attributes mentioned in sum/count where clauses.)  To fix:

1. Note the missing attributes(s) from the log
2. Add them to `docs/003_suggest.prompt`
3. Rebuild the project: `genai-logic genai --project-name='genai_demo_with_logic' --using=genai_demo_no_logic/docs`


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
genai-logic genai-utils --import-genai --using=../wg_demo_no_logic_fixed
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
genai-logic genai --using=system/genai/examples/genai_demo/genai_demo.prompt --project-name=genai_demo
```
2. Rebuild:
```
cd genai_demo
genai-logic genai-utils --rebuild-test-data
```

</details>
</br>

<details markdown>

<summary> You can also execute directly, and iterate</summary>

<br>You can add new columns/tables, while keeping the prior model intact:

**Iterate:**
```bash title="Iterate"
# create project without creating a file...
genai-logic genai-create --project-name='customer_orders' --using='customer orders'

genai-logic genai-iterate --using='add Order Details and Products'
# open Docs/db.dbml
```

</details>
</br>

<details markdown>

<summary> AI sometimes fails - here's how to recover</summary>

<br>AI results are not consistent, so the model file may need corrections.  You can find it at `system/genai/temp/model.py`.  You can correct the model file, and then run:

```bash
genai-logic create --project-name=genai_demo --from-model=system/genai/temp/create_db_models.py --db-url=sqlite
```

Or, correct the chatgpt response, and

```bash
genai-logic genai --repaired-response=system/genai/examples/genai_demo/genai_demo.response_example --project-name=genai_demo
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
genai-logic genai --using=system/genai/examples/postgres/genai_demo_pg.prompt --db-url=postgresql://postgres:p@localhost/genai_demo
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

![copilot](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/copilot.png?raw=true)
</details>

<br>

2. Paste the copilot response into a new `sample_ai.py` file

3. Create your project:

```bash
genai-logic create --project-name=sample_ai --from-model=sample_ai.py --db-url=sqlite
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

## Procedures

<br>

<details markdown>

<summary> Detail Procedures</summary>

<br>Specific procedures for running the demo are here, so they do not interrupt the conceptual discussion above.

You can use either VSCode or Pycharm.


**1. Establish your Virtual Environment**

Python employs a virtual environment for project-specific dependencies.

**If the project was created in this Manager** (or opened from it), the venv is already configured — just press F5.

**If the project was cloned from git**, choose one of:

* **Quickest (no VS Code setup):** from the Manager terminal (or, use Code Assistant):
    ```bash
    genai-logic run --project-name=<project-name>
    ```

* **Mac/Linux with F5:** create a symlink to the Manager venv:
    ```bash
    cd <project>
    sh venv_setup/venv.sh symlink
    # reload VS Code window, then F5
    ```

* **Any platform:** create a local venv:
    ```bash
    sh venv_setup/venv.sh go        # mac/linux
    .\venv_setup\venv.ps1 go        # windows
    ```

For PyCharm, you will get a dialog requesting to create the `venv`; say yes.

See [Project-Env](https://apilogicserver.github.io/Docs/Project-Env/) for more information.

&nbsp;

**2. Start and Stop the Server**

Both IDEs provide Run Configurations to start programs.  These are pre-built by `ApiLogicServer create`.

For VSCode, start the Server with F5, Stop with Shift-F5 or the red stop button.

For PyCharm, start the server with CTL-D, Stop with red stop button.

&nbsp;

**3. Entering a new Order**

To enter a new Order:

1. Click `Customer 1`

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

> You'll see your project running in VSCode, in the browser. Behind the scenes, Codespaces requisitioned a cloud machine and loaded your project with a complete development environment — Python, dependencies, git — and attached your browser to it.

__3. Start the Server and open the App in the Browser__

* Use the pre-defined Launch Configuration

![API Logic Server Intro](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/git-codespaces/start-codespaces.png?raw=true)

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

&nbsp;

### Hiding Front Matter

<details markdown>

<summary>Hiding Front Matter </summary>

To hide the YAML or JSON front matter (the metadata block at the top of your markdown files) in the built-in VS Code markdown preview, you can adjust your editor settings:

1. Open the Settings panel using Ctrl + , (Windows/Linux) or Cmd + , (macOS).
2. Search for the following term: `markdown.previewFrontMatter`.
3. Change the dropdown value from show to `hide`.

The preview will now automatically strip the front matter from the rendered view.

![hide-front-matter](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/manager/hide-front-matter.png?raw=true)

</details>