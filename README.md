[![Downloads](https://pepy.tech/badge/apilogicserver)](https://pepy.tech/project/apilogicserver)
[![Latest Version](https://img.shields.io/pypi/v/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)

![Banner](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/hero-banner.png?raw=true)

&nbsp;

# Quickstart

If you have a supported Python (version 3.8-3.12), install is standard, typically:

```bash title="Install API Logic Server in a Virtual Environment"
python3 -m venv venv                 # windows: python -m venv venv
source venv/bin/activate             # windows: venv\Scripts\activate
python -m pip install ApiLogicServer
```

<br>Now, verify it's working - create and run the demo:

```bash title="Create and Run Demo"
ApiLogicServer create --project-name=sample_ai --db-url=sqlite:///sample_ai.sqlite
code sample_ai
```

Find the [user documentation here](https://apilogicserver.github.io/Docs/).  Use this for normal installation, to create and customize API Logic Projects.

To install the ***dev*** version, [see here](https://apilogicserver.github.io/Docs/Architecture-Internals).  This installs the source of API Logic Server, so you can explore or extend it.

&nbsp;

# Welcome to API Logic Server - Source

For Developers and their organizations seeking to **increase business agility,**

API Logic Server provides ***Microservice Automation:*** create executable projects with 1 command:

1. ***API Automation:*** crud for each table, with pagination, optimistic locking, filtering and sorting, and

2. ***App Automation:*** a multi-page, multi-table Admin App.  <br>

**Customize in your IDE:** use standard tools (Python, Flask, SQLAlchemy, GitHub and Docker), plus<br>

3. ***Logic Automation:*** unique **rules - 40X** more concise multi-table derivations and constraints.

Unlike frameworks, weeks-to-months of complex development is no longer necessary.  <br>
API Logic Server provides unique automation **for instant integrations and app backends**.


&nbsp;

For more information, including install procedures, [please see the docs](https://apilogicserver.github.io/Docs/).


### Making Contributions
This is an open source project.  We are open to suggestions.  Some of our ideas include:

| Component           | Provides         | Consider Adding                                                                |
|:---------------------------|:-----------------|:-------------------------------------------------------------------------------|
| 1. JSON:**API** and Swagger | API Execution    | Serverless, Kubernetes        | 
| 2. Transactional **Logic**   | Rule Enforcement | New rule types        |
| 3. This project | API Logic Project Creation | General support - see issues |


&nbsp; 


