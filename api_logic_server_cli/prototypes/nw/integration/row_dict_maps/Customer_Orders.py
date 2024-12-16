from integration.system.RowDictMapper import RowDictMapper
from database import models
from database.models import Employee
from flask import request, jsonify
from sqlalchemy import Column
from logic_bank.exec_row_logic.logic_row import LogicRow

class Customer_Orders(RowDictMapper):

    def __init__(self, logic_row: LogicRow = None):
        """
        RowDictMapper: Declares API format for customer with Orders.

        See: https://apilogicserver.github.io/Docs/Sample-Integration/
        
        Returns:
            _type_: customer_orders object (eg, provides row_to_dict and dict_to_row)
        """

        # mappers define fields, related data and aliases.. can be as simple as:
        customer_orders = super(Customer_Orders, self).__init__(
            model_class=models.Customer, 
            related = [ RowDictMapper( model_class=models.Order ) ]
        )

        # or more complex, for specific fields and aliases:
        customer_orders = super(Customer_Orders, self).__init__(
            model_class=models.Customer, fields = [ models.Customer.Id ],
            related = [ RowDictMapper( model_class=models.Order, fields = [ models.Order.Id, models.Order.AmountTotal ] ) ]
        )
        return customer_orders
