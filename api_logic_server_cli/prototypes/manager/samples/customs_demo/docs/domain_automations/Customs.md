This system was createby by:

1. genai-logic create --project_name=customs_demo --db_url=sqlite:///samples/dbs/starter.sqlite
2. In the created project, provide these to your AI Assistant:

        a. Please load `.github/.copilot-instructions.md`.
        b. The prompt below


```text title="Customs System"
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917 
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order 
 under subsection 53(2) and paragraph 79(a) of the 
 Customs Tariff program code 25267A to calculate duties and taxes 
 including provincial sales tax or HST where applicable when 
 hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26' 
 and create runnable ui with examples from Germany, US, Japan and China" 
 this prompt created the tables in db.sqlite.
  Transactions are received as a CustomsEntry with multiple 
SurtaxLineItems, one per imported product HS code.
```