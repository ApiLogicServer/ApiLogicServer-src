from integration.system.RowDictMapper import RowDictMapper
from database import models


class OrderB2BMapper(RowDictMapper):
    def __init__(self):
        """Order mapper: maps external partner OrderB2B JSON payload (Account, Notes, Items) to Order and Item rows."""
        mapper = super(OrderB2BMapper, self).__init__(
            model_class=models.Order,
            alias="Order",
            fields=[
                (models.Order.notes, "Notes"),
            ],
            parent_lookups=[
                (models.Customer, [(models.Customer.name, 'Account')])
            ],
            related=[
                ItemB2BMapper()
            ]
        )
        return mapper


class ItemB2BMapper(RowDictMapper):
    def __init__(self):
        """Item mapper: maps external partner Items array elements (Name, QuantityOrdered) to Item rows with Product lookup."""
        mapper = super(ItemB2BMapper, self).__init__(
            model_class=models.Item,
            alias="Items",
            fields=[
                (models.Item.quantity, "QuantityOrdered"),
            ],
            parent_lookups=[
                (models.Product, [(models.Product.name, 'Name')])
            ],
            isParent=False
        )
        return mapper

