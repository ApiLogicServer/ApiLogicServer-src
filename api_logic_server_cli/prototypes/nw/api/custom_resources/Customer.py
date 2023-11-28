from api.system.lac_endpoint import LacEndpoint
from database import models
from flask import request, jsonify
from sqlalchemy import Column

class Customer(LacEndpoint):
    def __init__(self):
        customer = super(Customer, self).__init__(
            model_class=models.Customer
            , alias="customers"
            , fields = [(models.Customer.CompanyName, "Customer Name")] 
            , children = 
                LacEndpoint(model_class=models.Order
                    , alias = "orders"
                    # , role_name = "OrderList"
                    , join_on=models.Order.CustomerId
                    , fields = [(models.Order.AmountTotal, "Total"), (models.Order.ShippedDate, "Ship Date")]
                    , children = LacEndpoint(model_class=models.OrderDetail, alias="details"
                        , join_on=models.OrderDetail.OrderId
                        , fields = [models.OrderDetail.Quantity, models.OrderDetail.Amount]
                        , children = LacEndpoint(model_class=models.Product, alias="product"
                            , join_on=models.OrderDetail.ProductId
                            , fields=[models.Product.UnitPrice, models.Product.UnitsInStock]
                            , isParent=True
                            , isCombined=False
                        )
                    )
                )
            )
        # CustomEndpoint(model_class=models.OrderAudit, alias="orderAudit")  # sibling child
        return customer
