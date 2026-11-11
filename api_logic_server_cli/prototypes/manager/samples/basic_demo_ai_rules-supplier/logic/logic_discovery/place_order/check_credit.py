"""
Requirement Check Credit:

1. The Customer's balance is less than the credit limit
2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
3. The Order's amount_total is the sum of the Item amount
4. The Item amount is the quantity * unit_price
5. The Product count suppliers is the sum of the Product Suppliers
6. Use AI to Set Item field unit_price by finding the optimal Product Supplier based on cost, lead time, and world conditions
"""
from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    Rule.constraint(validate=models.Customer, as_condition=lambda row: row.balance <= row.credit_limit, error_msg="balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
    Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
    Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)
    Rule.early_row_event(on_class=models.Item, calling=set_item_unit_price_from_supplier)


def set_item_unit_price_from_supplier(row: models.Item, old_row: models.Item, logic_row):
    """Item event: sets unit_price by asking the AI (Request Pattern, audited in SysSupplierReq) to pick the
    optimal Product Supplier; products with no suppliers get Product.unit_price. Early, so Item.amount sees it."""
    from logic.logic_discovery.place_order.ai_requests.supplier_selection import get_supplier_selection_from_ai
    if logic_row.is_deleted():
        return
    if not (logic_row.is_inserted() or row.product_id != old_row.product_id):
        return
    product = logic_row.session.get(models.Product, row.product_id)
    supplier_count = logic_row.session.query(models.ProductSupplier).filter_by(product_id=row.product_id).count()
    if supplier_count == 0:
        logic_row.log(f"No suppliers for {product.name}, using product default price")
        row.unit_price = product.unit_price
        return
    logic_row.log(f"Product {product.name} has {supplier_count} suppliers, requesting AI selection")
    supplier_req = get_supplier_selection_from_ai(product_id=row.product_id, item=row, logic_row=logic_row)
    row.unit_price = supplier_req.chosen_unit_price
