Model Context Protocol is a way for:

- LLMs to choreograph multiple MCP servers in a chain of calls.  MCPs support shared contexts and goals, enabling the LLM to use the result from 1 call to determine whether the goals has been reached, or which service is appropriate to call next.
- Chat agents to *discover* and *call* external servers, be they databases, APIs, file systems, etc.  MCPs support shared contexts and goals, enabling the LLM

For tech background, see Appendix 2.

This is to explore:

| Explore                                                        | Status                                                                                      |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| ALS Access via MCP                                             | Runs                                                                                        |
| Nat Lang ALS Access from simple driver                         | Runs (simple query from test driver using `openai.ChatCompletion.create`)                   |
| Nat Lang ALS Access using OpenAI Plugin                        | Ran simple ChatGPT query                                                                    |
| Nat Lang ALS Access from LangChain                             | Blocked: import version issues                                                              |
| Nat Lang access from Chat (eg, ChatGPT) to (tunnelled) ALS Svr | Blocked - See Appendix 1<br>* MCP unable to pre-register resource schemas inside its system |
| ALS Svr can be choroegraphed by LLM (1 in a chain of calls)    | TBD                                                                                         |
|                                                                |                                                                                             |

A value prop might be summarized: *instantly mcp-fy your legacy DB, including critical business logic and security*.

&nbsp;

## Status: Technology Exploration

This is an initial experiment, without automation.  Many substantive issues need to be addressed, including but not limited to security, update, etc.

We welcome participation in this exploration.  Please contact us via [discord](https://discord.gg/HcGxbBsgRF).

This exploration is changing rapidly.  For updates, replace `integration/mcp` from [integration/msp](https://github.com/ApiLogicServer/ApiLogicServer-src/tree/main/api_logic_server_cli/prototypes/nw_no_cust/integration/mcp){:target="_blank" rel="noopener"}.

&nbsp;

## ALS Access via MCP 

There are 2 projects we have used for testing:

1. **NW:** In the Manager, open `samples/nw_sample_nocust`, and explore `integration/mcp`.  This has been successfully used to invoke the server, including with authorization.
2. **GenAI_DEMO:** preferred, since has update - from Dev Source, run run config: `Create blt/genai_demo_ as IS_GENAI_DEMO`
    1. Copy 
    2. In the target `genai_demo-` project: 

```
cp -R ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/genai_demo_ ~/dev/ApiLogicServer/ApiLogicServer-dev/servers

cp -R ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw_no_cust/integration ~/dev/ApiLogicServer/ApiLogicServer-dev/servers/genai_demo_

cp ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw_no_cust/api/api_discovery/openapi.py ~/dev/ApiLogicServer/ApiLogicServer-dev/servers/genai_demo_/api/api_discovery/openapi.py

cp ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw_no_cust/config/default.env ~/dev/ApiLogicServer/ApiLogicServer-dev/servers/genai_demo_/config/default.env
```

Local testing:

1. Run `integration/mcp/3_executor_test_agent.py`

&nbsp;

## Access ALS with Nat Lang Query

The goal is *Nat Lang access from Chat*.  We begin with *Nat Lang ALS Access from simple driver.*

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

Fix API Keys and URLS, then run `natlang_to_api.py` (gateway not required).  Observe json result.

&nbsp;

### Nat Lang ALS Access using OpenAI Plugin

Please see `integration/openai_plugin`.

&nbsp;

### Nat Lang ALS Access from LangChain (not working)

Blocked on many import / version issues.  See `1_langchain_loader.py`.

&nbsp;

#### Create the MCP in Web ChatGPT

In the web GPT: 

Explore > Create > load mcp from `https://tunnel_url.ngrok-free.app/mcp.json`

You can use this to test Nat Lang queries, tho it fails to notice the /api suffix.

But this does not _run_ Nat Lang queries, since GPT is not enabled for http.  That requires yet another bridge in `api/api_discovery/openapi.py` (fetch_resource) -- coded, not tested.

&nbsp;

#### Proxy for strict JSON:API

Run `integration/msp/resources/proxy_server.py`.  

This runs on port 6000 - use that for ngrok:

```
ngrok http 6000
```

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

We currently create swagger 2 doc.  Many tools expect swagger 3.  We might use tools like Swagger Editor or APIMatic Transformer for conversion.

ChatGPT/MCP had difficulty with the api response not being *strict JSONPI*.  There's a jsonapi validator somewhere to verify the results are according to the jsonapi json schema.  We experimented with a proxy for translation.

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

### MCP

![Intro diagram](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/MCP_Arch.png?raw=true)

For more information:

- [see MCP Introduction](https://modelcontextprotocol.io/introduction)
- [and here](https://apilogicserver.github.io/Docs/Integration-MCP/)
- [and here](https://www.youtube.com/watch?v=1bUy-1hGZpI&t=72s)
- and this [N8N link](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/?utm_source=n8n_app&utm_medium=node_settings_modal-credential_link&utm_campaign=%40n8n%2Fn8n-nodes-langchain.mcpTriggerlangchain.mcpTriggerlangchain.mcpTrigger)
- and this [python sdk](https://github.com/modelcontextprotocol/python-sdk)
- 