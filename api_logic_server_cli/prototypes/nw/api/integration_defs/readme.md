# Purpose

This app illustrates using Custom Resources to create a new message-based system:

There are 2 **transaction sources:**

1. B2B partners
2. Internal UI

The **Northwind API Logic Server** provides APIs and the underlying logic for both transaction sources:
1. API - a self-serve API, here used by UI developers to build the Order Entry UI
2. Order Logic: shared over both transaction sources, this logic

    1. Enforces database integrity (checks credit, reorders products)
    2. Provides application integration services to format an order to alert shipping with a Kafka message.  Unlike APIs, messages are lost if the receiving server (Shipping) is down

The **Shipping API Logic Server** listens on kafka, and stores the message which updates <whatever> using logic

![overview](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/messages/overview.jpg?raw=true)

&nbsp;

# Setup: Create Project

To generate this app, *either:*

1. Use Dev IDE, Run Config `2 - Create servers/ApiLogicProject (new IDE)` (it's near the top), *or*
2. Use Preview Build (not currently working)
    * `python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ApiLogicServer==9.5.10`
    * Then, create as usual

```
ApiLogicServer create --project_name=ApiLogicProject --db_url=nw
```

&nbsp;

# Test `CustomAPI/Customer`

1. Establish the `venv`, as usual
2. F5 to run, as usual

&nbsp;

## Existing `add_order`

Here, the attribute names must exactly match the database / model names:

```bash
        curl -X 'POST' \
            'http://localhost:5656/api/ServicesEndPoint/add_order' \
            -H 'accept: application/vnd.api+json' \
            -H 'Content-Type: application/json' \
            -d '{
            "meta": {
                "method": "add_order",
                "args": {
                "CustomerId": "ALFKI",
                "EmployeeId": 1,
                "Freight": 10,
                "OrderDetailList": [
                    {
                    "ProductId": 1,
                    "Quantity": 1,
                    "Discount": 0
                    },
                    {
                    "ProductId": 2,
                    "Quantity": 2,
                    "Discount": 0
                    }
                ]
                }
            }
            }'
```

&nbsp;

## Verify create json from business object

1. Swagger: `ServicesEndPoint`` > `add_order`
2. Verify logic log contains **Send to Shipping:** (at end)

&nbsp;

## B2B Order

1. Swagger: `ServicesEndPoint` > `add_order_by_id`

&nbsp;

Or... 

```bash
curl -X  'POST' 'http://localhost:5656/api/ServicesEndPoint/add_order_by_id'  -H 'accept: application/vnd.api+json' -H 'Content-Type: application/json' -d '
{"order": {
            "AccountId": "ALFKI",
            "SalesRepId": 1,
            "Items": [
                {
                "ProductId": 1,
                "QuantityOrdered": 1
                },
                {
                "ProductId": 2,
                "QuantityOrdered": 2
                }
                ]
            }
}'
```

Or, use the ApiLogicServer curl

```bash
ApiLogicServer curl "'POST' 'http://localhost:5656/api/ServicesEndPoint/add_order_by_id'" --data '
{"order": {
            "AccountId": "ALFKI",
            "SalesRepId": 1,
            "Items": [
                {
                "ProductId": 1,
                "QuantityOrdered": 1
                },
                {
                "ProductId": 2,
                "QuantityOrdered": 2
                }
                ]
            }
}'
```


## With Lookup

This is a TODO item.

    """
ApiLogicServer curl "'POST' 'http://localhost:5656/api/ServicesEndPoint/add_b2b_order'" --data '
{"order": {
            "AccountId": "ALFKI",
            "SalesRep": "??",
            "Items": [
                {
                "ProductName": "Chai",
                "QuantityOrdered": 1
                },
                {
                "ProductName": "Chang",
                "QuantityOrdered": 2
                }
                ]
            }
}'
        """

&nbsp;

# Status

11/28/2003 - `add_order_by_id` runs, printing stub message for shipping

&nbsp;
