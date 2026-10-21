<!-- Text for the report, laid out in the report's own order, so you can read it top to bottom against the report.
     The text under a heading, and each block introduced by a comment line  text: name, replaces the built-in text.
     Leave one out to keep the built-in text, or leave it empty to show nothing.
     Grey lines starting with  > ⚙ generated:  show where generated content (tables, counts, logs) appears; they are fixed.
     To rename a section, put a comment line  title: New Name  under its heading.
     The first heading (single #) is the report's title, with a subtitle under it. Double curly braces are filled in by the generator. -->

# Requirements Traceability Report

This report shows requirements, the rules created from them, and the tests created from those rules.

<!-- text: cover -->
This report is generated from the project's own files: its requirements, the rules and integrations built from them, and the tests that check them. Nothing in it is written by hand. Open **Background** (below the summary) for what the terms mean, how to read the report, and what it does and does not establish.

> ⚙ generated: project line (name, date, rule and test counts, generator version), last test run, and a banner if any scenario failed

## At a Glance

<!-- (no introduction by default; add one here) -->

> ⚙ generated: verdict and scorecard (status, requirements, tests, last run, rules, security, messages)

<!-- text: scorecard-note -->
_Status: ✅ every requirement is implemented and tested, all scenarios pass, and the results are current. ⚠ a requirement is untested or unimplemented, there is no test run, or files changed since the last run. ❌ a scenario failed. This reports what was traced and tested, not that the system is correct._

> ⚙ generated: About this project (from the project's readme)

<!-- text: background -->
<details markdown>
<summary>Background: what this report is, and how to read it</summary>

**What a requirement is**

A **requirement** is a statement of business behavior, written in plain language as a Gherkin feature (Given / When / Then). It lives in the project at `docs/requirements/<name>/requirements.md`. The system is built from these requirements, and this report is organized around them.

**How the system was built**

1. **Requirements** state what the system must do.
2. **Rules and integrations** implement them. A *rule* is a declaration about the data (for example, "a customer's balance is the sum of the unshipped order totals, and must not exceed the credit limit"). Rules are not called by code: the engine enforces them on every commit, whether the change came from the Admin App, the API, or a message. *Integrations* are the API endpoints and Kafka topics.
3. **Tests** (Behave scenarios) drive the running system the way any client would and check the outcome.
4. **This report** connects them: each requirement, to the rules and handlers that implement it, to the tests that exercise it, to the logic log that shows which rules ran.

**How to read it**

| If you are... | Start with | Look for |
|---|---|---|
| Business owner | *Requirements in detail* | The requirement text, then the **Tests** line under it: does a test exist, and did it pass? |
| Auditor | *Coverage summary*, *Rule coverage by tests*, *Messages and APIs* | Gaps (untested, untraced), the date of the last test run, and how each rule was shown to run |
| Developer | *Tests and Results* | Each scenario's logic log: every rule that ran, in order, with old and new values |

**What this report establishes, and what it does not**

**It establishes**
- Which files and rules implement each requirement, read from the project's source.
- Which scenarios ran at the last test run, and whether each passed.
- Which rules the engine reported running in each scenario's logic log.

**It does not establish**
- That a requirement is complete or correct. It traces what was written down.
- That a rule took effect because it appears in a log. An event runs on every commit of its class and decides for itself whether to act.
- That a constraint was exercised, unless a scenario made it reject a transaction. A constraint appears in the log only when it rejects.
- That a message reached a broker or an endpoint, unless a test step looks for it there. The *Messages and APIs* table flags channels no test mentions.
- That the results are current. They are as old as the last test run, shown in the header, and the header warns if files changed after it.
- Which version of a requirement the code was built against, or which clause of a requirement a given rule serves.

**Terms**

| Term | Meaning |
|---|---|
| Requirement | A Gherkin feature describing business behavior; the unit this report traces. |
| Rule | A declaration about data (sum, count, formula, copy, constraint) that the engine enforces at every commit. |
| Event | Python code the engine calls when a row of a given class changes (for example, to publish a message). |
| Handler | Code that serves an API endpoint or consumes a Kafka topic. |
| Scenario | One Behave test: a short Given / When / Then script run against the live API. |
| Logic log | The engine's record of every rule it ran in a transaction, nested to show cascades (an Item change adjusts its Order, which adjusts its Customer). |
| Phase | The step of a commit: ROW LOGIC (derivations, constraints), COMMIT LOGIC (checks that need finished totals), AFTER_FLUSH LOGIC (events that need database-assigned keys, such as publishing). |
| Seen | The engine reported running the rule in that scenario's log. |

</details>

## Contents

<!-- (no introduction by default; add one here) -->

> ⚙ generated: one link per section above

## Requirements Coverage

Traceability here is **forward** (requirement, to the rules, handlers and grants that implement it, to the tests that exercise it) and **backward** (implementation and tests, to the requirement they serve). Anything with no requirement is listed as untraced, and every requirement with no implementation or no test is listed as a gap. Links are made by the `Feature:` names and `§N` tags that requirements, code and tests carry.

### Coverage summary

> ⚙ generated: coverage summary table

<!-- text: coverage-note -->
_Test results are as current as the last run (see the header). A gap is any requirement with no implementation or no test._

<details markdown>
<summary>How to read this table</summary>

Test results are read from `logs/behave.log`, so they are only as current as that run. Not recorded here: which version of a requirement the code was built against, and which clause of a requirement a given rule serves.

</details>

### Traceability matrix

> ⚙ generated: matrix: requirement, implemented by, rules, tests

### Rule coverage by tests

> ⚙ generated: table: rule, requirement, scenarios where the engine's log shows it

<!-- text: rule-coverage-note -->
_"Seen" means the engine's log shows the rule ran, not proof that it took effect._

<details markdown>
<summary>How to read this table</summary>

"Seen" means the engine reported running the rule in that scenario's logic log. A scenario can only contribute if it has a log (see the coverage summary): a test that does not open one writes into whichever log was open last, and its rules are then credited to that scenario, or to the shared log. An event's function runs on every commit of its class, and its own condition decides whether it acts, so seen does not mean it took effect. A constraint appears in the log only when it rejects a transaction, so it is seen only in scenarios that make it reject. "Not seen" therefore means no log shows it, not that no test ran it.

</details>

### Requirements in detail

> ⚙ generated: rule counts for the project

<!-- text: inventory-note -->
_Declarative rules are read directly from their declarations; functions and events are Python, so the report shows each one's docstring, not an analysis of its code._

<!-- text: detail-intro -->
Each requirement is followed by the rules and handlers in the files that implement it. Logic diagrams are shown (click to expand) where they exist.

<!-- text: diagrams-howto -->
<details markdown>
<summary>{{diagram_title}}</summary>

Needs Graphviz (`brew install graphviz`). Tell your AI assistant:

```
create logic diagram for each requirement
```

or run this from the Manager root{{manager_clause}}:

```
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py {{project}} --each
```

Each diagram is saved under `docs/requirements/<name>/logic_diagrams/`. Then regenerate this report (`python requirements_traceability_report.py run`, from `test/api_logic_server_behave`).

</details>

&nbsp;

> ⚙ generated: one "#### §N requirement" block per requirement: its text, its rules and handlers, and a fold with its logic diagram

#### Rules not traced to a requirement

> ⚙ generated: table of rules that no requirement claims

## Data Model

<!-- (no introduction by default; add one here) -->

> ⚙ generated: database diagram

<!-- text: data-model-note -->
_Generated from `docs/db.dbml` (parents above children; shaded rows are derived by rules). To use your own layout, save it as `docs/db_diagram.png`._

### Derived columns

> ⚙ generated: table of derived columns and their rules

## Security (RBAC)

<!-- (no introduction by default; add one here) -->

> ⚙ generated: security status

### Roles and CRUD (DefaultRolePermission)

> ⚙ generated: table

### Row-level grants (Grant)

> ⚙ generated: table

## Messages and APIs

<!-- (no introduction by default; add one here) -->

> ⚙ generated: messages and APIs table

<!-- text: tests-mention-note -->
_"Tests mention it" checks the test sources, not delivery._

<details markdown>
<summary>How to read this column</summary>

A passing scenario proves a message reached a topic or an endpoint only if its steps look for it there. A handler that ran (see the logic log) is weaker evidence than a step that consumes the message. Channels no test mentions are flagged.

</details>

<!-- text: messages-note -->
<details markdown>
<summary>How to read this table</summary>

Topics and endpoints are read from the discovery folders. The condition that triggers an outbound message lives in Python (see the rules under each requirement); here it is described by the handler's docstring. "Tables created" lists rows the handler's code constructs, following its calls within the project; blank means none were found, not that none exist.

</details>

> ⚙ generated: message shapes (one fold per topic)

## Tests and Results

> ⚙ generated: pass/fail status line

<!-- text: intro -->
These are Behave scenarios. Each one drives the running API the way any client would (create an order, change a quantity, ship it) and checks the result.

**The logic log** is what makes them more than pass/fail. Business rules run inside the server on every commit, so the server records exactly what they did, and this report embeds that record for each scenario. Two things to look for:

1. **It shows every rule that runs.** Each line is one rule execution, with the row's state, old and new values. You see not just that a test passed, but which rules ran and what each one changed.
2. **The nesting shows multi-table chaining.** Indentation follows the cascade: a change to an Item adjusts its Order, which adjusts its Customer.

<details markdown>
<summary>How to read the logic log</summary>

Open a scenario's "Rules exercised and logic log" block to see it. The log is shown in full, attribute values included, because those values are what you diagnose from when a rule produces an unexpected result.

To read a log line:

```
....Order[16] {Update - Adjusting order: amount_total} id: 16, customer_id: 19, amount_total:  [0.0-->] 90.0
```

- The leading dots are the depth in the cascade: Item (2 dots), its Order (4), its Customer (6).
- `Order[16]` is the row; `{...}` is the rule or action that ran; the rest is the row's attribute values at that step.
- `[0.0-->] 90.0` marks a value the rules changed, with its old and new value.
- The log is in phases: **ROW LOGIC** (derivations and constraints, as rows change), **COMMIT LOGIC** (checks that need the finished aggregates), and **AFTER_FLUSH LOGIC** (events that need database-assigned keys, such as the Kafka publish).

More: [Logic Log](https://apilogicserver.github.io/Docs/Logic-Debug/#logic-log).

</details>

&nbsp;

<!-- text: tests-howto -->
<details markdown>
<summary>{{howto_title}}</summary>

**1. Have AI create them.** This project's context tells your AI assistant how (`.github/copilot-instructions.md`, `docs/training/testing.md`). Just say:

```
create tests from rules
```

The assistant reads `database/models.py`, the logic files and the custom APIs, then writes `.feature` files and step implementations under `test/api_logic_server_behave/features/`. Then say `run the tests` and `run the requirements traceability report` and the assistant does both.

{{feature_prompt}}
**2. You can also define tests manually.** Add a `<name>.feature` file (Gherkin) under `test/api_logic_server_behave/features/` and its steps under `features/steps/`. The steps call the running API, so tests exercise the same rules as any client. See `docs/training/testing.md` for the patterns that keep tests repeatable.

**Or run them yourself** (server running, from `test/api_logic_server_behave`):

```
python behave_run.py --outfile=logs/behave.log
python requirements_traceability_report.py run
```

</details>

> ⚙ generated: used inside the fold above, where {{feature_prompt}} is (only when the project has requirements)

<!-- text: feature-prompt -->
Or, to have each requirement's tests linked in the Tests column above (it matches on `Feature:` name), say which names to use:

```
create tests from rules, one Feature per requirement, named exactly:
{{feature_names}}
```

_Tests with other names still run and appear below; they just aren't linked to a requirement._

> ⚙ generated: for each feature a "### Feature: <name>" heading; for each scenario a "#### Scenario: <name>" block with a fold for its rules and logic log

## Provenance

<!-- (no introduction by default; add one here) -->

> ⚙ generated: how this report was produced (date, generator and version, text source, last test run, project, requirement files)

<!-- text: provenance-note -->
_The report is derived from the project's files and the last test run; nothing in it is stored anywhere else, so regenerating it always reflects the project as it is now._
