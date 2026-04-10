<!--
  readme.md — GenAI-Logic / ApiLogicServer prototype base template
  Version: 3.14  (Apr 9, 2026) — in sync with .github/.copilot-instructions.md
  Propagation: copied as-is into every created project (no marker substitution)
    - Demo-named projects (basic_demo, demo_eai, …): this becomes readme_standard.md;
      a demo-specific readme is fetched from Docs repo via create_readme.py
    - Generic projects (e.g. elmo): this IS the readme
  Markers: none — no xxx-style substitution placeholders in this file
-->
# GenAI-Logic API Logic Server - Auto-Generated Microservice

**🎯 What's Automatically Created:**
- ✅ **Admin Web App** - Multi-page React app at `http://localhost:5656`
    * Customize at `ui/admin/admin.yaml`
    * You can also create a fully customizabe react app: `gail genai-add-app --app-name=react-app --vibe`
- ✅ **JSON:API Endpoints** - REST API for all database tables at `/api/*`
- ✅ **Swagger Documentation** - Interactive API docs at `/api`
- ✅ **Business Logic Engine** - Declarative rules in `logic/declare_logic.py`
- ✅ **Security Framework** - Authentication/authorization in `security/`
- ✅ **Database Models** - SQLAlchemy ORM in `database/models.py`

See readme files under api, logic and security.

**🚀 Ready to Run:** This is a complete, working system. Just press F5 or run `python api_logic_server_run.py`

<br>

---

# 🚀 Quick Start

**Bootstrap Copilot by pasting the following into the chat:**
```
Please load `.github/.copilot-instructions.md`.
```

<br>

**Microservice Automation Complete -- run to verify:** for **VSCode** projects except those downloaded from Web/GenAI:
1. `Press F5 to Run` (your venv is defaulted)  

&emsp;&emsp;&emsp;&emsp;For **other IDEs,** please follow the [Setup and Run](#1-setup-and-run) procedure, below.

<br>

> 💡 **Tip:** Create the sample app for customization examples:  
> `ApiLogicServer create --project-name=nw_sample --db_url=nw+`

&nbsp;

# Using this readme

This readme contains the following sections:


| Section                  | Info                               |
|:-------------------------|:-----------------------------------|
| [1. Setup and Run](#1-setup-and-run) | Information about API Logic Server, and setting up your venv     |
| [2. Key Customization Files](#2-key-customization-files) | Quick idea of the key files you'll alter        |
| [3. Deployment](#3-deployment) | Deploy early previews to the cloud - enable team collaboration     |
| [4. Project Requirements](#4-project-requirements)     | Options for capturing requirements |
| [5. Project Information](#5-project-information)                | Creation dates, versions          |

&nbsp;

# 1. Setup and Run

**VSCode:** press F5 (venv is pre-configured). For other IDEs, activate the venv first:
```bash
source venv/bin/activate   # windows: venv\Scripts\activate
```

## 1.1 Run

The `ApiLogicServer create` command creates Run Configurations for PyCharm and VSCode:

* For PyCharm, press Ctl-D
* For VSCode, &nbsp;press F5:

![Start Project](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/tutorial/2-apilogicproject-nutshell.png?raw=true)

As shown above:

1. Use the pre-supplied Run Configurations; use either...
    * `ApiLogicServer` to run [with security](https://apilogicserver.github.io/Docs/Security-Swagger/)
    * `ApiLogicServer - No Security` (simplifies use of Swagger)
2. Click the url in the console to start the Admin App
    * Use it to explore your **data** (shown below)
    * And your **API** (via Swagger)

![Admin App](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/ui-admin/run-admin-app.png?raw=true)


&nbsp;

# 2. Key Customization Files

Your project is ready to run, but it's likely you'll want to customize it - declare logic, new endpoints, etc.


The ___Key Customization Files___ listed in the table below are created as stubs, intended for you to add customizations that extend the created API, Logic and Web App.

* Since they are separate files, the project can be
[rebuilt](https://apilogicserver.github.io/Docs/Project-Rebuild/) (e.g., synchronized with a revised schema), preserving your customizations.

<br>

| Directory | Usage                         | Key Customization File             | Typical Customization                                                                 |
|:-------------- |:------------------------------|:-----------------------------------|:--------------------------------------------------------------------------------------|
| ```api``` | **JSON:API**<br>*Ready to Run*                    | ```api/customize_api.py```         | Add new end points / services                                                         |
| ```ui``` | **Multi-Page Admin App**<br>*Ready to Run*  | ```ui/admin/admin.yaml```          | Control field display - order, captions etc.                                          |
| ```database``` | SQLAlchemy Data Model Classes | ```database/customize_models.py``` | Add derived attributes, and relationships missing in the schema                       |
| ```logic``` | **Transactional Logic**<br>spreadsheet-like rules   | ```logic/declare_logic.py```       | Declare multi-table derivations, constraints, and Python events such as send mail / messages |
| ```security``` | Authentication, Authorization   | ```security/declare_security.py```          | Control login, role-based row access         |
| ```integration``` | EAI / Kafka Pipelines | ```integration/kafka/kafka_subscribe_discovery/readme.md``` | Start here for existing pipelines; see handler `.py` files for design, debug, and test instructions |
| ```docs/requirements``` | XRD Specs & Audit Trail | ```docs/requirements/<name>/requirements.md``` + ```ad-libs.md``` | What was spec'd and what AI decided — read before touching integration code |
| ```test``` | Behave Test Suite              | ```test/api_logic_server_behave/features```          | Declare and implement [Behave Tests](https://apilogicserver.github.io/Docs/Behave/)                                          |

<br>

Notes:

1. API Logic Server **CLI** provides commands you can use to ugrade your project, e.g., to add security.  See the next section.
2. You will observe the project is small.  That is because the app, logic and api are represented as **models:**
    * The [web app](ui/admin/admin.yaml) is a YAML file (about 150 lines - no html or JavaScript)
    * The [api](api/expose_api_models.py) is essentially 1 line per data model (table)

&nbsp;

# 3. Deployment

The `devops` directory contains several scripts for creating container images, testing them, and deploying them.

Since API Logic Server creates working software (UI, API), you can do this after creating your project, to [collaborate with your team](https://apilogicserver.github.io/Docs/DevOps-Containers-Preview/).

&nbsp;

# 4. Project Requirements

Optionally, you can **document requirements** as part of an **executable test plan**.  Test plan execution creates documentation (in markdown), including **requirements traceability** into implementation.  [See example here](test/api_logic_server_behave/reports/Behave%20Logic%20Report%20Sample.md).

&nbsp;

# 5. Project Information

This API Logic Project was created with the `ApiLogicServer create` command.
For information on Managing API Logic Projects, [click here](https://apilogicserver.github.io/Docs/Project-Structure).

| About                    | Info                               |
|:-------------------------|:-----------------------------------|
| API Logic Server Version | 15.00.38           |
| Execution begins with    | `api_logic_server_run.py`          |


&nbsp;

