from integration.system.RowDictMapper import RowDictMapper
from database import models

class OrderB2BMapper(RowDictMapper):
    def __init__(self):
        """
        B2B Order API Mapper for external partner integration.
        
        Maps external B2B format to internal Order/Item structure:
        - 'Account' field maps to Customer lookup by name
        - 'Notes' field maps directly to Order notes
        - 'Items' array with 'Name' and 'QuantityOrdered' maps to Item records
        """
        mapper = super(OrderB2BMapper, self).__init__(
            model_class=models.Order,
            alias="Order",
            fields=[
                (models.Order.notes, "Notes"),
                # customer_id will be set via parent lookup
                # amount_total will be calculated by business logic
                # CreatedOn will be set by business logic
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
        B2B Item Mapper for order line items.
        
        Maps external item format to internal Item structure:
        - 'Name' field maps to Product lookup by name
        - 'QuantityOrdered' maps to Item quantity
        """
        mapper = super(ItemB2BMapper, self).__init__(
            model_class=models.Item,
            alias="Items",
            fields=[
                (models.Item.quantity, "QuantityOrdered"),
                # unit_price will be copied from product by business logic
                # amount will be calculated by business logic (quantity * unit_price)
            ],
            parent_lookups=[
                (models.Product, [(models.Product.name, 'Name')])
            ],
            isParent=False
        )
        return mapper
