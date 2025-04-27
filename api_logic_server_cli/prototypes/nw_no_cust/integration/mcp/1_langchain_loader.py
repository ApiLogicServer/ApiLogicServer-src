from langchain.tools.openapi.utils.openapi_utils import OpenAPISpec
from langchain.tools.openapi.tool import OpenAPITool

# Load your OpenAPI spec
spec = OpenAPISpec.from_file("nw_swagger_3.yaml")

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
