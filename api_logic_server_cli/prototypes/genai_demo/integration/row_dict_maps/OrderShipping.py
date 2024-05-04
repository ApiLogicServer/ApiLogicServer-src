from integration.system.RowDictMapper import RowDictMapper
from database import models
from flask import request, jsonify
from sqlalchemy import Column

class OrderShipping(RowDictMapper):
    
    def __init__(self):
        """
        RowDictMapper: Declares message format advising Shipping of new Orders.

        Used in: logic/declare_logic.py -- send_order_to_shipping

        Returns:
            _type_: OrderShipping object (eg, provides row_to_dict and dict_to_row)
        """
        order = super(OrderShipping, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [models.Order.OrderID, (models.Order.AmountTotal, "Total"), (models.Order.OrderDate, "Order Date"), models.Order.CustomerID]
            , related = RowDictMapper(model_class=models.Item, alias="Items"
                , fields = [models.Item.OrderID, models.Item.Quantity, models.Item.Amount]
                , related = RowDictMapper(model_class=models.Product, alias="product"
                    , fields=[models.Product.ProductName, models.Product.UnitPrice]
                    , isParent=True
                )
            )
        )

        return order
