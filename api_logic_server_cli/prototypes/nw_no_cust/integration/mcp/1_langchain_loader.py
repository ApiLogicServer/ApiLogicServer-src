"""
==========================================================================================
 LangChain OpenAPI Loader – JSON:API Planner Tool (1_langchain_loader.py)
==========================================================================================

Alert:
------
This does not work - hours of import version madness.


Purpose:
--------
This script loads an OpenAPI 3.0 specification (e.g., nw_swagger_3.yaml) using LangChain's
OpenAPI tools to dynamically generate a structured LangChain Tool. It can be used as a 
building block in an AI system that automatically interprets natural language goals and 
calls API endpoints by mapping them to OpenAPI operations.

How It's Used:
--------------
- Reads the OpenAPI schema and extracts available endpoints.
- Instantiates a tool for a specific operation (e.g., getCustomer).
- Allows GPT agents or scripts to call the tool using structured input.
- Typically used in multi-agent or planner + executor systems (e.g., AutoGen, LangGraph).
- It is *not* required to run integration/mcp/3_executor_test_agent.py 

Limitations:
------------
- This script does not itself parse natural language input.
- The operation_id must be known and match one in the OpenAPI spec.
- Requires LangChain and OpenAPI tool support installed.

Dependencies:
-------------
- langchain
- openapi-spec-validator

Recommended Next Step:
----------------------
Use this in conjunction with a GPT planner that:
1. Converts natural language into structured intent.
2. Selects the correct operation_id.
3. Provides parameters as expected by the OpenAPI operation.

"""

from langchain.tools.openapi.utils.openapi_utils import OpenAPISpec
from langchain.tools.openapi.tool import OpenAPITool

# Load your OpenAPI spec
spec = OpenAPISpec.from_file("resources/nw_swagger_3.yaml")
spec = OpenAPISpec.from_file("resources/nw_swagger_2.yaml")

# Create LangChain tool from a specific endpoint
customer_tool = OpenAPITool.from_openapi_spec(
    spec=spec,
    operation_id="getCustomer",  # use actual operationId from your spec
    verbose=True
)

# Run a test call
result = customer_tool.run({
    "filter[Country]": "USA",
    "page[limit]": 3
})
print(result)
