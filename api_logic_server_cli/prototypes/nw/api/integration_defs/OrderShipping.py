from api.system.integration_services import IntegrationServices
from database import models
from flask import request, jsonify
from sqlalchemy import Column

class OrderShipping(IntegrationServices):
    def __init__(self):
        order = super(OrderShipping, self).__init__(
            model_class=models.Order
            , alias = "order"
            # , role_name = "OrderList"
            # , join_on=models.Order.CustomerId
            , fields = [models.Order.Id, (models.Order.AmountTotal, "Total"), (models.Order.OrderDate, "Order Date"), models.Order.Ready]
            , related = IntegrationServices(model_class=models.OrderDetail, alias="Items"
                , join_on=models.OrderDetail.OrderId
                , fields = [models.OrderDetail.OrderId, models.OrderDetail.Quantity, models.OrderDetail.Amount]
                , related = IntegrationServices(model_class=models.Product, alias="product"
                    , join_on=models.OrderDetail.ProductId
                    , fields=[models.Product.ProductName, models.Product.UnitPrice, models.Product.UnitsInStock]
                    , isParent=True
                )
            )
        )

        # CustomEndpoint(model_class=models.OrderAudit, alias="orderAudit")  # sibling child
        return order
