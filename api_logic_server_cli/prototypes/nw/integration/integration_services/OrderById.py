from integration.system.integration_service import IntegrationService
from database import models
from flask import request, jsonify
from sqlalchemy import Column

class OrderById(IntegrationService):
    
    def __init__(self):
        """ Illustrates poor API definition.

        Undesirable that client must provide SalesRepId and ProductId.

        * Requires they 'lookup' the IDs from the name
        * Better: use the automated lookup function: @see OrderB2B.

        Returns:
            _type_: IntegrationServices object
        """
        order = super(OrderById, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [(models.Order.CustomerId, "AccountId"), (models.Order.EmployeeId, 'SalesRepId')]
            , related = IntegrationService(model_class=models.OrderDetail
                , alias="Items"
                , fields = [(models.OrderDetail.Quantity, "QuantityOrdered"), (models.OrderDetail.ProductId, "ProductId")]
            )
        )

        return order
