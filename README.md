[![Downloads](https://pepy.tech/badge/apilogicserver)](https://pepy.tech/project/apilogicserver)
[![Latest Version](https://img.shields.io/pypi/v/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)

![Banner](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/hero-banner.png?raw=true)

&nbsp;
---

Find the [documentation here](https://apilogicserver.github.io/Docs/).

&nbsp;

# Welcome to API Logic Server - Source

For Developers and their organizations seeking to **increase business agility,**

API Logic Server provides ***Microservice Automation:*** create executable projects with 1 command:

1. ***API Automation:*** crud for each table, with pagination, optimistic locking, filtering and sorting, and

2.  ***App Automation:*** a multi-page, multi-table Admin App.  <br>

**Customize in your IDE:** use standard tools (Python, Flask, SQLAlchemy, GitHub and Docker), plus<br>

3. ***Logic Automation:*** unique **rules - 40X** more concise multi-table derivations and constraints.

Unlike frameworks, weeks-to-months of complex development is no longer necessary.  <br>
API Logic Server provides unique automation **for instant integrations and app backends**.


&nbsp;

# Instantly Create and Run

![quick tour](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/nutshell/gif.gif?raw=true)


&nbsp;

### Making Contributions
This is an open source project.  We are open to suggestions.  Some of our ideas include:

| Component           | Provides         | Consider Adding                                                                |
|:---------------------------|:-----------------|:-------------------------------------------------------------------------------|
| 1. JSON:**API** and Swagger | API Execution    | Serverless, Kubernetes        | 
| 2. Transactional **Logic**   | Rule Enforcement | New rule types        |
| 3. This project | API Logic Project Creation | General support - see issues |


To get started, please see  the [Architecture.](https://apilogicserver.github.io/Docs/Architecture-Internals/)

&nbsp; 


[^1]:
    See the [FAQ for Low Code](FAQ-Low-Code)

### Change Log

02/13/2024 - 10.02.04: kafka_producer.send_kafka_message, sample md fixes, docker ENV, pg authdb

02/07/2024 - 10.02.00: BugFix[38]: foreign-key/getter collision

01/31/2024 - 10.01.28: LogicBank fix, sample-ai, better rules example

01/15/2024 - 10.01.18: Cleanup, logic reminder, nw tutorial fixes

01/08/2024 - 10.01.07: Default Interpreter for VS Code, Allocation fix, F5 note fix, #als signposts

01/03/2024 - 10.01.00: Quoted col names, Default Interpreter for VS Code

12/21/2023 - 10.00.01: Fix < Python 3.11

12/19/2023 - 10.00.00: Kafka pub/sub, Data Type Fixes

12/06/2023 - 09.06.00: Oracle Thick Client, Safrs 3.1.1, Integration Sample, No rule sql logging, curl Post

11/19/2023 - 09.05.14: ApiLogicServer curl, optional project_name arg on add-auth, add-db, rebuild

11/12/2023 - 09.05.08: multi-db bug fix (24)

11/07/2023 - 09.05.07: Basic-demo: simplify customization process

11/05/2023 - 09.05.06: Basic-demo enhancements, bug fixes (22, 23)

10/31/2023 - 09.05.00: Enhanced Security (global filter, permissions), Logic (Insert Parent)

09/29/2023 - 09.04.00: Enhanced devops automation (sqlite, MySql, Postgres)

09/08/2023 - 09.03.04: AI Driven Automation (preview)

09/08/2023 - 09.03.00: Oracle support

09/08/2023 - 09.02.23: Fix Issue 16 - Incorrect admin.yml when table name <> class name

08/22/2023 - 09.02.18: Devops container/compose, Multi-arch dockers, add-auth with db_url, auth docker dbs

07/04/2023 - 09.01.00: SQLAlchemy 2 typed-relns/attrs, Docker: Python 3.11.4 & odbc18

06/22/2023 - 09.00.00: Optimistic Locking, safrs 310 / SQLAlchemy 2.0.15

05/07/2023 - 08.04.00: safrs 3.0.4, tutorial demo notes, rm cli/docs, move pythonanywhere

05/01/2023 - 08.03.06: allocation sample

04/29/2023 - 08.03.03: restore missing debug info for open database failures

04/26/2023 - 08.03.00: virt attrs (Issue 56), safrs 3.0.2, LogicBank 1.8.4, project readme updates

04/13/2023 - 08.02.00: integratedConsole, logic logging (66), table relns fix (65)

03/23/2023 - 08.01.15: table filters, cloud debug additions, issue 59, 62-4

02/15/2023 - 08.00.01: Declarative Authorization and Authentication

01/05/2023 - 07.00.00: Multi-db, sqlite test dbs, tests run, security prototype, env config

11/22/2022 - 06.03.06: Image, Chkbox, Dialects, run.sh, SQL/Server url change, stop endpoint, Chinook Sqlite

10/02/2022 - 06.02.00: Option infer_primary_key, Oct1 SRA (issue 49), cleanup db/api setup, restore postgres dvr

09/15/2022 - 06.01.00: Multi-app Projects

08/28/2022 - 06.00.01: Admin App show_when, cascade add. Simplify Codespaces swagger url & use default config

06/12/2022 - 05.02.22: No pyodbc by default, model customizations simplified, better logging

05/04/2022 - 05.02.03: alembic for database migrations, admin-merge.yaml

04/27/2022 - 05.01.02: copy_children, with support for nesting (children and grandchildren, etc.)

03/27/2022 - 05.00.06: Introducing [Behave test framework](https://apilogicserver.github.io/Docs/Logic-Tutorial/), LogicBank bugfix

12/26/2021 - 04.00.05: Introducing the Admin app, with Readme Tutorial

