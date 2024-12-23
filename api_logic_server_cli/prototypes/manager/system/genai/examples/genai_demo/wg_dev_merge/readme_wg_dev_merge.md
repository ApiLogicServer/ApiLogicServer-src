The Diego Lo Giudice challenge: coordinate parallel dev streams
* WG_Team: new rules & attributes
    * Implicit Assumption: WG is not a day-1-only pilot... it lives for a while...
* Dev_Team: their own new rules & attributes, using either genai and/or alembic...

## Ground Rules
* No Dev_Team -> WG_Team integration (just deploy Dev_Team version, and use)
    * Dev team code cannot be integrated into WG - dependencies, libs, integration, ...
* WG_Team - serial dev (as now)
* WG_Team logic files are separate from Dev_Team (eg, using logic/discovery)
* sqlite only, for now (presume upgrade to 'some other db' is doable later)
    * Tyler, what were the issues you mentioned in sqlite that forced you to use PG?
* All Dev_Team and logic generations are finished before merge-G

## Key Idea: is 'source of truth' the WG_Results json data, or the .py files?
* Seems like it comes to what each group sees and edits:
    * Dev_Team: .py 
    * WG_Team: WG_Results json data (via Nat Lang) 
        * Are these maintained in WG db?  Seems like they'd have to be...
            * It's all the WG_Team sees.
            * And they need to be able to delete them.
            * Does this hold true over multiple iterations?
* I have verified that GenAI merges json/py data models (see below)
    * Note our big advantage is the logic merges automatically, without worrying about order.
        * That's because execution is automatically ordered by dependencies.

## Sample Projects
Base Project is GenAI_no_logic.  No rule-based attributes.

WG adds standard rules - Customer.balance etc.

Dev (wg_genai_demo_no_logic_fixed) adds Product.carbon_neutral from constraint_tests.prompt.
It was created like this (no need to do this, it's already done)
* cd project
* als genai-logic
* als genai-utils --fixup
* cd ..
* als genai --retries=-1 --project-name=genai_demo_no_logic_fixed --using=genai_demo_no_logic --repaired-response=genai_demo_no_logic/docs/fixup/response_fixup.json


### GenAI merges json/py data models 
![successfully merged](./merged%20models.png)

## Status - 12/21

TODO / Fixup:
1. seems to lose tables (had to have rules on Order etc)
2. fix prompt so it does not try to do rules eg in DDL

TODO / Import
1. See #2 above.  Item stuff like def __repr__(self)...
    * To get around, 

To do:
* add test data
* pull in wg rules
* add this to the wg_test suite

## Usage

```bash
cd system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed
als genai-utils --import-genai --using=../wg_demo_no_logic_fixed
```

It may fail
* fix `system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/docs/import/create_db_models.py`
* make sure to get initial system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/database/models.py (eg, make a copy before 1st test)
* vs. 'system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/docs/import/create_db_models.sqlite'
* vs. 'sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/docs/import/create_db_models.sqlite'

* use the restart option
```bash
cd system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed
als genai-utils --import-genai --using=../wg_demo_no_logic_fixed --import-restart
```

