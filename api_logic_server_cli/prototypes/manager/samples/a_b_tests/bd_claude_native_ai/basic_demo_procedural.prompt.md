Note: this is a test of native AI coding ability — please do not use ApiLogicServer, GenAI-Logic, LogicBank, or any other code-generation or business-rules/rules-engine framework. Just plain hand-written code (standard web framework + ORM of your choice).

Using basic_demo.sqlite, build a system (api + web app) that lets us enter orders.

Here's what needs to happen when someone places an order:

- For each line item on the order, look up the product's price and multiply by the quantity to get the item's amount.
- Add up the item amounts to get the order's total.
- Add the order total to the customer's balance.
- Before we let the order go through, check that the customer's balance doesn't go over their credit limit — if it would, reject the order.
