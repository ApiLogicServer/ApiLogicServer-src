from api.system.integration_endpoint import IntegrationEndpoint
from database import models
from database.models import Employee
from flask import request, jsonify
from sqlalchemy import Column

models.Order.Employee.label

models.Employee.LastName

class OrderB2B(IntegrationEndpoint):
    def __init__(self):
        """TODO

        Returns:
            _type_: _description_
        """
        order = super(OrderB2B, self).__init__(
            model_class=models.Order
            , alias = "order"
            # , role_name = "OrderList"
            # , join_on=models.Order.CustomerId
            , fields = [(models.Order.CustomerId, "AccountId")]
            , related = [
                (IntegrationEndpoint(model_class=models.OrderDetail
                    , alias="Items"
                    , join_on=models.OrderDetail.OrderId
                    , fields = [(models.OrderDetail.Quantity, "QuantityOrdered")]
                    , related = [
                        (IntegrationEndpoint(model_class=models.Product
                        , alias="Product"
                        , isParent = True
                        , fields = [models.Product.ProductName]
                        , lookup = "*" ) 
                        )                       
                    ]
                    )
                )
                , (IntegrationEndpoint(model_class=models.Employee
                    , alias="SalesRep"
                    , isParent = True
                    , join_on=models.Employee.Id
                    , fields = [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')]
                    , lookup = [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')] 
                    )
                )
            ]
        )

        # CustomEndpoint(model_class=models.OrderAudit, alias="orderAudit")  # sibling child
        return order
