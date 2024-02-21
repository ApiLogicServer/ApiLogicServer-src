from integration.system.RowDictMapper import RowDictMapper
from database import models
from flask import request, jsonify
from sqlalchemy import Column
from logic_bank.exec_row_logic.logic_row import LogicRow

class OrderToShip(RowDictMapper):
    
    def __init__(self, logic_row: LogicRow = None):
        """
        Declares message format advising Shipping of new Orders.

        Used in: integration.kafka.kafka_consumer

        Sample Data:

         * Processing message: [{'CustomerId': 'ALFKI', 'Id': 11079, 'Items': [{'Amount': 18.0, 'OrderId': 11079, 'ProductName': 'Chai', 'Quantity': 1, 'UnitPrice': 18.0, 'UnitsInStock': 37}, {'Amount': 38.0, 'OrderId': 11079, 'ProductName': 'Chang', 'Quantity': 2, 'UnitPrice': 19.0, 'UnitsInStock': 13}], 'Order Date': '2023-12-17 19:14:10.573881', 'Total': 56.0}

        Returns:
            _type_: OrderShipping object (eg, provides dict_to_row)
        """

        order = super(OrderToShip, self).__init__(
            model_class=models.Order
            , alias = "order"
            , fields = [(models.Order.NWRefId, "Id")]
            , parent_lookups = [ ( models.Customer, [(models.Customer.Name, 'CustomerId')] ) ]
            , related = [
                RowDictMapper(model_class=models.Item
                    , alias="Items"
                    , fields = [models.Item.Quantity, models.Item.Amount]
                    , parent_lookups = [ (models.Product, [ (models.Product.Name, 'ProductName') ]) ]
                )
            ]
        )

        return order
