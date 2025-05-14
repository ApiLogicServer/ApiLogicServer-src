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