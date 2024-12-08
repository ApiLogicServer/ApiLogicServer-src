Use this to explore [managing logic in your project with multiple files](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-logic-to-existing-projects):

1. Run Config: `  - GenAI - no logic` to create project `genai_demo_no_logic`
2. `cp -r system/genai/examples/genai_demo/multiple_logic_files/docs/logic genai_demo_no_logic/docs`
3. `cd genai_demo_no_logic`
4. `als genai-logic`

Observe that logic python files are created under `genai_demo_no_logic/logic/logic_discovery`.
To test, update a customer name to "x".