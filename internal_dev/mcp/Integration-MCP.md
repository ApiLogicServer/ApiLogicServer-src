!!! pied-piper ":bulb: TL;DR - MCP: Enable Bus Users to use NL to create multi-service execution flows"

	MCP enables Business Users to use Natural Language to create declarative execution flows across multiple business-rule-enforced API services.  MCP is an open protocol than enables:
	
	1. **MCP Client Executors** to leverage LLMs to tranlate NL queries into multi-step execution flows called **Tool Context Blocks.**. 
	2. The MCP Client Executor executes the Tool Context block steps, making calls on the  **MCP Server Executors.**
	
		* MCP Server Executors are commonly provided via **logic-enabled JSON:APIs.**  (Note the logic is critical in maintaining integrity and security.)
	
	In some cases, you may have a database, but neither the APIs nor the logic.  GenAI-Logic API Logic Server can **mcp-ify existing databases** by:
	
	3. Creating JSON:APIs for existing databases with a single CLI command
	4. Enabling you to [declare business logic](Logic.md), which can be used via the APIs in MCP executipn flows.

 

## Architecture:

![Intro diagram](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/MCP_Arch.png?raw=true)  

1. MCP Client Executor Startup

	* Calls *wellknown* endpoint to load schema
	* This schema is similar to `docs/db.dbml` (already created by als)

2. MCP Client Executor sends Bus User ***NL query + schema*** (as prompt or tool definition) to the external LLM, here, ChatGPT (requires API Key).  LLM returns an ***MCP Tool Context*** JSON block.

	* An MCP Client Executor might be similar in concept to installed/Web ChatGPT (etc), but those *cannot* be used to access MCPs since they cannot issue http calls.  This is an internally developed app (or, perhaps an IDE tool)

		* We are using a test version: `integration/mcp/mcp_client_executor.py`
	* Tool definitions are OpenAI specific, so we are sending the schema (in each prompt)

		* Note this strongly suggests this is a **subset** of your database.  
	* This schema is derived from `docs/db.dbml` (already created by als)
 

3. MCP Client Executor iterates through the Tool Context, calling the JSON:API Endpoint that enforces business logic.

Here is a typical `https://localhost:5656/.well-known/mcp.json` response (not yet implemented):

```json
{
  "tool_type": "json-api",
  "base_url": "https://crm.company.com",
  "resources": [
    {
      "name": "Customer",
      "path": "/Customer",
      "methods": ["GET", "PATCH"],
      "fields": ["id", "name", "balance", "credit_limit"],
      "filterable": ["name", "credit_limit"],
      "example": "List customers with credit over 5000"
    }
  ]
}
```


&nbsp;

## Example: send emails for pending orders


The **basic_demo** sample enables you to create orders with business logic to check credit by using rules to roll-up item amount to orders / customers.  Setting the `date_shipped` indicates payment is received, and the customer balance is reduced.

In this example, we want a new service to:

1. Find Orders placed over 30 days ago that are not shipped
2. Send an Email encouraging prompt payment

We want to do this without troubling IT by enabling business users, while maintaining integrity.  MCP meets this need.

&nbsp;

### Setup

There are 2 projects we have used for testing:  

1. **basic_demo:** preferred, since has update - from Dev Source, run run config: `Create blt/genai_demo_ as IS_GENAI_DEMO`

2. **NW:** In the Manager, open `samples/nw_sample_nocust`, and explore `integration/mcp`. This has been successfully used to invoke the server, including with authorization.

3. Create in manager

4. Run `als add-cust` to load mcp tests

5. Run `python integration/mcp/mcp_client_executor.py`


You will need a ChatGPT APIKey.

&nbsp;
### Prompt

Here is a NL prompt using *basic_demo:*

```
List the orders created more than 30 days ago, and send a discount offer email to the customer for each one.

Respond with a JSON array of tool context blocks using:
- tool: 'json-api'
- JSON:API-compliant filtering (e.g., filter[CreatedOn][lt])
- Use {{ order.customer_id }} as a placeholder in the second step.
- Include method, url, query_params or body, headers, expected_output.
```

%nbsp;

### Sample Flow

#### MCP Client Executor

![0-MCP-client-executor](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/0-MCP-client-executor.png?raw=true) 

#### 1 - Discovery

![1-discovery-from-als](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/1-discovery-from-als.png?raw=true) 

#### 2 - Tool Context from LLM

![2-tool-context-from-LLM](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/2-tool-context-from-LLM.png?raw=true) 

#### 3 - Invoke MCP Server

![3-MCP-server response](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/3-MCP-server-response.png?raw=true) 


&nbsp;

### Status: Work In Progress

This is an initial experiment, with a number of ToDo's: real filtering, update, etc.  That said, it might be an excellent way to explore MCP.

We welcome participation in this exploration. Please contact us via [discord](https://discord.gg/HcGxbBsgRF).

This exploration is changing rapidly. For updates, replace `integration/mcp` from [integration/msp](https://github.com/ApiLogicServer/ApiLogicServer-src/tree/main/api_logic_server_cli/prototypes/nw_no_cust/integration/mcp){:target="_blank" rel="noopener"}.

&nbsp;

## Appendix 1: OpenAI Feedback

  

It appears that OpenAI is missing an enabling feature:

  

📢 Feedback: Unlocking Swagger-Based JSON:API Support in MCP

  

Summary:

  

As a developer, I have a fully functional REST API with a Swagger 2.0 spec and a proxy layer that emits strict JSON:API compliant responses.

  

However, MCP fails to parse the results due to a ValueError, seemingly because the resource type ("type": "Customer") isn't known to MCP’s internal schema registry — even though it is fully defined in my Swagger spec.

  

Details:

  

The server replies with correct Content-Type: application/vnd.api+json

  

- Every item includes "type", "id", and "attributes"

- The response includes jsonapi and links

- Swagger 2.0 spec clearly defines the resource fields

  

Issue: MCP does not ingest the Swagger schema to understand new resource types or field structures, making machine-integration impossible — despite the API being fully compliant with both Swagger and JSON:API standards.

  

Request: Please support one (or more) of the following:

  

1. Auto-ingesting Swagger (OpenAPI) specs for schema understanding

2. Allowing users to register or upload resource types

3. Relaxing strict JSON:API parsing to tolerate unfamiliar types that are structurally valid

4. Benefit: This would unlock powerful real-world MCP integrations with actual APIs — enabling developers to query their real data using natural language, with minimal friction and zero backend changes.

  

&nbsp;

  

## Appendix 2: Tech Notes

  

Info courtesy ChatGPT...

  

&nbsp;

  

### API

  

We currently create swagger 2 doc. Many tools expect swagger 3. We might use tools like Swagger Editor or APIMatic Transformer for conversion.

  

ChatGPT/MCP had difficulty with the api response not being *strict JSONPI*. There's a jsonapi validator somewhere to verify the results are according to the jsonapi json schema. We experimented with a proxy for translation.

  

### LangChain

  

What LangChain Does:

  

- Chains together prompts, tools, memory, and agents

- Helps you call APIs, query databases, or browse documents using LLMs

- Provides standard components like:

- Prompt templates

- Retrieval (RAG)

- Agents (autonomous or guided)

- Tool wrappers (e.g., OpenAPI, SQL, Python functions)

- Memory modules

  

⸻

  

💡 Example Use Case:

  

“Build an agent that answers business questions using a SQL database + OpenAI.”

  

LangChain can:

  

1. Accept a question from a user

2. Convert it into a SQL query (via GPT)

3. Run it on your database

4. Return and explain the result

  

***See:*** `integration/mcp/1_langchain_loader.py`

  

&nbsp;

  
## Appendix 3: Access ALS with Nat Lang Query


We explored several alternatives:

  

| Explore | Status |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| ALS Access via MCP | Runs |
| Nat Lang ALS Access from simple driver | Runs (simple query from test driver using `openai.ChatCompletion.create`) |
| Nat Lang ALS Access using OpenAI Plugin | Ran simple ChatGPT query |
| Nat Lang ALS Access from LangChain | Blocked: import version issues |
| Nat Lang access from Chat (eg, ChatGPT) to (tunnelled) ALS Svr | Blocked - See Appendix 1<br>* MCP unable to pre-register resource schemas inside its system |
| ALS Svr can be choroegraphed by LLM (1 in a chain of calls) | TBD |
| | |

    

This is an early attempt to use web ChatGPT for *Nat Lang access from Chat*.  We begin with *Nat Lang ALS Access from simple driver.*

  

&nbsp;

  

### Nat Lang ALS Access from simple driver

  

Here we use a simple driver to simulate Chat access.

  

&nbsp;

  

#### Tunnel to local host with ngrok

  

Requires tunnel to local host such as [ngrok](https://ngrok.com/downloads/mac-os?tab=download), then

  

```

ngrok config add-authtoken <obtain from https://dashboard.ngrok.com/get-started/setup/macos>

```

  

then

  

```

ngrok http 5656

```

  

You should see:

  

![ngrok](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/ngrok.png?raw=true)

  

and note the url like: `https://tunnel_url_eg_bca3_2601.ngrok-free.app -> http://localhost:5656`

  

We'll call it `tunnel_url`.

  

&nbsp;

  

#### Use natlang_to_api

  

```

pip install openai==0.28.1

```

  

Fix API Keys and URLS, then run `natlang_to_api.py` (gateway not required). Observe json result.

  

&nbsp;

  

### Nat Lang ALS Access using OpenAI Plugin

  

Please see `integration/openai_plugin`.

  

&nbsp;

  

### Nat Lang ALS Access from LangChain (not working)

  

Blocked on many import / version issues. See `1_langchain_loader.py`.

  

&nbsp;

  

#### Create the MCP in Web ChatGPT

  

In the web GPT:

  

Explore > Create > load mcp from `https://tunnel_url.ngrok-free.app/mcp.json`

  

You can use this to test Nat Lang queries, tho it fails to notice the /api suffix.

  

But this does not _run_ Nat Lang queries, since GPT is not enabled for http. That requires yet another bridge in `api/api_discovery/openapi.py` (fetch_resource) -- coded, not tested.

  

&nbsp;

  

#### Proxy for strict JSON:API

  

Run `integration/msp/resources/proxy_server.py`.

  

This runs on port 6000 - use that for ngrok:

  

```

ngrok http 6000

```

  
## Appendix 4: Exposing Corp DB to public MCP

TBD - investigate exposing a corp db to MCP so it can be discovered and used in a choreography.

&nbsp;
## Appendix 5: MCP Background

  

For more information:

  

- [see MCP Introduction](https://modelcontextprotocol.io/introduction)

- [and here](https://apilogicserver.github.io/Docs/Integration-MCP/)

- [and here](https://www.youtube.com/watch?v=1bUy-1hGZpI&t=72s)

- and this [N8N link](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/?utm_source=n8n_app&utm_medium=node_settings_modal-credential_link&utm_campaign=%40n8n%2Fn8n-nodes-langchain.mcpTriggerlangchain.mcpTriggerlangchain.mcpTrigger)

- and this [python sdk](https://github.com/modelcontextprotocol/python-sdk)

- and [this video](https://www.youtube.com/shorts/xdMVgZfZ1yg)