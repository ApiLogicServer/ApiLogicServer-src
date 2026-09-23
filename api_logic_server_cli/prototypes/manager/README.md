<!--
title: Welcome - see end for instructions to hide this
Description: Instant mcp-enabled microservices, standard projects, declarative business logic
Source: docs/Manager-readme
version info: 17.03.08 (07/22/2026)
do_process_code_block_titles: True
Used: Manager Readme (via copy_md())
demo_customs_clvs: Customs-clvs-readme
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

GenAI-Logic turns your requirements into enterprise-class database transaction systems, **governed** by **no-bypass rules**.

It reads whatever form your requirements are already in — **plain English, Gherkin, actual regulation text** — or, you can request an **interview** to discover the requirements.

And it **fits what you already use**: your methodology, standard tools, and shared artifacts, **fostering collaboration** between Business Users and Developers.

This is the start page for the [GenAI-Logic Manager](https://apilogicserver.github.io/Docs/Manager) — where you manage projects, create notes and resources, etc.  It's also your learnng hub.
<!-- CODESPACES-ONLY-START
(see [codespaces setup here](system/ApiLogicServer-Internal-Dev/setup.gif))
CODESPACES-ONLY-END -->

<details markdown>
<summary><strong>Say "hi" to your coding assistant</strong> — click to see important notes on models</summary>

<br>Using a lighter or auto-selected model? Fine for exploring — for real logic you intend to keep, pick a frontier model (Claude Sonnet 5, GPT-5, etc.) if your plan allows it, and review the AI's output either way, the same as you would any other engineer's.

*Why this matters: [AI-Enabled Projects](https://apilogicserver.github.io/Docs/Project-AI-Enabled/).*

</details>

&nbsp;

## 🚀 First Time Here?
<!-- CODESPACES-INSERT-POINT: create_codespaces_mgr.py injects browser note here — do not rename this heading -->

<details markdown>
<summary>The Ideal — executable business prompts, held to an enterprise standard</summary>

<br>Governance — logic that's readable, enforced without bypass, and auditable — isn't a developer nicety; it's a standing CIO concern for any AI-built system. Watch for it below: the same commit that fails in a moment is that property, live.

<!-- LOCAL-MGR-ONLY-START -->
> **Heads up:** you're about to switch to the AI chat panel, and back. VS Code's preview forgets which sections below are open/closed when you return — so **drag this preview tab's icon out into its own window** first (once), and it won't happen again.
<!-- LOCAL-MGR-ONLY-END -->
<!-- CODESPACES-ONLY-START
> **Heads up:** you're about to switch to the AI chat panel, and back. The browser tab showing this README forgets which sections below are open/closed when you return — so **open the README on GitHub** ([ApiLogicServer/codespaces_mgr](https://github.com/ApiLogicServer/codespaces_mgr)) **in a split-view tab** first (once), and it won't happen again.

<details markdown>
<summary>&emsp;&emsp;Show me how</summary>

<br>Right-click the GitHub README tab and choose **New Split View with Current Tab**:

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/git-codespaces/StartSplitView.png?raw=true" alt="Open the README from GitHub, right-click the tab, choose New Split View with Current Tab" width="700">

You'll end up with the Codespace on one side and the README on the other — switch between AI chat and README without losing your place:

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/git-codespaces/SplitView.png?raw=true" alt="Codespace and README side by side in split view" width="700">

</details>
CODESPACES-ONLY-END -->

<br>Say this to your AI assistant (allow several minutes):

```
Create basic_demo from samples/dbs/basic_demo.sqlite.

On Placing Orders, Check Credit:    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped is not None.
```

<!-- CODESPACES-ONLY-START
> **In a hurry, or want zero AI/model dependency?** Skip the wait — copy the finished result instead:
> ```bash
> cp -r samples/basic_demo_existing_db basic_demo
> ```
> Same prompt, same logic, same rules — [check_credit.py](samples/basic_demo_existing_db/logic/logic_discovery/place_order/check_credit.py) is real, already there. Press F5 and you're looking at a working, governed project in seconds, no AI call required.
CODESPACES-ONLY-END -->

<details markdown>
<summary>Starting from a new database instead?</summary>

The prompt above starts from an existing database — the common real-world case, and much faster (no schema design step). You *could* have AI design a new database from scratch instead:

<br>Say this to your AI assistant (allow several minutes):

```
Create basic_demo from samples/prompts/genai_demo.prompt
```

</details>

&nbsp;

<!-- CODESPACES-ONLY-START
> **During project creation, a browser tab may auto-open (or offer to)** showing it running — safe to decline or dismiss.
CODESPACES-ONLY-END -->

**See it running:** Press F5 using "API Logic Server Run (run project from manager)", and open the Admin App. Explore the API via Swagger, browse the data, and follow the relationships — all auto-generated from the data model.

Now trigger it: open an **unshipped** Order for Alice, edit the Widget item:

```
Change the quantity to a very large number. Save.
```

<details markdown>
<summary>&emsp;&emsp;Detail Instructions -- Screen Shots</summary>

<br>Alter the quantity for an *unshipped* item:

1. Show the Customer List
2. Show the first Customer
3. Show first Order
4. Edit the Item
5. Set the quantity

![credit-check](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/credit-check.png?raw=true)

</details>

<br>

The save fails — note the dialog. That's 5 rules — not ~200 lines of code — governing this transaction across four tables. **Not what you'd get if you'd asked AI alone.** Let's explore.

</details>

&nbsp;

<details markdown>
<summary>AI Alone Writes Code You Can't Read or Trust — Here's the Evidence</summary>

<br>AI is genuinely good at UI, data mapping, boilerplate, etc — no argument there. **Business logic is the exception.**

Left unguided, any AI assistant — including the one that just built basic_demo for you — would default to procedural code for logic like this. Ask it directly, and you get three problems:

<details markdown>
<summary>&emsp;&emsp;<strong>Not readable</strong> — unreadable at scale is ungovernable at scale</summary>

<br>[procedural/credit_service.py](samples/basic_demo_logic_gov/logic/procedural/credit_service.py) — ~200 lines for those same 5 requirements. Open it and judge for yourself. Now picture a real system: 10-20X the requirements of this example, and proportionally more procedural code to match. Nobody can audit that at a glance — not the next developer, not compliance, not you in six months. At that scale, an auditor can't read it all — they can only sample, and hope.

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>Not trustworthy (1)</strong> — the procedural version shipped 2 real bugs</summary>

<br>Found only by specifically testing what happens when a row is reparented to a new owner: [the A/B test](samples/basic_demo_logic_gov/logic/procedural/declarative-vs-procedural-comparison.md). Root cause: **path confusion** — procedural code must enumerate every change path (insert, update, delete, reparent) by hand, and it's easy to miss one.

There's a structural problem underneath the bugs, too: **AI pattern-matches dependencies, it doesn't compute them** — so the odds of a miss go up as the system grows. [More detail →](samples/basic_demo_logic_gov/logic/procedural/declarative-vs-procedural-comparison.md#the-underlying-problem-dependency-graphs)

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>Not trustworthy (2)</strong> — a typical spec produced logic for one path only</summary>

<br>We gave two frontier models a typical requirement — check credit on placing an order, phrased the way a developer naturally writes it — with no ApiLogicServer, and told them explicitly not to use rules. Both produced the same shape of code: one function, wired to order creation. No update path. No delete path.

Probed directly: change an item's quantity, delete an item, reassign an order to a different customer, reassign an item to a different product. Every case, both models, left stale data behind. No error. Nothing to catch it. The logic wasn't buggy so much as absent — it existed for exactly one path and nowhere else. [Full experiment →](https://apilogicserver.github.io/Docs/Tech-Standard-Reqs)

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>Not maintainable</strong> — the cost doesn't scale with the fix</summary>

<br>Hand-editing 200 generated lines isn't a real option — nobody reliably patches the output of a code generator, any more than you'd hand-patch a compiler's output. That leaves one path: **change the prompt and regenerate.**

But that doesn't dodge the risk, it repeats it — the AI re-derives everything from scratch, with no guarantee it reproduces the paths that already worked. Adding one small constraint — a one-line change — means regenerating and re-reviewing the whole system, every time, at every table. On a real system that's not a quick edit. It's hours, real AI cost, and a fresh chance at a new bug — to make a change that should have taken a minute.

</details>

&nbsp;

That's not (only) a capability gap — it's a representation problem: procedural code doesn't carry an explicit dependency graph, so nothing short of building one — inside the AI's process or outside it — closes this gap. A rules engine builds that graph explicitly, once, and checks it. That's the difference this document shows.

**We're deeply impressed with AI — this is about closing the one gap it has: logic.** That's next.

</details>

&nbsp;

<details markdown>
<summary>Governed Systems You Can Read, Trust, and Maintain — Augment AI with Rules</summary>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>1. What you just ran</strong> — see why it's different</summary>

<br>You've probably used AI to generate code before — so what's different here?

**Difference 1: it produces executable models, not code.** You just ran that project. Instead of a pile of procedural code, you got artifacts that declare structure or policy rather than procedure — same 5 requirements, same AI:

1. **Data model** — `database/models.py`
2. **Full JSON:API** — Swagger, pagination, optimistic locking (`api/expose_api_models.py` — 52 lines, zero per-table code)
3. **Admin App** — multi-table, with navigations and lookups (`ui/admin/admin.yaml` — simple YAML, not HTML/JS)
4. **Business logic** — [logic_discovery/place_order/check_credit.py](samples/basic_demo_logic_gov/logic/logic_discovery/place_order/check_credit.py) — 5 rules (~40X less), same requirements, same AI, 0 bugs

**Difference 2: the logic itself is declarative.** 5 lines, intent still clear — not ~200 lines of procedural frankencode. That's what declarative buys — more on that below.

Each small, readable, yours. Plain Python — standard tooling applies. Security is opt-in, not default — bootstrap RBAC anytime with `genai-logic add-auth`.

The save you just saw fail was enforced by exactly one of those 5 rules. Let's look at why that's not what you'd get from AI alone.

![Governance by Architecture, Not Discipline](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/architecture/gov-by-arch.png?raw=true)

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>2. Debug it</strong> — standard logging, standard debugger</summary>

<br>No new tools required. The rule chain that just fired is in the log — plain text, readable in your terminal or editor: [sample trace](samples/basic_demo_logic_gov/logs/als-sample.log). A live run writes the same thing to the standard log, `logs/als.log`.

Every rule is a plain Python function or lambda. Set a breakpoint on any `calling=` function or `as_condition=` lambda in your IDE, exactly like you would anywhere else in the codebase — no proprietary debugger, no special UI.

![logic-debug](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/logic/logic-debug.png?raw=true)

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>3. Iterate</strong> — 1 AI prompt adds table, relationship, 2 rules</summary>

<br>Ask your AI assistant for a new rule, in plain English:

```
Customers should not be able to create new orders if they have unresolved past due letters.
```

There was no `Letter` table in the model — the AI adds it, relates it to `Customer`, and declares a `count` + a `constraint`. One sentence creates a schema change and two new rules — automatically integrated with the 5 already there. No need to open `check_credit.py` to find where this belongs, or trace the other rules to check for conflicts.

**A lot just happened here — worth a closer look.**

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>4. Why Rules Are Declarative</strong> — automatic calling, automatic ordering</summary>

<br>This iteration — like maintenance generally — was remarkably simple, because **rules are declarative:**

- **No need to call the new logic.** Rules are invoked automatically - regardless of the originating path.  You can **trust** that they'll always run.
- **Order doesn't matter.** Open `check_credit.py` and shuffle the five rules into any order you like. Rerun — still correct. Try that with 200 lines of procedural code.  You can **trust** that they'll run in the right order.
- **You got more than you asked for.** The original requirement said *"On Placing Orders, Check Credit"* — insert time. But the save that failed was an *edit* to an existing order. Nobody wrote an update-time check.

Functions don't behave like that. So why is that?

> **Traditional logic is procedural** — you own *how*: when it's called, and in what order. **Declarative logic — rules** — is about *what*, not how: you state the fact, and the system takes responsibility for invocation and ordering. That's why the new rule didn't need to be called, and why order didn't matter.

The next section explores this in detail. Ask your AI assistant — *"What are rules?"* — or keep reading.

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>5. How Declarative Rules Make Logic Easy to Read, Trust, and Maintain</strong></summary>

<br>**Rules** enforce business policy — multi-table derivations, constraints, and actions like messaging. **LogicBank**, the rule engine, hooks SQLAlchemy's commit event to run them on every transaction — authored as plain Python functions in `logic/logic_discovery/`, readable, version-controlled, owned like any other source file.

**How it works:**
1. **At startup** — rules load, and the engine computes their dependency graph once.
2. **At commit** — for each transaction, the engine finds the rules relevant to what changed, and fires them in the right order.

Unlike procedural code, they're **declarative** — solving exactly the three problems raised above (AI great, but hard to Read, Trust, and Maintain):

| Property | What it means | Why it matters |
|---|---|---|
| **Readable** | 5 lines, one per requirement — declared once, e.g. `Customer.balance = sum of unpaid orders` | No archaeology needed to see what it does |
| **Trustworthy** | Rules fire at every commit, from every caller, on every insert *and* edit — you never call them | Can't be forgotten, can't be bypassed |
| **Maintainable** | Dependency order is computed once, automatically — not written into your source file | Add a rule anywhere, it finds its place |

> Think of a **spreadsheet:** `B10 = SUM(B1:B9)` isn't called, it *reacts* — change any input cell, it recalculates. Rules react the same way to changes in what they depend on.

Procedural code is hard to read — so you can't tell whether it's called from every caller, in the right order. That's not a testing gap; it's a representation problem.

> Declarative rules are easy to read — the intent, now rigorous — and with no bypass and automatic ordering.
>
> ***You can read the rules, and trust they are being enforced. Always.***

Full writeup: [declarative/procedural comparison](samples/basic_demo_logic_gov/logic/procedural/declarative-vs-procedural-comparison.md).

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>How this works: Context Engineering (CE) + a commit-time rules engine</strong></summary>

<br>Two things have to be true for this to work:

**Step 1 — Context Engineering trains the AI to write rules, not code.** That same AI, left unguided, would have produced the ~200 buggy lines from earlier. Writing rules instead wasn't its own idea — it was told to, in detail, by **Context Engineering** — the same files driving this conversation right now. When you ask for business logic, CE steers the AI toward the *right* rule type (sum vs. count vs. Allocate vs. Request Pattern) for what you actually asked for, instead of letting it default to the procedural code it's seen a million times in training — making rules the default, easy path, not a discipline a team has to maintain by hand.

**Step 2 — the rules engine runs the rules.** Rules aren't called from your code — they're wired into a single SQLAlchemy `before_flush` listener, loaded once at server start as described above. Every write, from any path — API, custom endpoint, Kafka consumer, agent — passes through that one listener before it commits. No bypass — there's no second door.

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>Governance reports</strong> — logic flow, AI alerts, health check</summary>

<br>Rules you can read is only half of it — the AI is also proactive about what it wants *you* to double-check. Three reports, generated from the running system, not hand-written:

- **[Logic flow diagram](samples/basic_demo_logic_gov/docs/requirements/logic_flow_basic_demo_logic_gov.md)** — NL requirement, dependency diagram, and rule summary, for every rule chain
- **[AI alerts](samples/basic_demo_logic_gov/docs/requirements/ad-libs.md)** — every assumption the AI made beyond the spec, flagged for you to verify, not buried
- **[Health check](samples/basic_demo_logic_gov/docs/requirements/health_check.md)** — rule adoption, dependency-tracking integrity, missing docstrings, across the whole project

A compliance reviewer can check the implementation in minutes, not by reading code. Here's that report for the basic_demo rules you just ran — the same report generates for any project, including the enterprise-scale ones below:

<img src="samples/basic_demo_logic_gov/docs/requirements/logic_diagrams/logic_diagram.svg" alt="Logic diagram: Item/Order/Customer rule chain, generated from the running rules" width="480">

</details>

</details>

</details>

&nbsp;

<details markdown>
<summary>Pre-Built Enterprise Architecture — API, MCP, Messages, Rules, RBAC (via Context Engineering)</summary>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>It's enterprise-aware, not just logic-aware</strong> — EAI, MCP, AI Rules, RBAC, Custom UIs</summary>

<br>Context Engineering's system knowledge isn't limited to rules — it already knows the integration points a real enterprise system needs, the same way it already knows a lookup wants an integer foreign key. [More on system vs. domain knowledge →](https://apilogicserver.github.io/Docs/Tech-AI-First/#two-kinds-of-knowledge-conflated)

- **Enterprise Integration (EAI)** — the demo above showed ***Publish** the Order to Kafka topic*. For the **subscribe** side, see [samples/basic_demo_eai/readme.md](samples/basic_demo_eai/readme.md): B2B orders from partner systems, via a Custom API or Kafka subscriber, including *lookups* so partners send `"Account": "Alice"` (not internal IDs).

<br>

- **MCP** (Model Context Protocol) — your API is **MCP-discoverable** out of the box (`/.well-known/mcp.json`). Copilot, Claude, or ChatGPT can find the schema and answer natural-language queries against it. There's no discovery layer for you to write — see [samples/basic_demo_ai_rules-supplier/readme_ai_mcp.md](samples/basic_demo_ai_rules-supplier/readme_ai_mcp.md)

<br>

- **AI Rules** — rules that call AI for genuinely judgment-call decisions (e.g. picking a supplier under disrupted shipping lanes). Such AI "proposals" are **governed by the deterministic rules** to ensure results conform to business policy — see [samples/basic_demo_ai_rules-supplier/readme.md](samples/basic_demo_ai_rules-supplier/readme.md)

<br>

- **Custom UIs, safely** — Vibe tools (Cursor, v0, etc.) generate the UI; it's built against the same governed API, so the logic runs the same regardless of what's calling it. Quick-start a React app from your (possibly customized) admin app: `Create a new react app named my-app-name from ui/admin/admin.yaml`.

<br>

- **RBAC** (Role Based Access Control) — declare row level security using technologies like Keycloak.

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>The Logic Architecture</strong> — any requirement format, one commit point (no bypass)</summary>

<br>The **Commit No Bypass** gate ensures these additional transaction sources — MCP, AI Rules, Custom UIs, and EAI's own Kafka producers and consumers — all converge on the same enforcement point.

<img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/architecture/logic-architecture-exec.png?raw=true" alt="Design and Runtime funnels into one governed Rules Engine" height="380" width="380" align="right">

That's the architecture: two funnels, converging on one engine, at the **same commit point. No bypass.**

* **Design Funnel:** all requirement formats — NL, Gherkin, pseudocode, formulas

* **Runtime Funnel:** all transaction sources — APIs, messages, MCP, agents, workflows

    * **This architecture is future-proofed:** a new integration tomorrow (another broker, custom API, an MCP tool call) inherits every rule already declared, automatically — because rules operate at the ORM layer, the same `before_flush` listener from above. Nothing to re-wire, nothing to remember to call.

*Full case: [Governance by Architecture, Not Discipline](https://apilogicserver.github.io/Docs/Tech-Gov-By-Arch/).*

</details>

&nbsp;

<details open markdown>
<summary>&emsp;&emsp;<strong>This is what makes Executable Requirements possible</strong> — at enterprise class</summary>

<br>We now have a comprehensive tool set (AI, rules for governance, enterprise integration services). These enable **Governed Enterprise Systems — from prompts**, in formats you already know, not a new syntax to learn:

- **Budget allocation system:**

    - [The prompt](samples/prompts/allocation.prompt.md) ([↗](https://github.com/ApiLogicServer/allocate_dept_account_demo/blob/main/docs/requirements/prompt.md)) that built it.
    - **Trust:** read [the resultant rules](samples/allocate_dept_account_demo/logic/logic_discovery/charge_distribution.py) ([↗](https://github.com/ApiLogicServer/allocate_dept_account_demo/blob/main/logic/logic_discovery/charge_distribution.py)) (or see the [logic diagram](samples/allocate_dept_account_demo/docs/requirements/logic_diagrams/logic_diagram.svg) ([↗](https://github.com/ApiLogicServer/allocate_dept_account_demo/blob/main/docs/requirements/logic_diagrams/logic_diagram.svg))) — they'll monitor every transaction.
    - **Verify:** AI read those same rules and wrote a [Behave test suite](samples/allocate_dept_account_demo/test/api_logic_server_behave/features/charge_distribution.feature) ([↗](https://github.com/ApiLogicServer/allocate_dept_account_demo/blob/main/test/api_logic_server_behave/features/charge_distribution.feature)) from them — no test written by hand. Running it produces an automated [Logic Report](samples/allocate_dept_account_demo/test/api_logic_server_behave/reports/Behave%20Logic%20Report.md) ([↗](https://github.com/ApiLogicServer/allocate_dept_account_demo/blob/main/test/api_logic_server_behave/reports/Behave%20Logic%20Report.md)) — 7 scenarios, 37 steps, all passing, with the rule chain's execution trace on every scenario. Not a hand-written report — regenerate it any time the rules change, and it's still true.

- **Canadian CBSA duty-calculation system:**

    - Use **actual regulations** — [this prompt](samples/demo_customs_surtax/readme.md) ([↗](https://github.com/ApiLogicServer/demo_customs_surtax/blob/main/docs/requirements/prompt.md)) reads them straight off the web, producing [these rules](samples/demo_customs_surtax/logic/logic_discovery/cbsa_steel_surtax.py) ([↗](https://github.com/ApiLogicServer/demo_customs_surtax/blob/main/logic/logic_discovery/cbsa_steel_surtax.py)).
    - **Proactive Human-in-the-loop:** the [ad-libs report](samples/demo_customs_surtax/docs/requirements/ad-libs.md) ([↗](https://github.com/ApiLogicServer/demo_customs_surtax/blob/main/docs/requirements/ad-libs.md)) lists every low-confidence decision — so you know exactly where it guessed.

- **Low Value Import Shipments (CLVS)** — screens dangerous goods, using internationally agreed rules:

    - [Business description](samples/demo_customs_clvs/readme.md) ([↗](https://github.com/ApiLogicServer/demo_customs_clvs/blob/main/readme.md)) and [actual requirements](samples/demo_customs_clvs/docs/requirements/customs_demo/requirements.md) ([↗](https://github.com/ApiLogicServer/demo_customs_clvs/blob/main/docs/requirements/customs_demo/requirements.md)), expressed in **Gherkin format**.
    - Complex incoming messages need only sample [XML examples](samples/requirements/customs_demo_clvs/docs/requirements/customs_demo/message_formats/demo-01-no-match.xml) ([↗](https://github.com/ApiLogicServer/demo_customs_clvs/blob/main/docs/requirements/customs_demo/message_formats/demo-01-no-match.xml)).
    - Rules make it **auditable** — logistics firm participation is *subject to audit*. Failure would mean hiring 100+ additional staff, an *8-figure exposure*. Auditors can [read the rules](samples/demo_customs_clvs/logic/logic_discovery/clvs_eligibility.py) [↗](https://github.com/ApiLogicServer/demo_customs_clvs/blob/main/logic/logic_discovery/clvs_eligibility.py), and trust they will be enforced - not sample and hope.  ([Full writeup →](https://apilogicserver.github.io/Docs/Tech-Ent-AI))

**Unburdened from logic, AI is free to do what it's great at** — reading any of these requirement formats and translating intent — while rules turn that intent into real, governed systems.

</details>

</details>

&nbsp;

<details markdown>
<summary>Scales Past One Project — Any Requirement Format Produces Governed Rules</summary>

<br>The three enterprise systems above ([Budget Allocation](samples/prompts/allocation.prompt.md), [CBSA Customs Surtax](samples/demo_customs_surtax/readme.md), [Customs CLVS](samples/demo_customs_clvs/readme.md)) were built from three different input formats — a plain prompt, actual regulation text, Gherkin — by different teams, writing the way they already write. All three came out the same way: governed rules, no bypass.

That's the point. A hand-coded system needs a correct handler for every path on every table — the discipline has to live in each team. Here, the pipeline supplies the paths. The second project doesn't depend on the first team's care, or on anyone learning a new methodology first.

Give us whatever, you get rules — even the hardest case. [A head-to-head test](https://apilogicserver.github.io/Docs/Tech-Standard-Reqs) fed the same naturally procedural spec to native AI and to this pipeline. Native AI built the insert path and silently dropped update and delete. The pipeline produced 5 governed rules covering every path. Same input, same AI — the difference was the architecture.

![Governance by Architecture, Not Discipline](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/architecture/proc-decl-simple.png?raw=true)

The GenAI-Logic side of that test, in full: [samples/basic_demo_genai_logic](samples/basic_demo_genai_logic) — the procedurally-phrased prompt, the 5 rules it produced, and confirmation all 9 change paths are governed, not just the one the prompt described.

![Procedural Spec In, Declarative Rules Out](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/exec_reqmts/proc-to-decl.png?raw=true)

The native-AI side, in full: [samples/bd_claude_native_ai](samples/bd_claude_native_ai) — the actual code, the prompt, and the [unedited transcript](samples/bd_claude_native_ai/transcript.md).

</details>

&nbsp;

<details markdown>
<summary>Business Users Empowered — a Friendly IDE, Guided by AI (via Context Engineering)</summary>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>A Business-User-Friendly IDE</strong> — same AI, same governed output, no developer tooling to learn</summary>

<br>

![reg-tech](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/exec_reqmts/reg-tech.png?raw=true)

*More: [Business-User-Friendly IDE →](https://apilogicserver.github.io/Docs/Introduction/#a-business-user-friendly-ide)*

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>No Proprietary Interface, No Rigid Structure</strong> — just ask the AI when you need guidance</summary>

<br>Traditional studios lock you into proprietary, rigid interfaces. Here, AI isn't boxed into a fixed structure — and when you need guidance, just ask.

![help-me](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/manager/help-me.png?raw=true)

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>And When You Need Even More Guidance</strong> — just ask the system to define Requirements From Interview</summary>

<br>And when you need even more guidance, just ask the system to define the **requirements from an interview** — AI will interview you on what's still ambiguous, then confirm before building. No spec-writing skill required going in.

![RFI](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/exec_reqmts/RFI.png?raw=true)

[Real transcript, unedited →](samples/requirements/RFI/RFI-transcript.md)

</details>

</details>

&nbsp;

<details markdown>
<summary>Promotes Business User and Developer Collaboration — One Artifact, One Toolset</summary>

<br>The rule a business user reads and the rule a developer debugs are the same lines, in the same file, in the same IDE — standard Python, standard tooling, your infrastructure, not a proprietary one.

No paying twice: once for the BU-built version, again when it hits its limit and a developer has to rebuild it to meet corporate standards. No finger-pointing between departments over whose fault the gap was — there's one artifact, one team owns it, from day one.

![collaboration](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/exec_reqmts/collaboration.png?raw=true)

</details>

&nbsp;

<details markdown>
<summary>Go deeper — beyond credit-check: security, customization, integration, logic debugging</summary>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>Guided tour</strong> — the full 30-45 min build, past what "The Ideal" showed</summary>

<br>**Create basic_demo** (auto-opens with guided tour option):
```bash
genai-logic create --project_name=basic_demo --db_url=sqlite:///samples/dbs/basic_demo.sqlite
```

**Inside the project:** Say to your AI assistant: *"Guide me through basic_demo"* (30-45 min hands-on tour).

> Teaches API creation, declarative rules, security, and Python customization. Fail-safe — scripts ensure no coding errors.

</details>

&nbsp;

<details markdown>
<summary>&emsp;&emsp;<strong>Your AI as on-call consultant</strong> — ask it anything, verify it doesn't just recite</summary>

<br>Same materials, same AI you've been using — it doesn't just write rules, it automates everything above and helps when things break: EAI's 2-message Kafka pattern, the AI/Request Pattern wiring, Executable Requirements' pre-coding schema assessment — all documented training material (`docs/training/*`) the AI reads *before* writing your code, not generic knowledge it's guessing from. Ask "what are rules?" or "how do rules work?" — or, without an AI handy, just read [samples/basic_demo_logic_gov/logic/readme_logic.md](samples/basic_demo_logic_gov/logic/readme_logic.md) — same material.

Ask it your own questions directly:
- Is this really infrastructure, like a database?
- Is this a black box? How do I debug a rule chain?
- Can I verify this with tests, not just take it on faith?
- What did the AI decide on its own that I should double-check? (the ad-libs report)
- Can I see a governance/health report for this project's logic?
- What does it take to migrate off this if we ever wanted to?
- How does this perform at scale?
- What does this integrate with — APIs, workflows, agents, MCP?
- Does this work with my existing database?

More background: [Eval Guide](https://apilogicserver.github.io/Docs/Eval/).

Put together: once the AI knows how the system works, it doesn't just generate rules instead of code — it helps you debug them, and helps you understand them. A design assistant, not just a coding assistant.

<details markdown>
<summary>&emsp;&emsp;&emsp;&emsp;<strong>The AI was trained on this material</strong> — can you trust its answers?</summary>

<br>Don't take them on faith. Ask the same question a different way, or ask something not covered here — like where this architecture breaks down. If it just recites the same lines back, you've caught it. If it reasons, that's the test passing.

</details>

Ready to see it for yourself? The demo catalog below runs the same systems live.

</details>

</details>

&nbsp;

&nbsp;

## 📚 Build It Yourself — Demo Catalog

The section above showed you pre-built samples to browse. These are the same use cases, but as commands you run yourself — paste one into your AI assistant and it builds that project for you, live.

> Tip: every project is AI-enabled — once it's built, ask your AI assistant how it works

&nbsp;

## 1. Enterprise-Class Systems From Requirements

Each of these builds a complete system from a single prompt or command — 💬 = say it to your AI assistant, › = run in a terminal:


| Use Case | 💬 Say to your AI, or › run | What You'll Learn |
|----------|---------|-------------------|
| **[Allocation with AI Rules](samples/allocate_dept_account_demo/docs/requirements/logic_flow_allocate_dept_account_demo.md)** <br> demo_allo_dept_gl | 💬 create demo_allo_dept_gl from samples/prompts/allocation.prompt.md <br> *or* <br> › genai-logic create --project_name=demo_allo_dept_gl --db_url=sqlite:///samples/dbs/starter.sqlite | - [Cascade Allocation (Costs to Depts/GL)](https://apilogicserver.github.io/Docs/Sample_Allo_Dept_GL_readme) <br> - AI Rules for fuzzy match to project |
| **[Customs CLVS](samples/requirements/customs_demo_clvs/docs/requirements/customs_demo/requirements.md)** <br> demo_customs_clvs | › genai-logic create  --project_name=demo_customs_clvs --db_url=sqlite:///samples/dbs/customs.sqlite | - Governed Business Systems<br> - EAI (using XML), textual requirements |
| **[Customs Surtax](samples/prompts/customs_cbsa.prompt.md)** <br> demo_customs_surtax | 💬 create project demo_customs_surtax from samples/prompts/customs_cbsa.prompt.md | - New Business System from Regulations |

&nbsp;

> **Running a cloned project?** F5 won't work until the venv is set up — see [Project-Env](https://apilogicserver.github.io/Docs/Project-Env/) for options (`genai-logic run`, symlink, or local venv).

&nbsp;

## 2. Enterprise Technology Demos

Each of these builds a complete system from a single prompt or command — 💬 = say it to your AI assistant, › = run in a terminal:


| Use Case | 💬 Say to your AI, or › run | What You'll Learn |
|----------|---------|-------------------|
| **[Use Case 1: AI Rules](samples/basic_demo_ai_rules-supplier/readme.md)**<br> demo_ai_rules_supplier | › genai-logic create --project_name=demo_ai_rules_supplier --db_url=sqlite:///samples/dbs/basic_demo.sqlite | - Use AI Rules (req pattern) to choose Optimal Supplier, per world conditions |
| **[Use Case 2: Governed MCP Server](https://apilogicserver.github.io/Docs/Sample-Basic-Demo-MCP-Send-Email)** <br>demo_mcp_send_email | › genai-logic create --project_name=demo_mcp_send_email --db_url=sqlite:///samples/dbs/basic_demo.sqlite | - Bus Users compose new service to send email to overdue customers, subject to email opt-out rules<br>- Create custom API with NL<br>- Create an email service (req pattern) |
| **[EAI: Enterprise App Integration](samples/basic_demo_eai/readme.md)** <br>demo_eai | › genai-logic create --project_name=demo_eai --db_url=sqlite:///samples/dbs/basic_demo.sqlite | - Executable Requirements<br>- Create custom API with NL<br>- Create Kafka Listener with NL |
| **[Use Case 4: Vibe Dev Backend](https://apilogicserver.github.io/Docs/Sample-Basic-Demo-Vibe)** <br> demo_vibe | › genai-logic create --project_name=demo_vibe --db_url=sqlite:///samples/dbs/basic_demo.sqlite | - UI elements, eg, Cards, Maps, Trees... |
| **[Requirements From Interview](https://apilogicserver.github.io/Docs/Exec-Reqmts/)** <br> basic_demo_rfi | 💬 paste [samples/prompts/basic_demo_rfi.prompt](samples/prompts/basic_demo_rfi.prompt) | - Most of this prompt is fully specified (AI builds those parts directly, no questions asked)<br>- And requests interview ("Also, interview me to work out this general intent: ...")... AI interviews you on that part only, confirms before building<br>- [Real transcript included](samples/requirements/RFI/RFI-transcript.md) |
| **[Use Case 5: Business Users](https://www.genai-logic.com/#h.69d2voz8q5r1)** <br> webgenai | See `webgenai/` in this Manager | - Create systems from browser, with logic, sample data and derived attributes |

&nbsp;


## 3. Additional Demos

Advanced examples and specialized patterns:

| Demo | 💬 Say to your AI, or › run | What You'll Learn |
|------|---------|-------------------|
| **Executable Requirements** | See [samples/requirements/readme_reqmts.md](samples/requirements/readme_reqmts.md) | Create from Gherkin requirements <br>implement reqs <path> |
| **New system from prompt** | › genai-logic genai --using=samples/prompts/genai_demo.prompt | Create systems from prompt<br>Like WebGenAI, but from IDE |
| **Coding Samples** | › code samples/nw_sample | Useful code examples<br>Search: `#als` |
| **MCP Discovery** <br> demo_copilot_mcp_discovery | › genai-logic create --project_name=demo_copilot_mcp_discovery --db_url=sqlite:///samples/dbs/basic_demo.sqlite | test rules via Copilot access to MCP Server | 


**Copy Snippets for venv:**
```bash title="Copy Snippets for venv"
source venv/bin/activate       # windows: venv\Scripts\activate
source ../venv/bin/activate    # windows: ../venv\Scripts\activate
python -m venv venv            # may require python3 -m venv venv
```

&nbsp;


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

&nbsp;

### Appendix

<details markdown>

<summary>Appendix</summary>

#### Recurrent Errors on Complex Business Logic Dependencies

The A/B test's two bugs came from AI writing *procedural logic* and missing the reparenting case — old parent left stale when a foreign key is reassigned. Separately, AI was also asked to generate the *Behave test suite* for `basic_demo_logic_gov` directly from the declared rules — a credible, well-structured result, reactive and API-driven, comparable in shape to test infrastructure that took weeks to write by hand for other sample projects in this repo. But it has the same gap: no scenario reassigns an existing order's customer or an existing item's product. Same AI, same underlying reasoning pattern, two different generative tasks (write the logic, write the tests for the logic) — one recurring miss.

That's not a knock on either result — both are genuinely useful starting points. It's evidence for the underlying claim: AI reasons locally, case by case, not by systematically enumerating a dependency graph — and that blind spot doesn't go away because you ask it to "be careful about dependencies" in a different task. It shows up again. **This is exactly what LogicBank takes off the table** — not just the reparenting case, but the entire category: every change path (insert, update, delete, and their combinations with every foreign key and conditional aggregate), across every use case, from every source (API, message, MCP, agent). Not because the rules are written more carefully, but because the engine derives the paths structurally — there's no enumeration step left for anyone, human or AI, to get wrong.

#### A Proven Technology

The 40X figure isn't a one-off — it's consistent with two decades of production measurement on a predecessor system (Versata, 1995-2010: 94-99% of logic automated by rules, typically ~97%, across several dozen systems). The remaining 3-6% is exactly the hand-written event code the guard below governs — most of a real system falls inside the declarative vocabulary, not outside it. This is the architect's own measurement, not an independently audited figure — treat it as a strong internal data point, not third-party verification. [Full history →](https://apilogicserver.github.io/Docs/Tech-Proven/)

#### Not a RETE Engine

Purpose-built for transaction processing, not inference/decision logic. [Why this matters →](https://apilogicserver.github.io/Docs/FAQ-RETE/)

#### Events and No Bypass

Hand-written event code can reopen the bug class — if a `row_event`/`commit_row_event` mutates a row directly, that value skips derivation, cascades, and constraints entirely. But this isn't a silent hole: the engine **refuses to start** if it detects a mutating event without an explicit `allow_row_mutation=True` override. The safe alternative (`early_row_event`, or `logic_row.insert()`) gets full rule processing automatically. Net effect: the escape hatch is closed by default, and every place it's deliberately opened is a single `grep` away. [Details →](https://apilogicserver.github.io/Docs/Logic-Type-Events/#events-must-not-mutate-row)

</details>
