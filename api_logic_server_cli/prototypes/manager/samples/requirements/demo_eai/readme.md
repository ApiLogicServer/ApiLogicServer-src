<!--
  TEMP
-->

# demo-eai Temp Readme

```bash title="Establish Initial State, Execute Requirements"
# A - Create project from existing database
genai-logic create --project_name=demo_eai --db_url=sqlite:///samples/dbs/basic_demo.sqlite

# B - in created project, get these requirements
$ cp -r ../samples/requirements/demo-eai/ .

# C - create system from requirements
implement requirements docs/requirements/demo_eai
```
