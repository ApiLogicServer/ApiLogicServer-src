"""
Check Credit Use Case - Business Logic Rules

Natural Language Requirements:
1. The Customer's balance is less than the credit limit
2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
3. The Order's amount_total is the sum of the Item amount
4. The Item amount is the quantity * unit_price
5. The Product count_suppliers is the sum of the Product Suppliers
6. Use AI to Set Item field unit_price by finding the optimal Product Supplier
   based on cost, lead time, and world conditions

version: 3.0
date: February 5, 2026
source: docs/training/probabilistic_logic.md (AI Rules)
    
    # Rule 4: Item amount = quantity * unit_price
    Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    
    # Rule 5: Product count_suppliers = count of ProductSuppliers
    Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)
    
    # Rule 1: Customer balance <= credit_limit (constraint)
    Rule.constraint(validate=models.Customer, as_condition=lambda row: row.balance <= row.credit_limit, error_msg="balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
    
    # Rule 6: AI-driven unit_price selection (early event pattern)
    Rule.early_row_event(on_class=models.Item, calling=set_item_unit_price_from_supplier)


def set_item_unit_price_from_supplier(row: models.Item, old_row: models.Item, logic_row):
    """
    Early event: Sets unit_price using AI if suppliers exist, else uses fallback.
    
    Fires on insert AND when product_id changes (same semantics as copy rule).
    """
    from logic.logic_discovery.place_order.ai_requests.supplier_selection import get_supplier_selection_from_ai
    
    # Skip on delete (old_row is None) - CRITICAL: Check this FIRST
    if logic_row.is_deleted():
        return
    
    # Process on insert OR when product_id changes
    if not (logic_row.is_inserted() or row.product_id != old_row.product_id):
        return
    
    product = row.product
    
    # FALLBACK LOGIC when AI shouldn't/can't run:
    # Strategy: Try reasonable default (copy from parent matching field), else fail-fast
    if product.count_suppliers == 0:
        # Reasonable default: copy from parent.unit_price (matching field name)
        if hasattr(product, 'unit_price') and product.unit_price is not None:
            logic_row.log(f"No suppliers for {product.name}, using product default price")
            row.unit_price = product.unit_price
            return
        else:
            # No obvious fallback - fail-fast with explicit TODO
            raise NotImplementedError(
                "TODO_AI_FALLBACK: Define fallback for Item.unit_price when no suppliers exist. "
                "Options: (1) Use a default constant, (2) Leave NULL if optional, "
                "(3) Raise error if required field, (4) Copy from another source"
            )
    
    # Product has suppliers - call AI wrapper
    logic_row.log(f"Product {product.name} has {product.count_suppliers} suppliers, requesting AI selection")
    supplier_req = get_supplier_selection_from_ai(
        product_id=row.product_id,
        item_id=row.id,
        logic_row=logic_row
    )
    
    # Extract AI-selected value
    row.unit_price = supplier_req.chosen_unit_price
    logic_row.log(f"Set unit_price to {row.unit_price} from AI supplier selection")
