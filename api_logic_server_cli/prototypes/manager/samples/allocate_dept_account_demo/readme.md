---
title: Allocate Project Payments to configured Departments/Accounts
notes: gold source is docs
source: docs/Sample_Allo_Dept_GL_readme
version: 1.0 from docsite, for readme, for readme 3/10/26
---

# Allocate Project Payments to configured Departments/Accounts

**Audience:** Technical GenAI-Logic evaluators

**Project:** Allocate Project Payments to configured Departments/Accounts

**Run Instructions:** at end



## Creation Prompts

Requires 16.02.07, windows or mac.

<br>

## With Fuzzy Lookup Logic

This finds the Project from Contractor information:

```text title='🤖 Paste this into the copilot chat to create: Allocate Project Contractor Payments to configured Departments/Accounts'
Departments own a series of General Ledger Accounts.

Departments also own Department Charge Definitions — each defines what percent
of an allocated cost flows to each of the Department's GL Accounts.
An active Department Charge Definition must cover exactly 100% (derived: 
total_percent = sum of lines; is_active = 1 when total_percent == 100).

Project Funding Definitions define which Departments fund a designated percent
of a Project's costs, and which Department Charge Definition each Department
applies. An active Project Funding Definition must cover exactly 100% (derived:
total_percent = sum of lines; is_active = 1 when total_percent == 100).

Projects are assigned to a Project Funding Definition.

When a Charge is received against a Project, cascade-allocate it in two levels:
  Level 1 — allocate the Charge amount to each Department per their 
             Project Funding Line percent → creates ChargeDeptAllocation rows
  Level 2 — allocate each ChargeDeptAllocation amount to that Department's 
             GL Accounts per their Charge Definition line percents
             → creates ChargeGlAllocation rows

Constraint: a Charge may only be posted if the Project's 
Project Funding Definition is active.

Charges can be placed by contractors.  They may supply only a minimal project description to identify the Project - use AI Rules to find an Active Project based on a fuzzy match to project name, and past charges from the contractor.  For example, you might observe that a contractor works on roads vs construction.

Total the charges into the Project and GL Account.
```


```bash title='🤖 Bootstrap Copilot by pasting the following into the chat'
Please load `.github/.copilot-instructions.md`
```

&nbsp;

<br>

```text title='🤖 Paste this into the copilot chat to create: Allocate Project Payments to configured Departments/Accounts'
Departments own a series of General Ledger Accounts.

Departments also own Department Charge Definitions — each defines what percent
of an allocated cost flows to each of the Department's GL Accounts.
An active Department Charge Definition must cover exactly 100% (derived: 
total_percent = sum of lines; is_active = 1 when total_percent == 100).

Project Funding Definitions define which Departments fund a designated percent
of a Project's costs, and which Department Charge Definition each Department
applies. An active Project Funding Definition must cover exactly 100% (derived:
total_percent = sum of lines; is_active = 1 when total_percent == 100).

Projects are assigned to a Project Funding Definition.

When a Charge is received against a Project, cascade-allocate it in two levels:
  Level 1 — allocate the Charge amount to each Department per their 
             Project Funding Line percent → creates ChargeDeptAllocation rows
  Level 2 — allocate each ChargeDeptAllocation amount to that Department's 
             GL Accounts per their Charge Definition line percents
             → creates ChargeGlAllocation rows

Constraint: a Charge may only be posted if the Project's 
Project Funding Definition is active.
```

&nbsp;

## Admin App Fixup

You may need to remind Copilot to update the Admin App.  Often, you can rename `admin-merge.yml` to `admin.yml`.

&nbsp;

# Results

![summary](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/allocation/allo-dept-gl/allo_dept_gl_screen.png?raw=true)
