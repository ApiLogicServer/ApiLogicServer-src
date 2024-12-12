Status: this example under construction.  
It should work (build and run), but 
the resultant project combines the rules into `declare_logic.py` -- 
they should be under `logic/discovery`.

Use this to explore:

1. [managing logic in your project with multiple files](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-logic-to-existing-projects)
2. Merging multiple logic files into a single project, and reflect newly introduced attributes into:
    * the data model
    * and the test data

<br/>

## Create genai_no_logic and add logic files

1. Create the `genai_demo_no_logic` project
```
als genai  --retries=3 --project-name=genai_demo_no_logic --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt
```
<br/>

2. Acquire the logic files into in `genai_demo_no_logic/docs/logic`
```
cp -r system/genai/examples/genai_demo/multiple_logic_files/docs/logic genai_demo_no_logic/docs
```

The `/logic` files are natural language prompts - `credit_check.prompt` and `constraint_tests`.
 
> Observe this logic introduces new attributes: `customer.balance, product.carbon_neutral`

<br/>

3. Use `genai-logic` to translate Natural Language logic into logic code at `genai_demo_no_logic/logic/logic_discovery` (it takes a few moments):

```
cd genai_demo_no_logic
als genai-logic
```

<br/>

## Fixup to account for new attributes

The project is not yet runnable, since: 
* the logic refers to attributes not in the data model / database
* the test data is incomplete and incorrect.

To address, use the `genai-utils --fixup` utility, then rebuild the project:

```
cd genai_demo_no_logic
als genai-utils --fixup    

# Creates genai_demo_no_logic/docs/fixup/ -- verify:
#   2_models.response contains customer.balance, product.carbon_neutral
#   3_rules.response contains all logic


cd ..   # This cd is important!  (else you get TypeError: ...)
als genai --using=genai-utils_fixed --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/docs/fixup/response_fixup.json

# or, --repaired-response now supports a directory of data model / rule models:
als genai --using=genai-utils_fixed --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/docs/fixup
```

## Test

To test, open and start `genai_demo_no_logic_fixed`, and use the Admin app to update a customer name to "x".  This should trigger a constraint message.