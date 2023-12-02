from api.system.integration_services import IntegrationServices
from database import models
from database.models import Employee
from flask import request, jsonify
from sqlalchemy import Column

models.Order.Employee.label

models.Employee.LastName

class OrderB2B(IntegrationServices):

    def __init__(self):
        """
        Declares format of partner APIs that Post Orders.

        See: https://apilogicserver.github.io/Docs/Sample-Integration/
        
        Returns:
            _type_: IntegrationServices object.
        """
        order = super(OrderB2B, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [(models.Order.CustomerId, "AccountId")]
            , related = [
                (IntegrationServices(model_class=models.OrderDetail
                    , alias="Items"
                    , fields = [(models.OrderDetail.Quantity, "QuantityOrdered")]
                    , related = [
                        (IntegrationServices(model_class=models.Product
                        , alias="Product"
                        , isParent = True
                        , fields = [models.Product.ProductName]
                        , lookup = "*" ) 
                        )                       
                    ]
                    )
                )
                , (IntegrationServices(model_class=models.Employee
                    , alias="SalesRep"
                    , isParent = True
                    , fields = [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')]
                    , lookup = [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')] 
                    )
                )
            ]
        )

        # CustomEndpoint(model_class=models.OrderAudit, alias="orderAudit")  # sibling child
        return order
