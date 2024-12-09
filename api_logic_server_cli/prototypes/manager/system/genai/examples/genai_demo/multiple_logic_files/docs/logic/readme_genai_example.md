Status: this example under construction.

Use this to explore [managing logic in your project with multiple files](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-logic-to-existing-projects)

## Create genai_no_logic and add logic files
1. Run Config: `  - GenAI - no logic` to create project `genai_demo_no_logic`
2. `cp -r system/genai/examples/genai_demo/multiple_logic_files/docs/logic genai_demo_no_logic/docs`
    * This simulates the process of declaring your logic files,
    providing the files in `genai_demo_no_logic/docs/logic`
3. `cd genai_demo_no_logic`
4. `als genai-logic`
    * This uses GenAI to translate Natural Language logic into logic code
    * Results are at: genai_demo_no_logic/logic/logic_discovery

It takes a few moments.  

<br/>

## Fixup to account for new attributes

The project is not yet runnable, since: 
* the logic refers to attributes not in the data model / database
* the test data is incomplete and incorrect.

To address, use the `genai-utils --fixup` utility, then rebuild the project:

```
cd genai_demo_no_logic
als genai-utils --fixup
# creates genai_demo_no_logic/docs/response_fixup.json
cd ..
als genai --using=genai-utils_fixed --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/docs/response_fixup.json
```

## Test

To test, update a customer name to "x".