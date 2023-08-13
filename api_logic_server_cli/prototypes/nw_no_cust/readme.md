# Northwind Sample, without customizations

This is the _no-customizations_ version of the Northwind Sample project.  It enables you to:

1. See exactly what database introspection creates
2. Introduce customizations to explore them and their impact

To introduce customizations, use the terminal and run:

```
ApiLogicServer add-cust
```

&nbsp;&nbsp;

# API Logic Server

This project was created by API Logic Server.  Edit / extend this readme as desired.

&nbsp;&nbsp;

# Setup and Run

### Establish your Python environment
Install your projects' virtual environment
as described in [Virtual Environment](https://apilogicserver.github.io/Docs/Project-Env/). See also the `venv_setup` directory in your API Logic Project.

### For SqlServer, install `pyodbc`
Not required for docker-based projects (it's pre-installed). 
For local installs, see the [Install pyodbc](https://apilogicserver.github.io/Docs/Install-pyodbc/).

### Run
Then, start the API, either by IDE launch configurations, or by command line:
```
python api_logic_server_run.py
```

* **Open the Admin App -** [http://localhost:5656/admin-app/index.html#/Home](http://localhost:5656/admin-app/index.html#/Home)


&nbsp;&nbsp;

# Project Information

| About                    | Info                               |
|:-------------------------|:-----------------------------------|
| Created                  | creation-date                      |
| API Logic Server Version | api_logic_server_version           |
| Created in directory     | api_logic_server_project_directory |
| API Name                 | api_logic_server_api_name          |

&nbsp;&nbsp;


# Key Technologies

API Logic Server is based on the projects shown below.
Consult their documentation for important information.

### SARFS JSON:API Server

[SAFRS: Python OpenAPI & JSON:API Framework](https://github.com/thomaxxl/safrs)

SAFRS is an acronym for SqlAlchemy Flask-Restful Swagger.
The purpose of this framework is to help python developers create
a self-documenting JSON API for sqlalchemy database objects and relationships.

These objects are serialized to JSON and 
created, retrieved, updated and deleted through the JSON API.
Optionally, custom resource object methods can be exposed and invoked using JSON.

Class and method descriptions and examples can be provided
in yaml syntax in the code comments.

The description is parsed and shown in the swagger web interface.
The result is an easy-to-use
swagger/OpenAPI and JSON:API compliant API implementation.

### LogicBank

[Transaction Logic for SQLAlchemy Object Models](https://apilogicserver.github.io/Docs/Logic/)

Use Logic Bank to govern SQLAlchemy update transaction logic - 
multi-table derivations, constraints, and actions such as sending mail or messages. Logic consists of _both:_

*   **Rules - 40X** more concise using a spreadsheet-like paradigm, and

*   **Python - control and extensibility,** using standard tools and techniques

Logic Bank is based on SQLAlchemy - it handles `before_flush` events to enforce your logic.
Your logic therefore applies to any SQLAlchemy-based access - JSON:Api, Admin App, etc.


### SQLAlchemy

[Object Relational Mapping for Python](https://docs.sqlalchemy.org/en/13/).

SQLAlchemy provides Python-friendly database access for Python.

It is used by JSON:Api, Logic Bank, and the Admin App.

SQLAlchemy processing is based on Python `model` classes,
created automatically by API Logic Server from your database,
and saved in the `database` directory.



### Admin App

This generated project also contains a React Admin app:
* Multi-page - including page transitions to "drill down"
* Multi-table - master / details (with tab sheets)
* Intelligent layout - favorite fields first, predictive joins, etc
* Logic Aware - updates are monitored by business logic

&nbsp;&nbsp;

# Project Structure
This project was created with the following directory structure:

| Directory | Usage                         | Key Customization File             | Typical Customization                                                                 |
|:-------------- |:------------------------------|:-----------------------------------|:--------------------------------------------------------------------------------------|
| ```api``` | JSON:API                      | ```api/customize_api.py```         | Add new end points / services                                                         |
| ```database``` | SQLAlchemy Data Model Classes | ```database/customize_models.py``` | Add derived attributes, and relationships missing in the schema                       |
| ```logic``` | Transactional Logic           | ```logic/declare_logic.py```       | Declare multi-table derivations, constraints, and events such as send mail / messages |
| ```ui``` | Admin App                     | ```ui/admin/admin.yaml```          | Control field display - order, captions etc.                                          |

### Key Customization File - Typical Customization

In the table above, the _Key Customization Files_ are created as stubs, intended for you to add customizations that extend
the created API, Logic and Web App.  Since they are separate files, the project can be
recreated (e.g., synchronized with a revised schema), and these files can be easily copied
into the new project, without line-by-line merges.

Please see the ```nw``` sample for examples of typical customizations.
