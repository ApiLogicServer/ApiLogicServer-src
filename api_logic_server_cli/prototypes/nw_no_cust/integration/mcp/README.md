Model Context Protocol is a way for Chat agents to discover and call external servers, be they databases, APIs, file systems, etc, and call their services.  And, for multiple such servers to be choreographed in a chain of calls.

This is to explore:

| Explore                                                           | Status |
| ----------------------------------------------------------------- | ------ |
| ALS Svr can be used as an MCP server                              | Runs   |
| Nat Lang access from ChatBot (eg, ChatGPT) to (tunnelled) ALS Svr | Fails  |
| ALS Svr can be choroegraphed by LLM (1 in a chain of calls)       | ?      |


![Intro diagram](resources/images/MCP%20Overview.png)

For more information:

* [see here](https://modelcontextprotocol.io/introduction)
* [and here](https://apilogicserver.github.io/Docs/Integration-MCP/)
* [and here](https://www.youtube.com/watch?v=1bUy-1hGZpI&t=72s)

> Status: Technology Exploration

## ChatGPT testing

In the Manager, open `samples/nw_sample_nocust`, and explore `integration/mcp`.  This has been successfully used to invoke the server, including with authorization.

This is just an initial experiment, without automation such as creation of openAI version 3 from version 2.  Many substantive issues need to be addressed, including but not limited to security, update, etc.

We welcome participation in this exploration.  Please contact us via [discord](https://discord.gg/HcGxbBsgRF){:target="_blank" rel="noopener"}.

Local testing:
1. Run `integration/mcp/3_executor_test_agent.py`


&nbsp;

## Access via ChatGPT

### Tunnel to local host with ngrok

Requires the web version, which in turn requires tunnel to local host such as [ngrok](https://ngrok.com/downloads/mac-os?tab=download), then

```
ngrok config add-authtoken <obtain from https://dashboard.ngrok.com/get-started/setup/macos>
```

then
```
ngrok http 5656
```

and note the url like: `https://mcp_url_eg_bca3_2601.ngrok-free.app -> http://localhost:5656`

We'll call it `mcp_url`.


### Configure ChatGPT


replacing url to create prompt (??)        d:
{
  "tool": "json-api",
  "method": "GET",
  "url": "https://mcp_url.ngrok.io/api/Customer",
  "query_params": {
    "filter[Country]": "Germany",
    "page[limit]": 2
  },
  "headers": {
    "Accept": "application/vnd.api+json"
  },
  "expected_output": "List of customer records"
}

### Create the MCP in Web ChatGPT

Explore > Create

An early try:

```prompt
You are an AI Planner that builds MCP tool_context blocks to call a JSON:API server.

Use this information:
- Base URL: [insert your ngrok URL]
- API conforms to JSON:API standard (application/vnd.api+json).
- Key resources: Customer, Order, Product.

Example Goal:
"List all customers from Germany, limited to 2 results."

Expected MCP tool_context output:

{
  "tool": "json-api",
  "method": "GET",
  "url": "mcp_url/api/Customer",
  "query_params": {
    "filter[Country]": "Germany",
    "page[limit]": 2
  },
  "headers": {
    "Accept": "application/vnd.api+json"
  },
  "expected_output": "List of customer records"
}
```

Later, did this:

```prompt
You are an AI Planner + Executor for a live JSON:API server.

When a user gives you a natural language goal (e.g., “list customers from Germany”), you:
	•	Identify the resource (Customer, Order, Product).
	•	Map filters (e.g., Country=Germany).
	•	Construct a JSON:API call to the live endpoint (through a function called fetch_resource).
	•	Execute the live API call through the function.
	•	Format and display the results neatly.

Base URL:
https://mcp_url.ngrok-free.app/api/

The API follows JSON:API standards (application/vnd.api+json).
```



online:

{
  "tool": "json-api",
  "method": "GET",
  "url": "https://mcp_url.ngrok-free.app/api/Customer",
  "query_params": {
    "filter[Country]": "Germany",
    "page[limit]": 2
  },
  "headers": {
    "Accept": "application/vnd.api+json"
  },
  "expected_output": "List of customer records"
}

