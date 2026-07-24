This report shows test results with embedded logic execution traces.

**For complete documentation on using Behave:** See [Behave.md](https://apilogicserver.github.io/Docs/Behave/)

**About This Project:**

> // to create: implement demo_allo_dept_gl from samples/prompts/allocation.prompt.md
>
> Departments own a series of General Ledger Accounts.
>
> Departments also own Department Charge Definitions — each defines what percent
> of an allocated cost flows to each of the Department's GL Accounts.
> An active Department Charge Definition must cover exactly 100% (derived:
> total_percent = sum of lines; is_active = 1 when total_percent == 100).
>
> Project Funding Definitions define which Departments fund a designated percent
> of a Project's costs, and which Department Charge Definition each Department
> applies. An active Project Funding Definition must cover exactly 100% (derived:
> total_percent = sum of lines; is_active = 1 when total_percent == 100).
>
> Projects are assigned to a Project Funding Definition.
>
> When a Charge is received against a Project, cascade-allocate it in two levels:
>   Level 1 — allocate the Charge amount to each Department per their
>              Project Funding Line percent → creates ChargeDeptAllocation rows
>   Level 2 — allocate each ChargeDeptAllocation amount to that Department's
>              GL Accounts per their Charge Definition line percents
>              → creates ChargeGlAllocation rows
>
> Constraint: a Charge may only be posted if the Project's
> Project Funding Definition is active.

&nbsp;

This report combines:

* Behave log (lists Features, test Scenarios, results), with embedded
* Logic showing rules executed, and how they operated

---

# Behave Logic Report
&nbsp;
&nbsp;
## Feature: About Sample  
  
&nbsp;
&nbsp;
### Scenario: Transaction Processing
&emsp;  Scenario: Transaction Processing  
&emsp;&emsp;    Given Sample Database  
&emsp;&emsp;    When Transactions are submitted  
&emsp;&emsp;    Then Enforce business policies with Logic (rules + code)  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Transaction Processing
```
  ProjectFundingDefinition  
    1. Derive <class 'database.models.ProjectFundingDefinition'>.is_active as Formula (1): as_expression=lambda row: 1 if row.total_percent  [...]  
    2. Derive <class 'database.models.ProjectFundingDefinition'>.total_percent as Sum(ProjectFundingLine.percent Where  - None)  
```
**Logic Log** in Scenario: Transaction Processing
```
Logic Phase:		ROW LOGIC		(session=0x10ac6b240) (sqlalchemy before_flush)			 - 2026-07-24 11:57:31,063 - logic_logger - INF
..ProjectFundingLine[None] {Insert - client} id: None, project_funding_definition_id: 5, department_id: 9, dept_charge_definition_id: 8, percent: 60, notes: None  row: 0x10acf9450  session: 0x10ac6b240  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,063 - logic_logger - INF
....ProjectFundingDefinition[5] {Update - Adjusting project_funding_definition: total_percent} id: 5, name: Test PFD 1784919451056, total_percent:  [0.0000-->] 60.0000, is_active: 0, notes: None  row: 0x10ae8ab50  session: 0x10ac6b240  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,064 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10ac6b240)   										 - 2026-07-24 11:57:31,064 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10ac6b240)   										 - 2026-07-24 11:57:31,064 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
## Feature: Charge Distribution Rules  
  
&nbsp;
&nbsp;
### Scenario: Charge Posted - cascades to dept and GL allocations
&emsp;  Scenario: Charge Posted - cascades to dept and GL allocations  
&emsp;&emsp;    Given a funding setup with Roads 60% / Construction 40%  
    And Roads splits to Labor 60% / Equipment 40%  
    And Construction splits to Labor 70% / Materials 30%  
&emsp;&emsp;    When a Charge of 100000 is posted to the Project  
&emsp;&emsp;    Then Charge total_distributed_amount is 100000  
    And ChargeDeptAllocation amounts are 60000 and 40000  
    And ChargeGlAllocation amounts for Roads are 36000 and 24000  
    And ChargeGlAllocation amounts for Construction are 28000 and 12000  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Charge Posted - cascades to dept and GL allocations
```
  Charge  
    1. RowEvent Charge.identify_project_for_charge()   
    2. Derive <class 'database.models.Charge'>.total_distributed_amount as Sum(ChargeDeptAllocation.amount Where  - None)  
    3. RowEvent Charge.check_active_funding()   
  ChargeDeptAllocation  
    4. Derive <class 'database.models.ChargeDeptAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
    5. Derive <class 'database.models.ChargeDeptAllocation'>.percent as Copy(project_funding_line.percent)  
  ChargeGlAllocation  
    6. Derive <class 'database.models.ChargeGlAllocation'>.percent as Copy(dept_charge_definition_line.percent)  
    7. Derive <class 'database.models.ChargeGlAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
  GlAccount  
    8. Derive <class 'database.models.GlAccount'>.total_allocated as Sum(ChargeGlAllocation.amount Where  - None)  
  Project  
    9. Derive <class 'database.models.Project'>.total_charges as Sum(Charge.amount Where  - None)  
```
**Logic Log** in Scenario: Charge Posted - cascades to dept and GL allocations
```
Logic Phase:		ROW LOGIC		(session=0x10ac6a690) (sqlalchemy before_flush)			 - 2026-07-24 11:57:31,094 - logic_logger - INF
..Charge[None] {Insert - client} id: None, project_id: 8, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: None, description: Behave test charge, charge_date: None  row: 0x10ae191d0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,094 - logic_logger - INF
..Charge[None] {server_defaults: total_distributed_amount } id: None, project_id: 8, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10ae191d0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,094 - logic_logger - INF
..Charge[None] {server aggregate_defaults: total_distributed_amount } id: None, project_id: 8, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10ae191d0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,094 - logic_logger - INF
..Charge[None] {BEGIN Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 8, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10ae191d0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,095 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae68830  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,095 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 9, dept_charge_definition_id: 8, percent: 60.0000, amount: 60000.0000  row: 0x10ae68830  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,095 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 9, dept_charge_definition_id: 8, percent: 60.0000, amount: 60000.0000  row: 0x10ae68830  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,096 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10ae882d0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,096 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 14, percent: 60.0000, amount: 36000.00000000  row: 0x10ae882d0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,096 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 14, percent: 60.0000, amount: 36000.00000000  row: 0x10ae882d0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,097 - logic_logger - INF
........GlAccount[14] {Update - Adjusting gl_account: total_allocated} id: 14, department_id: 9, account_number: 510700, name: roads_labor 1784919451070, total_allocated:  [0.00-->] 36000.00000000, notes: None  row: 0x10ae89cd0  session: 0x10ac6a690  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,097 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10ae8acd0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,097 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 15, percent: 40.0000, amount: 24000.00000000  row: 0x10ae8acd0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,097 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 15, percent: 40.0000, amount: 24000.00000000  row: 0x10ae8acd0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,097 - logic_logger - INF
........GlAccount[15] {Update - Adjusting gl_account: total_allocated} id: 15, department_id: 9, account_number: 510751, name: roads_equipment 1784919451075, total_allocated:  [0.00-->] 24000.00000000, notes: None  row: 0x10ae886d0  session: 0x10ac6a690  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,098 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 9, dept_charge_definition_id: 8, percent: 60.0000, amount: 60000.0000  row: 0x10ae68830  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,098 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 9, dept_charge_definition_id: 8, percent: 60.0000, amount: 60000.0000  row: 0x10ae68830  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,098 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 8, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount:  [0-->] 60000.0000, description: Behave test charge, charge_date: None  row: 0x10ae191d0  session: 0x10ac6a690  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,098 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae68a70  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,098 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 10, dept_charge_definition_id: 9, percent: 40.0000, amount: 40000.0000  row: 0x10ae68a70  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,098 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 10, dept_charge_definition_id: 9, percent: 40.0000, amount: 40000.0000  row: 0x10ae68a70  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,099 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10ae8bed0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,099 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 16, percent: 70.0000, amount: 28000.00000000  row: 0x10ae8bed0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,099 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 16, percent: 70.0000, amount: 28000.00000000  row: 0x10ae8bed0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,100 - logic_logger - INF
........GlAccount[16] {Update - Adjusting gl_account: total_allocated} id: 16, department_id: 10, account_number: 510810, name: construction_labor 1784919451081, total_allocated:  [0.00-->] 28000.00000000, notes: None  row: 0x10ae16c50  session: 0x10ac6a690  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,101 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10ae16050  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,101 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 17, percent: 30.0000, amount: 12000.00000000  row: 0x10ae16050  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,101 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 17, percent: 30.0000, amount: 12000.00000000  row: 0x10ae16050  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,101 - logic_logger - INF
........GlAccount[17] {Update - Adjusting gl_account: total_allocated} id: 17, department_id: 10, account_number: 510871, name: construction_materials 1784919451087, total_allocated:  [0.00-->] 12000.00000000, notes: None  row: 0x10ae8bb50  session: 0x10ac6a690  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,101 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 10, dept_charge_definition_id: 9, percent: 40.0000, amount: 40000.0000  row: 0x10ae68a70  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,101 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 10, dept_charge_definition_id: 9, percent: 40.0000, amount: 40000.0000  row: 0x10ae68a70  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,101 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 8, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount:  [60000.0000-->] 100000.0000, description: Behave test charge, charge_date: None  row: 0x10ae191d0  session: 0x10ac6a690  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,102 - logic_logger - INF
..Charge[None] {END Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 8, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 100000.0000, description: Behave test charge, charge_date: None  row: 0x10ae191d0  session: 0x10ac6a690  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,102 - logic_logger - INF
....Project[8] {Update - Adjusting project: total_charges} id: 8, name: Test Project 1784919451059, project_funding_definition_id: 5, total_charges:  [0.00-->] 100000.00, notes: None  row: 0x10ae8afd0  session: 0x10ac6a690  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,102 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10ac6a690)   										 - 2026-07-24 11:57:31,102 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10ac6a690)   										 - 2026-07-24 11:57:31,104 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Charge total_distributed_amount rollup - sums dept allocations
&emsp;  Scenario: Charge total_distributed_amount rollup - sums dept allocations  
&emsp;&emsp;    Given a funding setup with Roads 60% / Construction 40%  
    And Roads splits to Labor 60% / Equipment 40%  
    And Construction splits to Labor 70% / Materials 30%  
&emsp;&emsp;    When a Charge of 50000 is posted to the Project  
&emsp;&emsp;    Then Charge total_distributed_amount is 50000  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Charge total_distributed_amount rollup - sums dept allocations
```
  Charge  
    1. RowEvent Charge.identify_project_for_charge()   
    2. Derive <class 'database.models.Charge'>.total_distributed_amount as Sum(ChargeDeptAllocation.amount Where  - None)  
    3. RowEvent Charge.check_active_funding()   
  ChargeDeptAllocation  
    4. Derive <class 'database.models.ChargeDeptAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
    5. Derive <class 'database.models.ChargeDeptAllocation'>.percent as Copy(project_funding_line.percent)  
  ChargeGlAllocation  
    6. Derive <class 'database.models.ChargeGlAllocation'>.percent as Copy(dept_charge_definition_line.percent)  
    7. Derive <class 'database.models.ChargeGlAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
  GlAccount  
    8. Derive <class 'database.models.GlAccount'>.total_allocated as Sum(ChargeGlAllocation.amount Where  - None)  
  Project  
    9. Derive <class 'database.models.Project'>.total_charges as Sum(Charge.amount Where  - None)  
```
**Logic Log** in Scenario: Charge total_distributed_amount rollup - sums dept allocations
```
Logic Phase:		ROW LOGIC		(session=0x10ac6a9c0) (sqlalchemy before_flush)			 - 2026-07-24 11:57:31,162 - logic_logger - INF
..Charge[None] {Insert - client} id: None, project_id: 9, contractor_id: None, project_description: None, amount: 50000, total_distributed_amount: None, description: Behave test charge, charge_date: None  row: 0x10af05a90  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,162 - logic_logger - INF
..Charge[None] {server_defaults: total_distributed_amount } id: None, project_id: 9, contractor_id: None, project_description: None, amount: 50000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af05a90  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,162 - logic_logger - INF
..Charge[None] {server aggregate_defaults: total_distributed_amount } id: None, project_id: 9, contractor_id: None, project_description: None, amount: 50000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af05a90  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,162 - logic_logger - INF
..Charge[None] {BEGIN Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 9, contractor_id: None, project_description: None, amount: 50000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af05a90  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,163 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae69130  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,163 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 11, dept_charge_definition_id: 10, percent: 60.0000, amount: 30000.0000  row: 0x10ae69130  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,163 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 11, dept_charge_definition_id: 10, percent: 60.0000, amount: 30000.0000  row: 0x10ae69130  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,164 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10aee19d0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,164 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 18, percent: 60.0000, amount: 18000.00000000  row: 0x10aee19d0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,164 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 18, percent: 60.0000, amount: 18000.00000000  row: 0x10aee19d0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,164 - logic_logger - INF
........GlAccount[18] {Update - Adjusting gl_account: total_allocated} id: 18, department_id: 11, account_number: 511380, name: roads_labor 1784919451138, total_allocated:  [0.00-->] 18000.00000000, notes: None  row: 0x10aee27d0  session: 0x10ac6a9c0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,164 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10aee2ad0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,165 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 19, percent: 40.0000, amount: 12000.00000000  row: 0x10aee2ad0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,165 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 19, percent: 40.0000, amount: 12000.00000000  row: 0x10aee2ad0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,165 - logic_logger - INF
........GlAccount[19] {Update - Adjusting gl_account: total_allocated} id: 19, department_id: 11, account_number: 511441, name: roads_equipment 1784919451144, total_allocated:  [0.00-->] 12000.00000000, notes: None  row: 0x10aee1ed0  session: 0x10ac6a9c0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,165 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 11, dept_charge_definition_id: 10, percent: 60.0000, amount: 30000.0000  row: 0x10ae69130  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,165 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 11, dept_charge_definition_id: 10, percent: 60.0000, amount: 30000.0000  row: 0x10ae69130  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,165 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 9, contractor_id: None, project_description: None, amount: 50000, total_distributed_amount:  [0-->] 30000.0000, description: Behave test charge, charge_date: None  row: 0x10af05a90  session: 0x10ac6a9c0  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,165 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae69250  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,165 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 12, dept_charge_definition_id: 11, percent: 40.0000, amount: 20000.0000  row: 0x10ae69250  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,166 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 12, dept_charge_definition_id: 11, percent: 40.0000, amount: 20000.0000  row: 0x10ae69250  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,166 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10aee3f50  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,166 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 20, percent: 70.0000, amount: 14000.00000000  row: 0x10aee3f50  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,166 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 20, percent: 70.0000, amount: 14000.00000000  row: 0x10aee3f50  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,167 - logic_logger - INF
........GlAccount[20] {Update - Adjusting gl_account: total_allocated} id: 20, department_id: 12, account_number: 511490, name: construction_labor 1784919451149, total_allocated:  [0.00-->] 14000.00000000, notes: None  row: 0x10aee3b50  session: 0x10ac6a9c0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,167 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10aee3cd0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,167 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 21, percent: 30.0000, amount: 6000.00000000  row: 0x10aee3cd0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,167 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 21, percent: 30.0000, amount: 6000.00000000  row: 0x10aee3cd0  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,167 - logic_logger - INF
........GlAccount[21] {Update - Adjusting gl_account: total_allocated} id: 21, department_id: 12, account_number: 511551, name: construction_materials 1784919451155, total_allocated:  [0.00-->] 6000.00000000, notes: None  row: 0x10aee13d0  session: 0x10ac6a9c0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,168 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 12, dept_charge_definition_id: 11, percent: 40.0000, amount: 20000.0000  row: 0x10ae69250  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,168 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 12, dept_charge_definition_id: 11, percent: 40.0000, amount: 20000.0000  row: 0x10ae69250  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,168 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 9, contractor_id: None, project_description: None, amount: 50000, total_distributed_amount:  [30000.0000-->] 50000.0000, description: Behave test charge, charge_date: None  row: 0x10af05a90  session: 0x10ac6a9c0  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,168 - logic_logger - INF
..Charge[None] {END Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 9, contractor_id: None, project_description: None, amount: 50000, total_distributed_amount: 50000.0000, description: Behave test charge, charge_date: None  row: 0x10af05a90  session: 0x10ac6a9c0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,168 - logic_logger - INF
....Project[9] {Update - Adjusting project: total_charges} id: 9, name: Test Project 1784919451129, project_funding_definition_id: 6, total_charges:  [0.00-->] 50000.00, notes: None  row: 0x10aee2450  session: 0x10ac6a9c0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,168 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10ac6a9c0)   										 - 2026-07-24 11:57:31,168 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10ac6a9c0)   										 - 2026-07-24 11:57:31,169 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Project total_charges rollup - sums charges for the project
&emsp;  Scenario: Project total_charges rollup - sums charges for the project  
&emsp;&emsp;    Given a funding setup with Roads 60% / Construction 40%  
    And Roads splits to Labor 60% / Equipment 40%  
    And Construction splits to Labor 70% / Materials 30%  
&emsp;&emsp;    When a Charge of 30000 is posted to the Project  
    And a second Charge of 20000 is posted to the same Project  
&emsp;&emsp;    Then Project total_charges is 50000  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Project total_charges rollup - sums charges for the project
```
  Charge  
    1. RowEvent Charge.identify_project_for_charge()   
    2. Derive <class 'database.models.Charge'>.total_distributed_amount as Sum(ChargeDeptAllocation.amount Where  - None)  
    3. RowEvent Charge.check_active_funding()   
  ChargeDeptAllocation  
    4. Derive <class 'database.models.ChargeDeptAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
    5. Derive <class 'database.models.ChargeDeptAllocation'>.percent as Copy(project_funding_line.percent)  
  ChargeGlAllocation  
    6. Derive <class 'database.models.ChargeGlAllocation'>.percent as Copy(dept_charge_definition_line.percent)  
    7. Derive <class 'database.models.ChargeGlAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
  GlAccount  
    8. Derive <class 'database.models.GlAccount'>.total_allocated as Sum(ChargeGlAllocation.amount Where  - None)  
  Project  
    9. Derive <class 'database.models.Project'>.total_charges as Sum(Charge.amount Where  - None)  
```
**Logic Log** in Scenario: Project total_charges rollup - sums charges for the project
```
Logic Phase:		ROW LOGIC		(session=0x10ac6a7a0) (sqlalchemy before_flush)			 - 2026-07-24 11:57:31,217 - logic_logger - INF
..Charge[None] {Insert - client} id: None, project_id: 10, contractor_id: None, project_description: None, amount: 30000, total_distributed_amount: None, description: Behave test charge, charge_date: None  row: 0x10ae93b10  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,217 - logic_logger - INF
..Charge[None] {server_defaults: total_distributed_amount } id: None, project_id: 10, contractor_id: None, project_description: None, amount: 30000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10ae93b10  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,217 - logic_logger - INF
..Charge[None] {server aggregate_defaults: total_distributed_amount } id: None, project_id: 10, contractor_id: None, project_description: None, amount: 30000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10ae93b10  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,217 - logic_logger - INF
..Charge[None] {BEGIN Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 10, contractor_id: None, project_description: None, amount: 30000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10ae93b10  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,218 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae691c0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,218 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 13, dept_charge_definition_id: 12, percent: 60.0000, amount: 18000.0000  row: 0x10ae691c0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,218 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 13, dept_charge_definition_id: 12, percent: 60.0000, amount: 18000.0000  row: 0x10ae691c0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,219 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10aca2250  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,219 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 22, percent: 60.0000, amount: 10800.00000000  row: 0x10aca2250  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,219 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 22, percent: 60.0000, amount: 10800.00000000  row: 0x10aca2250  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,219 - logic_logger - INF
........GlAccount[22] {Update - Adjusting gl_account: total_allocated} id: 22, department_id: 13, account_number: 511930, name: roads_labor 1784919451193, total_allocated:  [0.00-->] 10800.00000000, notes: None  row: 0x10af64450  session: 0x10ac6a7a0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,219 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10acf9650  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,219 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 23, percent: 40.0000, amount: 7200.00000000  row: 0x10acf9650  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,220 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 23, percent: 40.0000, amount: 7200.00000000  row: 0x10acf9650  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,220 - logic_logger - INF
........GlAccount[23] {Update - Adjusting gl_account: total_allocated} id: 23, department_id: 13, account_number: 511991, name: roads_equipment 1784919451199, total_allocated:  [0.00-->] 7200.00000000, notes: None  row: 0x10af64ad0  session: 0x10ac6a7a0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,220 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 13, dept_charge_definition_id: 12, percent: 60.0000, amount: 18000.0000  row: 0x10ae691c0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,220 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 13, dept_charge_definition_id: 12, percent: 60.0000, amount: 18000.0000  row: 0x10ae691c0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,220 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 10, contractor_id: None, project_description: None, amount: 30000, total_distributed_amount:  [0-->] 18000.0000, description: Behave test charge, charge_date: None  row: 0x10ae93b10  session: 0x10ac6a7a0  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,220 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae69370  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,220 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 14, dept_charge_definition_id: 13, percent: 40.0000, amount: 12000.0000  row: 0x10ae69370  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,221 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 14, dept_charge_definition_id: 13, percent: 40.0000, amount: 12000.0000  row: 0x10ae69370  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,221 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10acf84d0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,221 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 24, percent: 70.0000, amount: 8400.00000000  row: 0x10acf84d0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,221 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 24, percent: 70.0000, amount: 8400.00000000  row: 0x10acf84d0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,222 - logic_logger - INF
........GlAccount[24] {Update - Adjusting gl_account: total_allocated} id: 24, department_id: 14, account_number: 512040, name: construction_labor 1784919451204, total_allocated:  [0.00-->] 8400.00000000, notes: None  row: 0x10ae8b350  session: 0x10ac6a7a0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,222 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10aee1dd0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,222 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 25, percent: 30.0000, amount: 3600.00000000  row: 0x10aee1dd0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,222 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 25, percent: 30.0000, amount: 3600.00000000  row: 0x10aee1dd0  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,222 - logic_logger - INF
........GlAccount[25] {Update - Adjusting gl_account: total_allocated} id: 25, department_id: 14, account_number: 512101, name: construction_materials 1784919451210, total_allocated:  [0.00-->] 3600.00000000, notes: None  row: 0x10aee38d0  session: 0x10ac6a7a0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,223 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 14, dept_charge_definition_id: 13, percent: 40.0000, amount: 12000.0000  row: 0x10ae69370  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,223 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 14, dept_charge_definition_id: 13, percent: 40.0000, amount: 12000.0000  row: 0x10ae69370  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,223 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 10, contractor_id: None, project_description: None, amount: 30000, total_distributed_amount:  [18000.0000-->] 30000.0000, description: Behave test charge, charge_date: None  row: 0x10ae93b10  session: 0x10ac6a7a0  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,223 - logic_logger - INF
..Charge[None] {END Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 10, contractor_id: None, project_description: None, amount: 30000, total_distributed_amount: 30000.0000, description: Behave test charge, charge_date: None  row: 0x10ae93b10  session: 0x10ac6a7a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,223 - logic_logger - INF
....Project[10] {Update - Adjusting project: total_charges} id: 10, name: Test Project 1784919451185, project_funding_definition_id: 7, total_charges:  [0.00-->] 30000.00, notes: None  row: 0x10aee1e50  session: 0x10ac6a7a0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,223 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10ac6a7a0)   										 - 2026-07-24 11:57:31,223 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10ac6a7a0)   										 - 2026-07-24 11:57:31,224 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: GlAccount total_allocated rollup - sums GL allocations
&emsp;  Scenario: GlAccount total_allocated rollup - sums GL allocations  
&emsp;&emsp;    Given a funding setup with Roads 60% / Construction 40%  
    And Roads splits to Labor 60% / Equipment 40%  
    And Construction splits to Labor 70% / Materials 30%  
&emsp;&emsp;    When a Charge of 100000 is posted to the Project  
&emsp;&emsp;    Then Roads Labor GlAccount total_allocated is 36000  
    And Roads Equipment GlAccount total_allocated is 24000  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: GlAccount total_allocated rollup - sums GL allocations
```
  Charge  
    1. RowEvent Charge.identify_project_for_charge()   
    2. Derive <class 'database.models.Charge'>.total_distributed_amount as Sum(ChargeDeptAllocation.amount Where  - None)  
    3. RowEvent Charge.check_active_funding()   
  ChargeDeptAllocation  
    4. Derive <class 'database.models.ChargeDeptAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
    5. Derive <class 'database.models.ChargeDeptAllocation'>.percent as Copy(project_funding_line.percent)  
  ChargeGlAllocation  
    6. Derive <class 'database.models.ChargeGlAllocation'>.percent as Copy(dept_charge_definition_line.percent)  
    7. Derive <class 'database.models.ChargeGlAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
  GlAccount  
    8. Derive <class 'database.models.GlAccount'>.total_allocated as Sum(ChargeGlAllocation.amount Where  - None)  
  Project  
    9. Derive <class 'database.models.Project'>.total_charges as Sum(Charge.amount Where  - None)  
```
**Logic Log** in Scenario: GlAccount total_allocated rollup - sums GL allocations
```
Logic Phase:		ROW LOGIC		(session=0x10ac6ae00) (sqlalchemy before_flush)			 - 2026-07-24 11:57:31,283 - logic_logger - INF
..Charge[None] {Insert - client} id: None, project_id: 11, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: None, description: Behave test charge, charge_date: None  row: 0x10af19950  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,283 - logic_logger - INF
..Charge[None] {server_defaults: total_distributed_amount } id: None, project_id: 11, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af19950  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,283 - logic_logger - INF
..Charge[None] {server aggregate_defaults: total_distributed_amount } id: None, project_id: 11, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af19950  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,283 - logic_logger - INF
..Charge[None] {BEGIN Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 11, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af19950  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,284 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae69490  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,284 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 15, dept_charge_definition_id: 14, percent: 60.0000, amount: 60000.0000  row: 0x10ae69490  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,284 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 15, dept_charge_definition_id: 14, percent: 60.0000, amount: 60000.0000  row: 0x10ae69490  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,285 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10aee0cd0  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,285 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 26, percent: 60.0000, amount: 36000.00000000  row: 0x10aee0cd0  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,285 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 26, percent: 60.0000, amount: 36000.00000000  row: 0x10aee0cd0  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,285 - logic_logger - INF
........GlAccount[26] {Update - Adjusting gl_account: total_allocated} id: 26, department_id: 15, account_number: 512600, name: roads_labor 1784919451260, total_allocated:  [0.00-->] 36000.00000000, notes: None  row: 0x10af66550  session: 0x10ac6ae00  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,285 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10af65250  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,286 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 27, percent: 40.0000, amount: 24000.00000000  row: 0x10af65250  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,286 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 27, percent: 40.0000, amount: 24000.00000000  row: 0x10af65250  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,286 - logic_logger - INF
........GlAccount[27] {Update - Adjusting gl_account: total_allocated} id: 27, department_id: 15, account_number: 512651, name: roads_equipment 1784919451265, total_allocated:  [0.00-->] 24000.00000000, notes: None  row: 0x10af66750  session: 0x10ac6ae00  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,286 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 15, dept_charge_definition_id: 14, percent: 60.0000, amount: 60000.0000  row: 0x10ae69490  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,286 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 15, dept_charge_definition_id: 14, percent: 60.0000, amount: 60000.0000  row: 0x10ae69490  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,286 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 11, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount:  [0-->] 60000.0000, description: Behave test charge, charge_date: None  row: 0x10af19950  session: 0x10ac6ae00  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,286 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae695b0  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,287 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 16, dept_charge_definition_id: 15, percent: 40.0000, amount: 40000.0000  row: 0x10ae695b0  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,287 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 16, dept_charge_definition_id: 15, percent: 40.0000, amount: 40000.0000  row: 0x10ae695b0  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,287 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10af67550  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,287 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 28, percent: 70.0000, amount: 28000.00000000  row: 0x10af67550  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,287 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 28, percent: 70.0000, amount: 28000.00000000  row: 0x10af67550  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,288 - logic_logger - INF
........GlAccount[28] {Update - Adjusting gl_account: total_allocated} id: 28, department_id: 16, account_number: 512710, name: construction_labor 1784919451271, total_allocated:  [0.00-->] 28000.00000000, notes: None  row: 0x10aee2850  session: 0x10ac6ae00  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,288 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10aee3750  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,288 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 29, percent: 30.0000, amount: 12000.00000000  row: 0x10aee3750  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,288 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 29, percent: 30.0000, amount: 12000.00000000  row: 0x10aee3750  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,288 - logic_logger - INF
........GlAccount[29] {Update - Adjusting gl_account: total_allocated} id: 29, department_id: 16, account_number: 512761, name: construction_materials 1784919451276, total_allocated:  [0.00-->] 12000.00000000, notes: None  row: 0x10ae15ed0  session: 0x10ac6ae00  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,289 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 16, dept_charge_definition_id: 15, percent: 40.0000, amount: 40000.0000  row: 0x10ae695b0  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,289 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 16, dept_charge_definition_id: 15, percent: 40.0000, amount: 40000.0000  row: 0x10ae695b0  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,289 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 11, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount:  [60000.0000-->] 100000.0000, description: Behave test charge, charge_date: None  row: 0x10af19950  session: 0x10ac6ae00  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,289 - logic_logger - INF
..Charge[None] {END Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 11, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 100000.0000, description: Behave test charge, charge_date: None  row: 0x10af19950  session: 0x10ac6ae00  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,289 - logic_logger - INF
....Project[11] {Update - Adjusting project: total_charges} id: 11, name: Test Project 1784919451251, project_funding_definition_id: 8, total_charges:  [0.00-->] 100000.00, notes: None  row: 0x10aee29d0  session: 0x10ac6ae00  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,289 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10ac6ae00)   										 - 2026-07-24 11:57:31,289 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10ac6ae00)   										 - 2026-07-24 11:57:31,290 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Charge Rejected - project funding definition not active
&emsp;  Scenario: Charge Rejected - project funding definition not active  
&emsp;&emsp;    Given a funding setup with Roads 60% / Construction 40% missing a line  
&emsp;&emsp;    When a Charge of 10000 is posted to the Project  
&emsp;&emsp;    Then Charge is rejected with inactive funding error  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Charge Rejected - project funding definition not active
```
  ProjectFundingDefinition  
    1. Derive <class 'database.models.ProjectFundingDefinition'>.is_active as Formula (1): as_expression=lambda row: 1 if row.total_percent  [...]  
    2. Derive <class 'database.models.ProjectFundingDefinition'>.total_percent as Sum(ProjectFundingLine.percent Where  - None)  
```
**Logic Log** in Scenario: Charge Rejected - project funding definition not active
```
Logic Phase:		ROW LOGIC		(session=0x10ac6b8a0) (sqlalchemy before_flush)			 - 2026-07-24 11:57:31,332 - logic_logger - INF
..ProjectFundingLine[None] {Insert - client} id: None, project_funding_definition_id: 10, department_id: 19, dept_charge_definition_id: 18, percent: 60, notes: None  row: 0x10aee15d0  session: 0x10ac6b8a0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,332 - logic_logger - INF
....ProjectFundingDefinition[10] {Update - Adjusting project_funding_definition: total_percent} id: 10, name: Test PFD 1784919451326, total_percent:  [0.0000-->] 60.0000, is_active: 0, notes: None  row: 0x10aee0350  session: 0x10ac6b8a0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,332 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10ac6b8a0)   										 - 2026-07-24 11:57:31,332 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10ac6b8a0)   										 - 2026-07-24 11:57:31,333 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Allocation percent frozen at charge time - not retroactively changed
&emsp;  Scenario: Allocation percent frozen at charge time - not retroactively changed  
&emsp;&emsp;    Given a funding setup with Roads 60% / Construction 40%  
    And Roads splits to Labor 60% / Equipment 40%  
    And Construction splits to Labor 70% / Materials 30%  
&emsp;&emsp;    When a Charge of 100000 is posted to the Project  
    And the Roads funding line percent is later changed to 90  
&emsp;&emsp;    Then the existing ChargeDeptAllocation percent for Roads is still 60  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Allocation percent frozen at charge time - not retroactively changed
```
  Charge  
    1. RowEvent Charge.identify_project_for_charge()   
    2. Derive <class 'database.models.Charge'>.total_distributed_amount as Sum(ChargeDeptAllocation.amount Where  - None)  
    3. RowEvent Charge.check_active_funding()   
  ChargeDeptAllocation  
    4. Derive <class 'database.models.ChargeDeptAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
    5. Derive <class 'database.models.ChargeDeptAllocation'>.percent as Copy(project_funding_line.percent)  
  ChargeGlAllocation  
    6. Derive <class 'database.models.ChargeGlAllocation'>.percent as Copy(dept_charge_definition_line.percent)  
    7. Derive <class 'database.models.ChargeGlAllocation'>.amount as Formula (1): as_expression=lambda row: (  
            row.charg [...]  
  GlAccount  
    8. Derive <class 'database.models.GlAccount'>.total_allocated as Sum(ChargeGlAllocation.amount Where  - None)  
  Project  
    9. Derive <class 'database.models.Project'>.total_charges as Sum(Charge.amount Where  - None)  
```
**Logic Log** in Scenario: Allocation percent frozen at charge time - not retroactively changed
```
Logic Phase:		ROW LOGIC		(session=0x10ac6bce0) (sqlalchemy before_flush)			 - 2026-07-24 11:57:31,360 - logic_logger - INF
..Charge[None] {Insert - client} id: None, project_id: 13, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: None, description: Behave test charge, charge_date: None  row: 0x10af39590  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,361 - logic_logger - INF
..Charge[None] {server_defaults: total_distributed_amount } id: None, project_id: 13, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af39590  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,361 - logic_logger - INF
..Charge[None] {server aggregate_defaults: total_distributed_amount } id: None, project_id: 13, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af39590  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,361 - logic_logger - INF
..Charge[None] {BEGIN Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 13, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 0, description: Behave test charge, charge_date: None  row: 0x10af39590  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,361 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae69760  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,361 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 19, dept_charge_definition_id: 18, percent: 60.0000, amount: 60000.0000  row: 0x10ae69760  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,362 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 19, dept_charge_definition_id: 18, percent: 60.0000, amount: 60000.0000  row: 0x10ae69760  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,362 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10ae89750  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,362 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 30, percent: 60.0000, amount: 36000.00000000  row: 0x10ae89750  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,362 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 30, percent: 60.0000, amount: 36000.00000000  row: 0x10ae89750  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,363 - logic_logger - INF
........GlAccount[30] {Update - Adjusting gl_account: total_allocated} id: 30, department_id: 19, account_number: 513370, name: roads_labor 1784919451337, total_allocated:  [0.00-->] 36000.00000000, notes: None  row: 0x10af65450  session: 0x10ac6bce0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,363 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10ae8ac50  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,363 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 31, percent: 40.0000, amount: 24000.00000000  row: 0x10ae8ac50  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,363 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 31, percent: 40.0000, amount: 24000.00000000  row: 0x10ae8ac50  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,363 - logic_logger - INF
........GlAccount[31] {Update - Adjusting gl_account: total_allocated} id: 31, department_id: 19, account_number: 513421, name: roads_equipment 1784919451342, total_allocated:  [0.00-->] 24000.00000000, notes: None  row: 0x10af64d50  session: 0x10ac6bce0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,363 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 19, dept_charge_definition_id: 18, percent: 60.0000, amount: 60000.0000  row: 0x10ae69760  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,364 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 19, dept_charge_definition_id: 18, percent: 60.0000, amount: 60000.0000  row: 0x10ae69760  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,364 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 13, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount:  [0-->] 60000.0000, description: Behave test charge, charge_date: None  row: 0x10af39590  session: 0x10ac6bce0  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,364 - logic_logger - INF
....ChargeDeptAllocation[None] {server_defaults: percent amount } id: None, charge_id: None, project_funding_line_id: None, department_id: None, dept_charge_definition_id: None, percent: 0, amount: 0  row: 0x10ae69520  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,364 - logic_logger - INF
....ChargeDeptAllocation[None] {Insert - Allocate charge to dept} id: None, charge_id: None, project_funding_line_id: None, department_id: 20, dept_charge_definition_id: 19, percent: 40.0000, amount: 40000.0000  row: 0x10ae69520  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,364 - logic_logger - INF
....ChargeDeptAllocation[None] {BEGIN Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 20, dept_charge_definition_id: 19, percent: 40.0000, amount: 40000.0000  row: 0x10ae69520  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,364 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10af67ed0  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,365 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 32, percent: 70.0000, amount: 28000.00000000  row: 0x10af67ed0  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,365 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 32, percent: 70.0000, amount: 28000.00000000  row: 0x10af67ed0  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,365 - logic_logger - INF
........GlAccount[32] {Update - Adjusting gl_account: total_allocated} id: 32, department_id: 20, account_number: 513480, name: construction_labor 1784919451348, total_allocated:  [0.00-->] 28000.00000000, notes: None  row: 0x10afc0350  session: 0x10ac6bce0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,365 - logic_logger - INF
......ChargeGlAllocation[None] {server_defaults: percent amount } id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: None, percent: 0, amount: 0  row: 0x10af67e50  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,365 - logic_logger - INF
......ChargeGlAllocation[None] {Insert - Allocate dept amount to GL account} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 33, percent: 30.0000, amount: 12000.00000000  row: 0x10af67e50  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,365 - logic_logger - INF
......ChargeGlAllocation[None] {copy_rules for role: dept_charge_definition_line - percent} id: None, charge_dept_allocation_id: None, dept_charge_definition_line_id: None, gl_account_id: 33, percent: 30.0000, amount: 12000.00000000  row: 0x10af67e50  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,366 - logic_logger - INF
........GlAccount[33] {Update - Adjusting gl_account: total_allocated} id: 33, department_id: 20, account_number: 513531, name: construction_materials 1784919451353, total_allocated:  [0.00-->] 12000.00000000, notes: None  row: 0x10afc09d0  session: 0x10ac6bce0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,366 - logic_logger - INF
....ChargeDeptAllocation[None] {END Allocate Rule, creating: ChargeGlAllocation} id: None, charge_id: None, project_funding_line_id: None, department_id: 20, dept_charge_definition_id: 19, percent: 40.0000, amount: 40000.0000  row: 0x10ae69520  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,366 - logic_logger - INF
....ChargeDeptAllocation[None] {copy_rules for role: project_funding_line - percent} id: None, charge_id: None, project_funding_line_id: None, department_id: 20, dept_charge_definition_id: 19, percent: 40.0000, amount: 40000.0000  row: 0x10ae69520  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,366 - logic_logger - INF
......Charge[None] {Adjustment logic chaining deferred for this parent (charge) - will run when the parent itself is processed this transaction} id: None, project_id: 13, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount:  [60000.0000-->] 100000.0000, description: Behave test charge, charge_date: None  row: 0x10af39590  session: 0x10ac6bce0  ins_upd_dlt: *, initial: * - 2026-07-24 11:57:31,366 - logic_logger - INF
..Charge[None] {END Allocate Rule, creating: ChargeDeptAllocation} id: None, project_id: 13, contractor_id: None, project_description: None, amount: 100000, total_distributed_amount: 100000.0000, description: Behave test charge, charge_date: None  row: 0x10af39590  session: 0x10ac6bce0  ins_upd_dlt: ins, initial: ins - 2026-07-24 11:57:31,366 - logic_logger - INF
....Project[13] {Update - Adjusting project: total_charges} id: 13, name: Test Project 1784919451328, project_funding_definition_id: 10, total_charges:  [0.00-->] 100000.00, notes: None  row: 0x10ae89550  session: 0x10ac6bce0  ins_upd_dlt: upd, initial: upd - 2026-07-24 11:57:31,366 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10ac6bce0)   										 - 2026-07-24 11:57:31,366 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10ac6bce0)   										 - 2026-07-24 11:57:31,368 - logic_logger - INF

```
</details>
  
&nbsp;&nbsp;  
/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/samples/allocate_dept_account_demo/test/api_logic_server_behave/behave_run.py completed at July 24, 2026 11:57:3  