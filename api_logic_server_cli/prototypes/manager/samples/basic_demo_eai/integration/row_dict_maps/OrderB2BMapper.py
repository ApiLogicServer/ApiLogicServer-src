from integration.system.RowDictMapper import RowDictMapper
from database import models


class OrderB2BMapper(RowDictMapper):
    def __init__(self):
        """
        B2B Order API Mapper for external partner integration.

        Maps the partner format (message_formats/order_b2b.json) to Order / Item:
        - 'Account' maps to a Customer lookup by name
        - 'Notes' maps directly to Order.notes
        - 'Items' with 'Name' and 'QuantityOrdered' map to Item rows (Product lookup by name)
        """
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
        """B2B Item Mapper: 'Name' -> Product lookup by name, 'QuantityOrdered' -> Item.quantity."""
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
