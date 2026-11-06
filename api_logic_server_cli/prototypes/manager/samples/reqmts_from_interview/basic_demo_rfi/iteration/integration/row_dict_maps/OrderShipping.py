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
            , fields = [models.Order.id, (models.Order.amount_total, "Total"), (models.Order.date_shipped, "Order Date"), models.Order.customer_id]
            , related = RowDictMapper(model_class=models.Item, alias="Items"
                , fields = [models.Item.order_id, models.Item.quantity, models.Item.amount]
                , related = RowDictMapper(model_class=models.Product, alias="product", role_name='product'
                    , fields=[models.Product.name, models.Product.unit_price]
                    , isParent=True
                )
            )
        )

        return order
