from integration.system.integration_service import IntegrationService
from database import models
from flask import request, jsonify
from sqlalchemy import Column

class OrderShipping(IntegrationService):
    
    def __init__(self):
        order = super(OrderShipping, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [models.Order.Id, (models.Order.AmountTotal, "Total"), (models.Order.OrderDate, "Order Date"), models.Order.Ready]
            , related = IntegrationService(model_class=models.OrderDetail, alias="Items"
                , fields = [models.OrderDetail.OrderId, models.OrderDetail.Quantity, models.OrderDetail.Amount]
                , related = IntegrationService(model_class=models.Product, alias="product"
                    , fields=[models.Product.ProductName, models.Product.UnitPrice, models.Product.UnitsInStock]
                    , isParent=True
                )
            )
        )

        return order
