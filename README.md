[![Downloads](https://pepy.tech/badge/apilogicserver)](https://pepy.tech/project/apilogicserver)
[![Latest Version](https://img.shields.io/pypi/v/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)

&nbsp;

# TL;DR

Create an executable project (MCP-enabled API and Admin App) from a database or natural language prompt with 1 command; customize with declarative rules and Python in your IDE, containerize and deploy.

&nbsp;

<details markdown>

<summary>Video Overview (4 min)</summary>

&nbsp;

See how **Microservice Automation** creates and runs a microservice - a multi-page app, and an API. 

* Here is a microservice -- api and admin app -- **created / running in 5 seconds**

    * It would be similar for your own databases

* Then, customize in your IDE with Python and **Logic Automation:** spreadsheet-like rules

[![GenAI Automation](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/sample-ai/copilot/genai-automation-video.png)](https://www.youtube.com/watch?v=7I33Fa9Ulos "Microservice Automation")

</details>

&nbsp;

# Quickstart

If you have a supported Python (version 3.10 - 3.12), install is standard, typically:

```bash title="Install API Logic Server in a Virtual Environment"
python3 -m venv venv                 # windows: python -m venv venv
source venv/bin/activate             # windows: venv\Scripts\activate
python -m pip install ApiLogicServer
```

<br>Now, verify it's working - open the Project Manager for instructions (readme), and run the demo:

```bash title="Start Manager"
ApiLogicServer start
```

Find the [user documentation here](https://apilogicserver.github.io/Docs/).  Use this for normal installation, to create and customize API Logic Projects.

To install the ***dev*** version, [see here](https://apilogicserver.github.io/Docs/Architecture-Internals).  This installs the source of API Logic Server, so you can explore or extend it.

&nbsp;

# Welcome to API Logic Server

For Developers and their organizations seeking to **increase business agility,**

API Logic Server provides ***Microservice Automation:*** create executable projects with 1 command:

1. ***MCP-enabled API Automation:*** crud for each table, with pagination, optimistic locking, filtering and sorting, and

2. ***App Automation:*** a multi-page, multi-table Admin App.  <br>

**Customize in your IDE:** use standard tools (Python, Flask, SQLAlchemy, GitHub and Docker), plus<br>

3. ***Logic Automation:*** unique **rules - 40X** more concise multi-table derivations and constraints.

Unlike frameworks, weeks-to-months of complex development is no longer necessary.  <br>
API Logic Server provides unique automation **for instant integrations and app backends**.


&nbsp;

For more information, including install procedures, [please see the docs](https://apilogicserver.github.io/Docs/).

&nbsp;

### Making Contributions

This is an open source project.  We are open to suggestions.  Some of our ideas include:

| Component           | Provides         | Consider Adding                                                                |
|:---------------------------|:-----------------|:-------------------------------------------------------------------------------|
| 1. JSON:**API** and Swagger | API Execution    | Serverless, Kubernetes        | 
| 2. Transactional **Logic**   | Rule Enforcement | Recompute Derivations        |
| 3. This project | API Logic Project Creation | General support - see issues |
| 3. GenAI | Web version | Create projects with logic |

&nbsp; 
