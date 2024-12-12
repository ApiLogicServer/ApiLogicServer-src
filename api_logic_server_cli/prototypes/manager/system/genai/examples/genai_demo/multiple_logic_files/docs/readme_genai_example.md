Status: this example under construction.

Use this to explore:

1. [managing logic in your project with multiple files](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-logic-to-existing-projects)
2. Merging multiple logic files into a single project, and reflect newly introduced attributes into:
    * the data model
    * and the test data

<br/>

## Create genai_no_logic and add logic files

1. Run Config: `  - GenAI - no logic` to create project `genai_demo_no_logic`
'''
als genai  --retries=3 --project-name=genai_demo_no_logic --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt
'''

2. Acquire the logic files (natural language prompts) into in `genai_demo_no_logic/docs/logic`
'''
cp -r system/genai/examples/genai_demo/multiple_logic_files/docs/logic genai_demo_no_logic/docs
'''

3. This uses GenAI to translate Natural Language logic into logic code at `genai_demo_no_logic/logic/logic_discovery`.  It takes a few moments.

```
cd genai_demo_no_logic`
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
als genai-utils --fixup    # creates genai_demo_no_logic/docs/fixup/

cd ..   # Important!  else you get TypeError: ...
als genai --using=genai-utils_fixed --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/docs/fixup/response_fixup.json

# BUG: missing contraints rules

# or...
als genai --using=genai-utils_fixed --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/docs/fixup
```

## Test

To test, update a customer name to "x".