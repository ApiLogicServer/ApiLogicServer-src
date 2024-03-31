# Quick Start

## Create from existing database

Try the demo:

```bash
ApiLogicServer create --project-name=sample_ai --db-url=sqlite:///sample_ai.sqlite
```

Or, the tutorial (lots of code & logic samples):
```bash
ApiLogicServer create --project-name=sample_ai --db-url=sqlite:///sample_ai.sqlite
```

Then, try your own databases

* Find [database url examples here](https://apilogicserver.github.io/Docs/Database-Connectivity/)


## Create from AI

You can use Copilot chat (left menu, if extension installed) to:

1. create a model
2. paste it into a model file
3. create 

```bash
als create --project-name=copilot --from-model=models.py --db-url=sqlite
```

## Environment Variables

Check:
1. `APILOGICSERVER_AUTO_OPEN`
2. `APILOGICSERVER_VERBOSE`
