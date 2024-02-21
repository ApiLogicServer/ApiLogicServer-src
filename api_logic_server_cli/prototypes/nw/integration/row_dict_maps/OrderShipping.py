from integration.system.RowDictMapper import RowDictMapper
from database import models
from flask import request, jsonify
from sqlalchemy import Column
from logic_bank.exec_row_logic.logic_row import LogicRow

class OrderShipping(RowDictMapper):
    
    def __init__(self, logic_row: LogicRow = None):
        """
        RowDictMapper: Declares message format advising Shipping of new Orders.

        Used in: logic/declare_logic.py -- send_order_to_shipping

        Args:
            logic_row (LogicRow): use in fields expressions (e.g., for parent reference)

        Returns:
            _type_: OrderShipping object (eg, provides row_to_dict and dict_to_row)
        """
        order = super(OrderShipping, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [models.Order.Id, (models.Order.AmountTotal, "Total"), (models.Order.OrderDate, "Order Date"), models.Order.CustomerId]
            , related = RowDictMapper(model_class=models.OrderDetail, alias="Items"
                , fields = [models.OrderDetail.OrderId, models.OrderDetail.Quantity, models.OrderDetail.Amount]
                , related = RowDictMapper(model_class=models.Product, alias="product"
                    , fields=[models.Product.ProductName, models.Product.UnitPrice, models.Product.UnitsInStock]
                    , isParent=True
                )
            )
        )

        return order
