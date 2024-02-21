from integration.system.RowDictMapper import RowDictMapper
from database import models
from flask import request, jsonify
from sqlalchemy import Column
from logic_bank.exec_row_logic.logic_row import LogicRow

class OrderById(RowDictMapper):
    
    def __init__(self, logic_row: LogicRow = None):
        """ Illustrates poor API definition.

        Undesirable that client must provide SalesRepId and ProductId.

        * Requires they 'lookup' the IDs from the name
        * Better: use the automated lookup function: @see OrderB2B.

        Returns:
            _type_: RowDictMapper object
        """
        order = super(OrderById, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [(models.Order.CustomerId, "AccountId"), (models.Order.EmployeeId, 'SalesRepId')]
            , related = RowDictMapper(model_class=models.OrderDetail
                , alias="Items"
                , fields = [(models.OrderDetail.Quantity, "QuantityOrdered"), (models.OrderDetail.ProductId, "ProductId")]
            )
        )

        return order
