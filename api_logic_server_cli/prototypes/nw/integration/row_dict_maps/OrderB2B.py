from integration.system.RowDictMapper import RowDictMapper
from database import models
from database.models import Employee
from flask import request, jsonify
from sqlalchemy import Column

class OrderB2B(RowDictMapper):

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
                (RowDictMapper(model_class=models.OrderDetail
                    , alias="Items"
                    , fields = [(models.OrderDetail.Quantity, "QuantityOrdered")]
                    , related = [
                        (RowDictMapper(model_class=models.Product
                        , alias="Product"
                        , isParent = True
                        , fields = [models.Product.ProductName]
                        , lookup = "*" ) 
                        )                       
                    ]
                    )
                )
                , (RowDictMapper(model_class=models.Employee
                    , alias="SalesRep"
                    , isParent = True
                    , fields = [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')]
                    , lookup = [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')] 
                    )
                )
            ]
        )
        return order
