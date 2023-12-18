from integration.system.RowDictMapper import RowDictMapper
from database import models
from flask import request, jsonify
from sqlalchemy import Column

class OrderToShip(RowDictMapper):
    
    def __init__(self):
        """
        Declares message format advising Shipping of new Orders.

        Used in: logic/declare_logic.py -- send_order_to_shipping

        Returns:
            _type_: OrderShipping object (eg, provides row_to_dict and dict_to_row)
        """
        order = super(OrderToShip, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [(models.Order.NWRefId, "Id")]
            , related = [
                RowDictMapper (model_class=models.Customer
                    , fields = [(models.Customer.Name, 'CustomerId')]
                    , lookup = "*"
                    , isParent=True
                ),
                RowDictMapper(model_class=models.Item
                    , alias="Items"
                    , fields = [models.Item.Quantity, models.Item.Amount]
                    , related = 
                        RowDictMapper(model_class=models.Product
                            , fields=[(models.Product.Name, 'ProductName')]
                            , lookup="*"
                            , isParent=True
                        )
                )
            ]
        )

        return order
