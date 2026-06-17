---
title: CBSA Steel Derivative Goods Surtax
notes: gold source is docs
source: docs/Customs-readme-surtax
version: 1.0 from docsite, for readme, for readme 6/13/2026
---

# CBSA Steel Derivative Goods Surtax

**Audience:** Technical GenAI-Logic evaluators

**Project:** CBSA Steel Derivative Goods Surtax Order calculator (PC Number 2025-0917, program code 25267A)

&nbsp;

<details markdown>

<summary>Executable Requirements - Governance By Architecture, At Scale</summary>

<br>This demo creates an entire subsystem — database, API, business logic, and Admin App — from a single natural language prompt, using Method 4 (System Creation Services).

Unlike the Customs CLVS demo (which starts from an existing database and adds relationship/logic fixes), this project is generated **fresh, end-to-end, from the prompt alone**. The prompt is the requirement; Context Engineering ensures the result is enterprise-class — governed, auditable, and correct — not just a working demo.

</details>

&nbsp;

<details markdown>

<summary>Claude Code CLI Instructions</summary>

<br>Execute these steps from the Manager, using the Claude Code terminal.

**A. Activate Claude Code**

Open the Claude Code terminal in the Manager.

**B. Activate the venv**

```bash title='🤖 Paste into the terminal'
! source ../venv/bin/activate
```

**C. Implement the project from the prompt**

```text title='🤖 Paste this into the Claude Code chat (Agent mode, Claude Sonnet 4.6 recommended)'
implement project demo_customs_surtax from samples/prompts/customs_cbsa.prompt
```

This single instruction drives Method 4 (System Creation Services) end-to-end:

1. Loads Context Engineering (`.github/.copilot-instructions.md`)
2. Creates the project (`genai-logic create --project_name=demo_customs_surtax ...`), generating the database, models, API, and Admin App from the prompt
3. Translates the prompt's business rules into declarative `logic/logic_discovery` rules (not procedural FrankenCode)
4. Generates seed test data and runs the test suite
5. Writes `docs/requirements/readme` (provenance) and `docs/requirements/ad-libs` (every assumption made beyond the prompt spec)

</details>

&nbsp;

## The Prompt

```text title='Prompt: samples/prompts/customs_cbsa.prompt'
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917 
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order 
 under subsection 53(2) and paragraph 79(a) of the 
 Customs Tariff program code 25267A to calculate duties and taxes 
 including provincial sales tax or HST where applicable when 
 hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26' 
 and create runnable ui with examples from Germany (CETA — exempt), US (CUSMA — exempt), Japan (CPTPP — exempt), and China (subject, 25%)
  Transactions are received as a CustomsEntry with multiple 
SurtaxLineItems, one per imported product HS code.
```

&nbsp;

## Domain Summary

Transactions are `CustomsEntry` records with one or more `SurtaxLineItem` rows (one per HS code).

### Tax calculation chain

| Step | Rule | Table |
|---|---|---|
| 1 | Copy `effective_date`, `program_code`, `pc_number` from `SysConfig` | `CustomsEntry` |
| 2 | Copy `country_surtax_rate` from `CountryOrigin` | `CustomsEntry` |
| 3 | Copy `province_tax_rate` from `Province` | `CustomsEntry` |
| 4 | `surtax_applicable = 1` when `ship_date >= effective_date` AND `country_surtax_rate > 0` | `CustomsEntry` |
| 5 | Copy `base_duty_rate`, `is_steel_derivative` from `HsCodeRate` | `SurtaxLineItem` |
| 6 | `surtax_applicable = 1` when entry `surtax_applicable == 1` AND `is_steel_derivative == 1` | `SurtaxLineItem` |
| 7 | `base_duty_amount = customs_value * base_duty_rate` | `SurtaxLineItem` |
| 8 | `surtax_amount = customs_value * country_surtax_rate` (if line `surtax_applicable`) | `SurtaxLineItem` |
| 9 | Sum `total_customs_value`, `total_duty_amount`, `total_surtax_amount` | `CustomsEntry` |
| 10 | `duty_paid_value = total_customs_value + total_duty_amount + total_surtax_amount` | `CustomsEntry` |
| 11 | `sales_tax_amount = duty_paid_value * province_tax_rate` | `CustomsEntry` |
| 12 | `total_tax_due = total_duty_amount + total_surtax_amount + sales_tax_amount` | `CustomsEntry` |

### Example countries in seed data

| Country | Agreement | Surtax rate |
|---|---|---|
| Germany (DE) | CETA | 0% |
| United States (US) | CUSMA | 0% |
| Japan (JP) | CPTPP | 0% |
| China (CN) | — | 25% |

### Provinces in seed data

| Province | Tax rate (pre-combined GST/PST/HST) |
|---|---|
| Ontario (ON) | 13% |
| Alberta (AB) | 5% |
| British Columbia (BC) | 12% |
| Nova Scotia (NS) | 15% |
| Manitoba (MB) | 12% |

&nbsp;

## Results: System, Test Suite and Report

### System: API, Database, Logic, Admin App

The GenAI-Logic `create` command builds a complete, runnable project: the JSON:API server (with Swagger), a full CRUD Admin App, and 18 declarative rules in `logic/logic_discovery/cbsa_steel_surtax.py` implementing the tax calculation chain above.

### Test Suite and Report

The GenAI-Logic `create` command also builds test services and Context Engineering. These enable the LLM to generate tests that prove the code works, and to produce readable test reports that elucidate the logic.

&nbsp;

## How it Works

### Authoring

1. Copilot loads Context Engineering (`.github/.copilot-instructions.md`, `docs/training`)
2. Invokes `genai-logic create --project_name=demo_customs_surtax ...` to scaffold the project — database, models, API, Admin App — all runnable, but no logic yet
3. Copilot then, under the guidance of Context Engineering:
    * Translates the prompt's business rules into declarative rules (`logic/logic_discovery`, *not FrankenCode*)
    * Generates seed test data (with values initialized per rules)
    * Runs the test suite

### Execution

Execution uses deterministic runtime engines (ORM, API, Logic) — no probabilistic AI calls at runtime. The result is correct by architecture, auditable to regulators, and maintainable by a single developer.
