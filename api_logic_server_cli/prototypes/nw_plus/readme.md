# Purpose

This app is an investigation of using Custom Resources to create a new message-based demo:

1. API - partner posts B2B Order (existing add_order API, or better a new Custom API) to NW
2. NW Order logic uses Custom Resources to format message representing the new Order, and sends with Kafka to Accounting.
    * This may be new functionality on CustomResource
3. Accounting (new sample app) listens on kafka, and stores the message which updates <whatever> using logic

&nbsp;

# Setup: Create Project

To generate this app, *either:*

1. Use Dev IDE, Run Config `Create servers/ApiLogicProject (new IDE) -- nw+` (it's near the top, under *2*), *or*
2. Use Preview Build
    * `python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ApiLogicServer==9.5.10`
    * Then, create as usual

```
ApiLogicServer create --project_name=nw_plus --db_url=nw+
```

&nbsp;

The `db_url` causes the system to

1. Create normal nw (rules etc)
2. Include the CustomResource from `api_logic_server_cli/model_migrator`
3. Overlay `api_logic_server_cli/prototypes/nw_plus/api/customize_api.py`
    * This brings in `api_logic_server_cli/prototypes/nw_plus/api/customize_api.py`, which is a sample custom resource from the CustomResource code comments

&nbsp;

# Test `CustomAPI/Customer`

Test using the new support for curl:

1. Establish the `venv`, as usual
2. F5 to run, as usual
3. Execute the sample `CustomAPI/Customer` resource:

```bash
ApiLogicServer login --user=admin --password=p
ApiLogicServer curl 'http://localhost:5656/CustomAPI/Customer?Id=ALFKI'
ApiLogicServer curl 'http://localhost:5656/CustomAPI/Customer?Id=ALFKI&Limit=1'
```

> Note: curl commands with '?' fail to parse in VSCode Run Launcher...

![run](images/test-with-curl.png)

&nbsp;

# Status

Minor bug inherited from comments: 

```log
AttributeError: module \'database.models\' has no attribute \'OrderAudit\'
```

&nbsp;

# curl support

This is new, useful in general and for this project.

If there are bugs, they're probably easy to fix:

1. The code is in `api_logic_server_cli/cli.py`
2. Search for *"login"*; observe it
    * Gets token from (must be running) server
    * Stores it in `api_logic_server_cli/api_logic_server_info.yaml` 
3. The `curl` command is then enabled:
    * Gets the token
    * Appends security headers to the curl command provided as arg #2

The yaml file looks like this:

```yaml
last_created_date: November 14, 2023 07:23:48
last_created_project_name: ../../../servers/ApiLogicProject
last_created_version: 09.05.09
last_login_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY5OTkzMTc3MSwianRpIjoiMzE2YmIzZGYtYTkwNC00NTI4LTg5ZTMtM2I1ODY0OGY5YjdjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNjk5OTMxNzcxLCJleHAiOjE2OTk5NDUwOTF9.xNKG4UxyNCN8-QyNNQWmAl3w3CZUVUnS2zqkZtmj59M
```