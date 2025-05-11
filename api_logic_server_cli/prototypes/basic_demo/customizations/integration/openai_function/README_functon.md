**OpenAI functions** are tools that extend the capabilities of ChatGPT by allowing it to access real-time data, perform actions, or connect with external services via APIs. .

Instead of being limited to its pre-trained knowledge, ChatGPT can use plugins to retrieve up-to-date information (like live weather, stock prices, or databases) or perform tasks (like booking a flight or running a query). 

The goal is to turn ChatGPT into a more useful, interactive assistant that can bridge AI language understanding with real-world actions and live data.   

>For example, in large companies, it can be remarkably hard to find corporate systems via an Intranet, and use different user interfaces.  ChatGPT can simplify finding these, and interacting with Natural Language.

This is to explore:

| Explore                                    | Status               |
| ------------------------------------------ | -------------------- |
| Nat Lang ALS Access using OpenAI Functions | Initial Test Running |
|                                            |                      |

A value prop might be summarized: *instantly expose legacy DBs to Natural Language, including critical business logic and security, to simplify user discovery and operation.*

<br>

## Status: Technology Exploration

This is an initial experiment, without automation.  Many substantive issues need to be addressed, including but not limited to security, update, etc.

We welcome participation in this exploration.  Please contact us via [discord](https://discord.gg/HcGxbBsgRF).

This exploration is changing rapidly.  For updates, replace `integration/mcp` from [integration/msp](https://github.com/ApiLogicServer/ApiLogicServer-src/tree/main/api_logic_server_cli/prototypes/nw_no_cust/integration/openai_plugin)

<br>

## Nat Lang ALS Access using OpenAI Plugin

Requires tunnel to local host such as [ngrok](https://ngrok.com/downloads/mac-os?tab=download), then

```
ngrok config add-authtoken <obtain from https://dashboard.ngrok.com/get-started/setup/macos>
```

then start the tunnel

```
ngrok http 5656
```

You should see:

![ngrok](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/ngrok.png?raw=true)

and note the url like: `https://42da-2601-644-4900-etc.ngrok-free.app -> http://localhost:5656`

We'll call it `tunnel_url`

Enter this into `config/default.env`

<br>

### Use GenAI_Demo

See `mcp/README_mcp.md`

<br>

### Obtain swagger_3

This has already been done using the procedure described below.

Obtain swagger 2 from API Logic Server, eg, http://localhost:5656/api/swagger.json) 

Convert to 3: https://converter.swagger.io or other.

<br>

#### Reduce to 30 Operations

Reduce down to 30 operations (genai_demo has 69).

For testing, you can copy `integration/openai_plugin/swagger_3_genai_demo.json` or `integration/openai_plugin/nw-swagger_3.json` over `integration/openai_plugin/swagger_3.json`.

This was obtained using ChatGPT with prompts like:

1. Optionally collapse GET by ID and GET collection into a single endpoint using query params
2. remove POST from relationship endpoints
3. remove delete
4. collapse relationship endpoints further

then fix the result:

1. ensure servers and paths is retained (got deleted for me), and includes https:
2. version 3.1.0

Still seeing (fix with Chat):

```
In path /Customer, method get is missing operationId; skipping
In path /Customer, method post is missing operationId; skipping
In path /Order, method get is missing operationId; skipping
In path /Order, method post is missing operationId; skipping
In path /Item, method get is missing operationId; skipping
In path /Item, method post is missing operationId; skipping
In path /Product, method get is missing operationId; skipping
In path /Product, method post is missing operationId; skipping
```

<br>

### Custom endpoint for openapi

OpenAI requires a openai document, so observe the custom endpoint - `api/api_discovery/openapi` - eg, to test locally: `http://localhost:5656/api/openai.json`

Note: the url for use in ChatGPT is the tunnelled version, from the env variable.

<br>

### Configure in ChatGPT

Then, upload it to the **Web** version of ChatGPT: 

1. Explore GPTs
2. Create
3. Configure
4. Create New Action

Provide the url of the openai endpoint:

https://tunnel_url.ngrok-free.app/api/openapi.json

<br>

### Retrieval worked:

- list customers
- list the items of order 1 with their product names

<br>

### Update: Resoved, pending verification

We also experimented with update, using `integration/openai_plugin/swagger_3.json`.

> It initially failed to load, which we repaired as noted in Appendix 2.

> It then failed to generate proper update API, evidently due to bad OpenAPI spec as noted in Appendix 3.

<br>

## Appendices

<br>

### Appendix 1: Create ai_plug_in.json

We also looked at openai plugins.  These appear to be discontinued.

Prepare `ai_plug_in.json` as shown in this directory.  Observe that it It identifies the url for finding the openapi through the tunnel.

Note: both ALS and and `ai_plug_in.json` presume the swagger and api are consistent:

- swagger is at `http://localhost:5656/api/swagger.json`, 
- typical API at `http://localhost:5656/api/Category`

Not required for function - **Settings / Beta / Plugins > Plugin install → expects the ai-plugin.json manifest URL**

This appears to be unavailable for ChatGPT 4o

<br>

### Appendix 2: Updateable openapi

It initially failed to load with

```
In context=('paths', '/Customer/{CustomerId}/', 'patch', 'requestBody', 'content', 'application/json', 'schema'), reference to unknown component Customer_inst; using empty schema

In path /Customer/{CustomerId}/, method patch, operationId UpdateCustomer_0, request body schema is not an object schema; skipping

In path /Customer/{CustomerId}/, method patch, operationId UpdateCustomer_0, skipping function due to errors
```

We requested a revised jasonapi from ChatGPT to clear these errors, which loaded.  

<br>

### Appendix 3: Invalid Data Object

 This appears to be caused by improper JSON:API openAPI spec, which caused ChatGPT to generate an improper json PATCH payload:

```python
            chatgpt_request_json = {
                        "credit_limit": 25000,
            }
            standard_request_json = {
                "data": {
                    "type": "Customer",
                    "id": "ALFKI",
                    "attributes": {
                        "name": "Alice",
                        "credit_limit": 25000,
                        "balance": 12345
                    }
                }
            }
```