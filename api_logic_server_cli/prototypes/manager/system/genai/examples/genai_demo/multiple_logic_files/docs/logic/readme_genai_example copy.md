Use this to explore [managing logic in your project with multiple files](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-logic-to-existing-projects):

## Create genai_no_logic and add logic files
1. Run Config: `  - GenAI - no logic` to create project `genai_demo_no_logic`
*   als genai  --retries=3 --project-name=genai_demo_no_logic --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt

2. `cp -r system/genai/examples/genai_demo/multiple_logic_files/docs/logic genai_demo_no_logic/docs`
3. `cd genai_demo_no_logic`
4. `als genai-logic`

Observe that logic python files are created under `genai_demo_no_logic/logic/logic_discovery`.
To test, update a customer name to "x".

<br/>

## Fixup to account for new attributes

```
cd genai_demo_no_logic
cp -r docs genai/fixup
als genai-utils --fixup
cd ..
als genai --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/genai/docs/response_fixup.json
?? als genai --using=genai-utils_fixed --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/genai/docs/response_fixup.json
```
