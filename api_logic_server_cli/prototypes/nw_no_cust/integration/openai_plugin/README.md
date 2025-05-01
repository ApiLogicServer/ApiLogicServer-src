**OpenAI plugins** are tools that extend the capabilities of ChatGPT by allowing it to access real-time data, perform actions, or connect with external services via APIs. 

Instead of being limited to its pre-trained knowledge, ChatGPT can use plugins to retrieve up-to-date information (like live weather, stock prices, or databases) or perform tasks (like booking a flight or running a query). 

The goal is to turn ChatGPT into a more useful, interactive assistant that can bridge AI language understanding with real-world actions and live data.   

>For example, in large companies, it can be remarkably hard to find corporate systems via an Intranet, and use different user interfaces.  ChatGPT can simplify finding these, and interacting with Natural Language.


This is to explore:

| Explore                                 | Status               |
| --------------------------------------- | -------------------- |
| Nat Lang ALS Access using OpenAI Plugin | Initial Test Running |
|                                         |                      |

A value prop might be summarized: *instantly expose legacy DBs to Natural Language, including critical business logic and security, to simplify user discovery and operation.*

&nbsp;


## Status: Technology Exploration

This is an initial experiment, without automation.  Many substantive issues need to be addressed, including but not limited to security, update, etc.

We welcome participation in this exploration.  Please contact us via [discord](https://discord.gg/HcGxbBsgRF).

This exploration is changing rapidly.  For updates, replace `integration/mcp` from [integration/msp](https://github.com/ApiLogicServer/ApiLogicServer-src/tree/main/api_logic_server_cli/prototypes/nw_no_cust/integration/openai_plugin)

&nbsp;

## Nat Lang ALS Access using OpenAI Plugin

Tunnel to local host with ngrok

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

and note the url like: `https://mcp_url_eg_bca3_2601.ngrok-free.app -> http://localhost:5656`

We'll call it `tunnel_url`

<br>

### Create ai_plug_in.json

Prepare `ai_plug_in.json` as shown in this directory.  It identifies the url for finding the openapi through the tunnel.

Note: both ALS and and `ai_plug_in.json` presume the swagger and api are consistent:

* swagger is at `http://localhost:5656/api/swagger.json`, 
* typical API at `http://localhost:5656/api/Category`

<br>

### Add APIs for openapi and openai_plugin

OpenAI requires a openai document, so create a custom endpoint - `api/api_discovery/openapi.py` - for swagger 3:
* swagger is at `http://localhost:5656/api/openai.json`

Note: the url needs to be the tunnelled version.

Fix servers in the `openai.json`

<br>

### Configure in ChatGPT

ChatGPT -> Create > Configure > Add Action > url

Provide the url of the openai endpoint:

https://tunnel_url.ngrok-free.app/api/openapi

which worked, but: **OpenAPI spec can have a maximum of 30 operations**, so, created a "pruned" version with just Customer: `integration/openai_plugin/nw-swagger_3.json`

fix openai version, url

retrieval worked:

![openai-plugin](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/openai-plugin/Nat%20Lang%20Query.png?raw=true)
