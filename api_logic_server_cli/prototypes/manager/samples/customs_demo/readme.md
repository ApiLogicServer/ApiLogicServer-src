---
title: Customs Surtax Calculator
notes: gold source is docs
source: docs/Customs-readme
version: 1.0 from docsite, for readme, for readme 2/16/2026
---

# Customs Surtax POC — Engineering README

**Audience:** Technical GenAI-Logic evaluators

**Project:** CBSA Steel Derivative Goods Surtax calculator, built as a proof-of-concept.

**Run Instructions:** at end


## Creation Prompts

Requires 16.02, windows or mac.

<br>

```bash title='🤖 Bootstrap Copilot by pasting the following into the chat'
Please load `.github/.copilot-instructions.md`
```

<br>

```text title='🤖 To Create the system, paste this into the copilot chat'
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917 
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order 
 under subsection 53(2) and paragraph 79(a) of the 
 Customs Tariff program code 25267A to calculate duties and taxes 
 including provincial sales tax or HST where applicable when 
 hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26' 
 and create runnable ui with examples from Germany, US, Japan and China" 
 this prompt created the tables in db.sqlite.
  Transactions are received as a CustomsEntry with multiple 
SurtaxLineItems, one per imported product HS code.
```

> See also the proposed prompt

```text title='🤖 Optionally, create the test suite'
create behave tests from CBSA_SURTAX_GUIDE
```

<br>

## Results: system, test suite and report

### System: API, Database, Logic, Admin App

![app](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/ui-vibe/customs/app_screenshot.png?raw=true)


### Test Suite and Report

The GenAI-Logic `create` command builds test services and Context Engineering. These enable the LLM to generate tests that proved the code worked, as well as elucidate the logic through readable test reports.

![behave rpt](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/ui-vibe/customs/behave_report_git.png?raw=true)

<br>

## Run Instructions

Start the server, and enter a SurTax Order:

* Country Origin: China
* Province: ON
* Order Number: <any unique>

And a SurTaxLineItem:

* Line #: 1
* Quantity: 1
* Price: 10000
* HS Code: < the first>

ReQuery, and Verify Total Amount Due: 14125

<br>

## Proposed Fixed Prompt

Two targeted changes: (1) province → single flat rate, (2) country/province/hs_code → FK references.

```
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917 
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order 
 under subsection 53(2) and paragraph 79(a) of the 
 Customs Tariff program code 25267A to calculate duties and taxes.
 Lookup tables: HSCodeRate (hs_code PK, surtax_rate), 
 CountryRate (country_code PK, surtax_rate), 
 Province (province_code PK, tax_rate — a single pre-combined rate whether HST or GST+PST).
 SurtaxLineItem references these by FK: hs_code_id, country_id, province_id.
 ship date >= '2025-12-26'.
 Create runnable ui with examples from Germany, US, Japan and China.
 Transactions are received as a CustomsEntry with multiple 
 SurtaxLineItems, one per imported product HS code.
```

**Key changes:**

- `"provincial sales tax or HST where applicable"` → `"Province (province_code PK, tax_rate — a single pre-combined rate whether HST or GST+PST)"`  eliminates the conditional/multi-column trigger
- `"country of origin"` + `"province code"` + `"hs codes"` → explicit `Lookup tables: ... SurtaxLineItem references these by FK` — forces FK relationships, enables `Rule.copy`
- Constraints (`ship_date >= entry_date`, `quantity > 0`, `unit_price > 0`) still need to be added explicitly or via CE
