from integration.system.integration_service import IntegrationService
from database import models
from database.models import Employee
from flask import request, jsonify
from sqlalchemy import Column

models.Order.Employee.label

models.Employee.LastName

class OrderB2B(IntegrationService):

    def __init__(self):
        """
        Declares API format enabling B2B partners to POST Orders.

        Used in - api/customize_api.py -- OrderB2B

        See: https://apilogicserver.github.io/Docs/Sample-Integration/
        
        Returns:
            _type_: OrderB2B object (eg, provides row_to_dict and dict_to_row)
        """
        order = super(OrderB2B, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [(models.Order.CustomerId, "AccountId")]
            , related = [
                (IntegrationService(model_class=models.OrderDetail
                    , alias="Items"
                    , fields = [(models.OrderDetail.Quantity, "QuantityOrdered")]
                    , related = [
                        (IntegrationService(model_class=models.Product
                        , alias="Product"
                        , isParent = True
                        , fields = [models.Product.ProductName]
                        , lookup = "*" ) 
                        )                       
                    ]
                    )
                )
                , (IntegrationService(model_class=models.Employee
                    , alias="SalesRep"
                    , isParent = True
                    , fields = [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')]
                    , lookup = [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')] 
                    )
                )
            ]
        )
        return order
