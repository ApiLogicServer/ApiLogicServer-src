This is internal informatin for als developers.

We have many demos: northwind, genai, sample_ai, basic_demo, tutorial.

Some should probably be deleted.

| Demo                                                                   | td:dr                                    | Iterations                                 | manager | tests         | database                                                                                             |
| ---------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------ | ------- | ------------- | ---------------------------------------------------------------------------------------------------- |
| [**NW**](https://apilogicserver.github.io/Docs/Tutorial/)              | - customizations<br>- larger project     |                                            |         |               | database/nw-gold.sqlite                                                                              |
| **genai_demo**                                                         | - WebGenAI                               | codespaces??<br>add-auth                   | y       | y<br>add-cust | prototypes/manager/system/genai/examples/genai_demo/genai_demo.response_example                      |
| **basic_demo**                                                         | 1. Instant<br>2. Logic <br>3. Python     | 1. add-cust<br>2. add-auth <br>3. add-cust | y       |               | starts as basic_demo, then adds enail, created_on, carbon_neutral<br>tests/test_databases/basic_demo/basic_demo.sql -> database/basic_demo.sqlit |
| [**sample_ai**](https://apilogicserver.github.io/Docs/Sample-AI/)      | genai_demo using CoPilot<br>funky copies |                                            |         |               | prototypes/sample_ai/database/chatgpt/sample_ai_items.sqlite<br>todo: check readme -  rebuild-from-database --project_name=./ --db_url=sqlite:///database/db.sqlite |
| [ai_chatgpt_agile](https://apilogicserver.github.io/Docs/Tutorial-AI/) |                                          |                                            |         |               |                                                                                                      |
| tutorial                                                               | std web -> als                           |                                            |         |               | dropped long ago                                                                                     |

Recall Fail-Safe Demo
* if genai, update models & rules in api_logic_server_cli/genai/genai.py # insert_logic_into_created_project() 

Perhaps genai_demo and basic_demo can share the same add_cust??
* readmes are created from docs project in `create_project_and_overlay_prototypes`
* genai begins with rules, has 1 add-cust (add_order B2B), and uses codespaces (since no CLI for add-cust)
        * codespaces does not run rules - WG_PROJECT is false, and the exported rules are not there.
* basic_demo has 2 add-cust (carbon_neutral and reorg)

Would be good if GenAI was same as BD after add-cust (ie, has MCP).
* maybe inject this in api_logic_server_cli/genai/genai.py # insert_logic_into_created_project()

Manager - put basic_demo readme in manager readme>
* Manager readme is processed for tl;dr -- Automation: Instant API, Admin App (enable UI dev, agile collaboration)

WebGenAI DX:

0. Convention: click the Blue Button
        * Home/Create Project
        * Home/Open App
        * Landing
        * Overview[Manager]/Open
        * Overview/GitHub
        * App Home / Develop --> GitHub
0. demo --> codespaces.  Where are instructions (what is CS, how do I load/run)?
1. Name can be any, iff created with APILOGICPROJECT_IS_GENAI_DEMO
2. Bypass duplicate discovery logic iff created with APILOGICPROJECT_IS_GENAI_DEMO
3. TODO:
        * cd project
        * als add-cust  # add customizations
        * run, and use place b2b order service - end point is not activated.

Misc:
* proper diff for .md: https://github.com/jonathanyeung/mark-sharp/blob/HEAD/user-guide.md