Status: this example under construction.

Use this to explore [managing logic in your project with multiple files](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-logic-to-existing-projects)

## Create genai_no_logic and add logic files
1. Run Config: `  - GenAI - no logic` to create project `genai_demo_no_logic`
*   als genai  --retries=3 --project-name=genai_demo_no_logic --using=system/genai/examples/genai_demo/genai_demo_no_logic.prompt

2. `cp -r system/genai/examples/genai_demo/multiple_logic_files/docs/logic genai_demo_no_logic/docs`
    * This simulates the process of declaring your logic files,
    providing the files in `genai_demo_no_logic/docs/logic`
3. `cd genai_demo_no_logic`
4. `als genai-logic`
    * This uses GenAI to translate Natural Language logic into logic code
    * Results are at: genai_demo_no_logic/logic/logic_discovery

It takes a few moments. 

Interim: maybe need to add the following to the docs/logic/*.prompt files (tho think not):

        <responseFormat>
        class Rule(BaseModel):
            name: str
            description: str
            use_case: str # specified use case or requirement name (use 'General' if missing)
            entity: str # the entity being constrained or derived
            code: str # logicbank rule code
            
        class Model(BaseModel):
            classname: str
            code: str # sqlalchemy model code
            sqlite_create: str # sqlite create table statement
            description: str
            name: str

        class TestDataRow(BaseModel):
            test_data_row_variable: str  # the Python test data row variable
            code: str  # Python code to create a test data row instance

        class WGResult(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
            # response: str # result
            models : List[Model] # list of sqlalchemy classes in the response
            rules : List[Rule] # list rule declarations
            test_data: str
            test_data_rows: List[TestDataRow]  # list of test data rows
            test_data_sqlite: str # test data as sqlite INSERT statements
            name: str  # suggest a short name for the project

        Format the response as a WGResult.

        </responseFormat>

<br/>

## Fixup to account for new attributes

The project is not yet runnable, since: 
* the logic refers to attributes not in the data model / database
* the test data is incomplete and incorrect.

To address, use the `genai-utils --fixup` utility, then rebuild the project:

Problem: test data not linking items to orders (pk not anticipated)
Cause: presumably fixup is creating request_fixup.json differently than normal creation
And: it's hard to see the request_fixup.json

```
cd genai_demo_no_logic
als genai-utils --fixup
# creates genai_demo_no_logic/docs/response_fixup.json
cd ..
als genai --using=genai-utils_fixed --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/docs/fixup/response_fixup.json

# or...
als genai-utils --submit --using=docs/fixup
cd ..
als genai --using=genai-utils_fixed --project-name=genai_demo_no_logic_fixed --retries=-1 --repaired-response=genai_demo_no_logic/docs/fixup/response.json
```

## Test

To test, update a customer name to "x".