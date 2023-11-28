# Purpose

This app is an investigation of using Custom Resources to create a new message-based demo:

1. API - partner posts B2B Order (existing add_order API, or better a new Custom API) to NW
2. NW Order logic uses Custom Resources to format message representing the new Order, and sends with Kafka to Shipping.
    * This may be new functionality on CustomResource
3. Shipping (new sample app) listens on kafka, and stores the message which updates <whatever> using logic

![overview](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/messages/overview.png?raw=true)

&nbsp;

# Setup: Create Project

To generate this app, *either:*

1. Use Dev IDE, Run Config `2 - Create servers/ApiLogicProject (new IDE)` (it's near the top), *or*
2. Use Preview Build (not currently working)
    * `python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ApiLogicServer==9.5.10`
    * Then, create as usual

```
ApiLogicServer create --project_name=nw_plus --db_url=nw
```

&nbsp;

# Test `CustomAPI/Customer`

1. Establish the `venv`, as usual
2. F5 to run, as usual

&nbsp;

## Existing `add_order`

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
curl -X 'POST' \
  'http://localhost:5656/api/ServicesEndPoint/add_order_by_id' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/json' \
  -d '{
  "meta": {
    "method": "add_order_by_id",
    "args": {
      "AccountId": "ALFKI",
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
  }
}'
```

Or, use the ApiLogicServer cur

```
ApiLogicServer curl "'POST' 'http://localhost:5656/api/ServicesEndPoint/add_order_by_id'" --data '
{"meta": {
                "method": "add_order_by_id",
                "args": {
                "AccountId": "ALFKI",
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
              }
            }'
```


## With Lookup

    """
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
        """



&nbsp;

# Status


&nbsp;
