from api.system.integration_endpoint import IntegrationEndpoint
from database import models
from flask import request, jsonify
from sqlalchemy import Column

class OrderById(IntegrationEndpoint):
    def __init__(self):
        """TODO

        Returns:
            _type_: _description_
        """
        order = super(OrderById, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [(models.Order.CustomerId, "AccountId"), (models.Order.EmployeeId, 'SalesRepId')]
            , related = IntegrationEndpoint(model_class=models.OrderDetail
                , alias="Items"
                , join_on=models.OrderDetail.OrderId
                , fields = [(models.OrderDetail.Quantity, "QuantityOrdered"), (models.OrderDetail.ProductId, "ProductId")]
            )
        )

        # CustomEndpoint(model_class=models.OrderAudit, alias="orderAudit")  # sibling child
        return order
