from integration.system.RowDictMapper import RowDictMapper
from database import models


class OrderB2BMapper(RowDictMapper):
    def __init__(self):
        """
        Order mapper: maps the partner B2B order format to Order and Item rows.

        - 'Account' looks up the Customer by name
        - 'Notes' maps to Order.notes
        - 'Items' maps to Item rows (see ItemB2BMapper)
        """
        mapper = super(OrderB2BMapper, self).__init__(
            model_class=models.Order,
            alias="Order",
            fields=[
                (models.Order.notes, "Notes"),
                # customer_id: set by the parent lookup; amount_total and CreatedOn: set by the rules
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
        """
        Item mapper: maps each partner order line to an Item row.

        - 'Name' looks up the Product by name
        - 'QuantityOrdered' maps to Item.quantity
        """
        mapper = super(ItemB2BMapper, self).__init__(
            model_class=models.Item,
            alias="Items",
            fields=[
                (models.Item.quantity, "QuantityOrdered"),
                # unit_price: copied from the Product by the rules; amount: derived by the rules
            ],
            parent_lookups=[
                (models.Product, [(models.Product.name, 'Name')])
            ],
            isParent=False
        )
        return mapper
