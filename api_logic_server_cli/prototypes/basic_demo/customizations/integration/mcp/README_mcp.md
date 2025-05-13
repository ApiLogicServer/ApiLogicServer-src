Model Context Protocol is a way for:

1. LLMs to ***choreograph*** multiple MCP servers in a chain of calls - an agentic workflow. MCPs support shared contexts and goals, enabling the LLM to use the result from 1 call to determine whether the goals has been reached, or which service is appropriate to call next

2. Chat agents to ***discover*** and ***call*** external servers, be they databases, APIs, file systems, etc. MCPs support shared contexts and goals, enabling the LLM

3. ***Corporate database participation*** in such flows, by making key functions available as MCP calls.

4. Chat agents to invoke ***NLM Natural Language services*** to corporate databases for improved user interfaces

For tech background, see Appendix 2.

&nbsp;

## MCP Logic Servers

GenAI-Logic / API Logic Server can instantly create an API for new / existing databases, and enable you to protect them with declarative logic and security.

We are extending this to provide for MCP access to the API: ***MCP Logic Servers***.

> A value prop might be summarized: *instantly mcp-ify your legacy DB, ***including*** critical business logic and security*.


&nbsp;


### Status: Work In Progress

This is an initial experiment, with a number of ToDo's: real filtering, update, etc.  That said, it might be an excellent way to explore MCP.

We welcome participation in this exploration. Please contact us via [discord](https://discord.gg/HcGxbBsgRF).

This exploration is changing rapidly. For updates, replace `integration/mcp` from [integration/msp](https://github.com/ApiLogicServer/ApiLogicServer-src/tree/main/api_logic_server_cli/prototypes/nw_no_cust/integration/mcp){:target="_blank" rel="noopener"}.

  

&nbsp;

  

## Internal NL Access to Corp DB via MCP / JSON:API

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

### Sample flow:

![Intro diagram](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/MCP_Arch.png?raw=true)  

1. Bus User enters a natural language query in the internal UI.

	* This might be similar to installed/Web ChatGPT (etc), but those *cannot* be used to access MCPs since they cannot issue http calls.  This is an internally developed app (or, perhaps an IDE tool)
	* We are using a test version: `integration/mcp/mcp_client_executor.py`

2. MCP Client Executor sends the query + schema (as prompt or tool definition) to the external LLM, here, ChatGPT (requires API Key).

	* Tool definitions are OpenAI specific, so we are sending the schema in each prompt.  
	* This schema is copied from `docs/db.dbml` (already created by als)
	* Note this strongly suggests this is a **subset** of your database. 

3. LLM returns an MCP Tool Context JSON block.

4. MCP Client Executor sends the Tool Context to the MCP Server Executor, an endpoint in your als project

	* See `api/api_discovery/mcp_server_executor.py`

5. MCP Server Executor calls the JSON:API Endpoint that enforces business logic.

6. JSON:API queries the Corp DB and returns the results.

  

  

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

  
## Appendix 4: MCP Background

  

For more information:

  

- [see MCP Introduction](https://modelcontextprotocol.io/introduction)

- [and here](https://apilogicserver.github.io/Docs/Integration-MCP/)

- [and here](https://www.youtube.com/watch?v=1bUy-1hGZpI&t=72s)

- and this [N8N link](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/?utm_source=n8n_app&utm_medium=node_settings_modal-credential_link&utm_campaign=%40n8n%2Fn8n-nodes-langchain.mcpTriggerlangchain.mcpTriggerlangchain.mcpTrigger)

- and this [python sdk](https://github.com/modelcontextprotocol/python-sdk)

- and [this video](https://www.youtube.com/shorts/xdMVgZfZ1yg)