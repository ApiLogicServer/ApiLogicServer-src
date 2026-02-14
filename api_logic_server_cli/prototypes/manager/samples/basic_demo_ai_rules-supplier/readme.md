---
title: basic_demo_ai_rules_supplier
notes: gold source is docs
source: docs/Sample_ai-rules
do_process_code_block_titles: True
version: 0.4, for readme 2/12/2026
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>

![example](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/copilot/AI-Rules-Audit.png?raw=true)


&nbsp;
**TL;DR - Integrated Deterministic and AI Rules**
&nbsp;
##
AI provides creativity and reasoning that businesses want... how do we provide that, *with deterministic goverance?*.  

For example - a business can continue to operate even if a tanker has blocked the Suez canal by choosing an alternate supplier, as declared in the prompt shown below.
&nbsp;

<br>

**🤖 Bootstrap Copilot by pasting the following into the chat:**
```bash title='🤖 Bootstrap Copilot by pasting the following into the chat'
Please load `.github/.copilot-instructions.md`
```

<br>

## Declare and Test

If you have not already created the project, you can create it in Manager using Copilot:

&emsp;*Create a system named basic_demo from samples/dbs/basic_demo.sqlite*.  

Then:


&nbsp;
**Paste this logic into Copilot chat (note: takes several minutes)**
&nbsp;

    On Placing Orders, Check Credit:

    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Product count suppliers is the sum of the Product Suppliers
    6. __Use AI__ to Set Item field unit_price by finding the optimal Product Supplier based on cost, lead time, and world conditions*

    Use case: App Integration

    1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.

Developers review this DSL before execution, providing a natural human-in-the-loop checkpoint.

To test:

1. Start the Server
2. Order some Egyptian Cotton Sheets (use in the Admin App, or test MCP using Copilot - paste:<br> &emsp;*On Alice's first order, include 100 Egyptian Cotton Sheets*
3. Verify the AI call - use the Admin App to view the audit trail (top of this page)

&nbsp;


## Background Concepts

### Unified Deterministic / Probablilistic Logic

Agentic systems are evolving quickly, and a clearer architectural picture is forming:

> Not AI *vs* Rules — **AI and Rules together.**

Different kinds of logic naturally call for different tools, as in this unified example:

* **Deterministic Logic** — logic that must always be correct, consistent, and governed.  
*Example:* “Customer balance must not exceed credit limit.”

* **AI Logic** — logic that benefits from exploration, adaptation, and probabilistic reasoning.  
*Example:* “Which supplier can still deliver if shipping lanes are disrupted?”

    * **Creative reasoning needs boundaries.<br>Deterministic rules supply the guardrails that keep outcomes correct, consistent, and governed.**

<br>

### Logic Architecture

**The Business Logic Agent** processes a *declarative NL requests:*

- At declaration time (e.g., in Copilot):

    * **D1:** Accepts a unified declarative NL request
    * **D2.** Uses GenAI to create
        * Rules (in Python DSL: Domain Specific Logic) for deterministic Logic
        * LLM calls for Probablistic

- At runtime, during commit

    * **R1:** DSL is executed by the Rules Engine (deterministic - no NL processing occurs)
    * **R2:** LLM calls are made to compute values (e.g., optimal supplier)
    * The rules engine ensures that R2 logic results are governed by R1 rules

![Bus-Logic-Engine](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/mcp/Bus-Logic-Agent.png?raw=true)

**AI logic become far more compelling when probabilistic intent is paired with deterministic enforcement.**

This "governable intent" model aligns with enterprise expectations —  
adaptive where helpful, reliable where essential.

**GenAI-Logic unifies probabilistic intent with deterministic enforcement in a single model**

<br>

## AI Logic Pattern: Pick Optimal

In this example, we leverage AI by providing a list of suppliers and the selection criteria (*"finding the optimal Product Supplier based on cost, lead time, and world conditions"*).  


&nbsp;
**AI Intelligent Selection From Options**
&nbsp;

     Invoke AI providing a prompt (*find optimal <criteria>*) and a *list of candidates*.
     
     AI computes the selected object.

     Here we select an optimal supplier from a list of suppliers.  Other examples:

     1. Shipping Carrier/Route Selection
     2. Dynamic Pricing/Discount Strategy
     3. Task/Resource Assignment
     4. Inventory Sourcing/Replenishment

<br>

esign

Data Model

rve:

roducts can have multiple suppliers (selection candidates)
he Audit table `SysSupplierReq` - rows are created for each AI request

sic_demo_data_model](images/basic_demo/basic_demo_data_model.png)

AI Code Generation via Context Engineering

as not *born* understanding how to use rules to solve this.  We provide extensive context engineering to automate this pattern.

an not only create the implementation, it can explain it:

I Supplier Selection Logic Flow

itiating Event**: When an Item is inserted or its `product_id` changes

ow** (see files under `logic/logic_discovery/place_order`):

*Early Row Event on OrderItem Fires** - see `./check_credit.py`

- Early row event: `set_item_unit_price_from_supplier()`
- Checks if suppliers exist for the product (fallback to Product.unit_price if no suppliers)
- Invokes wrapper

*Wrapper Function** invokes request pattern on `SysSupplierReq`

- See `./ai_requests/supplier_selection.py` -- `get_supplier_selection_from_ai()` 
- Hides complexity from rule, above, by using the *Request Pattern*:

    - Creates new `SysSupplierReq` row instance
    - Sets parent context links (`product_id`, `item_id`)
    - Inserts the request row: `SysSupplierReq` - runs its logic...
*AI Event Triggers** → Insert fires ***early_row_event:*** `select_supplier_via_ai()`

- *Request Pattern* implementation
- Get world conditions from `config/ai_test_context.yaml` (e.g., "Suez Canal blocked")
- Sends supplier data (cost, lead time, region) + world conditions to OpenAI
- AI analyzes and selects optimal supplier
- Populates `SysSupplierReq` result fields: `chosen_supplier_id`, `chosen_unit_price`, `reason`, `request`

*Wrapper Returns** → Returns populated `SysSupplierReq` row with AI results

- Caller extracts: `supplier_req.chosen_unit_price`
- Item's `unit_price` is set from this AI-chosen value

*Standard Rule Chaining provides Governance**: Formula rules automatically recalculate `Item.amount` → `Order.amount_total` → `Customer.balance`, triggering credit limit constraint check

y Pattern**: 

he ***request pattern*** is commonly used to insert a row, where logic (such as `early_row_event`) provides integration services (e.g, invoke AI, messaging, email, etc), with automatic request auditing 
he wrapper hides Request Pattern complexity - caller just gets back a populated row object with AI results (`chosen_supplier_id`, `chosen_unit_price`, `reason`) plus full audit trail.
