from integration.system.RowDictMapper import RowDictMapper
from database import models


class OrderB2BMapper(RowDictMapper):
    def __init__(self):
        """
        Order mapper: maps the partner B2B order (Account, Notes, Items) to Order and its Items -
        Account is looked up as Customer.name; amounts are derived by the Check Credit rules.
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
        """
        Item mapper: maps each partner item - Name is looked up as Product.name, QuantityOrdered is Item.quantity;
        unit_price and amount are derived by the Check Credit rules.
        """
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
