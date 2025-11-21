"""
TEMPLATE: Probabilistic + Deterministic Rules Implementation

This template provides a clean reference implementation for AI value computation
alongside deterministic rules, using the Request Pattern with early events.

Pattern: Early event with wrapper function that returns populated request object
Version: 3.0
Date: November 20, 2025

See docs/training/probabilistic_logic.prompt for complete documentation.
"""

import database.models as models

def declare_logic():
    from logic_bank.logic_bank import Rule
    """
    Declarative rules combining deterministic and probabilistic logic.
    
    Deterministic: constraints, sums, formulas, counts
    Probabilistic: AI-driven value computation via early events
    """
    
    # Deterministic Rules
    Rule.constraint(validate=models.Customer,
        as_condition=lambda row: row.balance <= row.credit_limit,
        error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
    
    Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total,
        where=lambda row: row.date_shipped is None)
    
    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
    
    Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    
    Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)
    
    # Probabilistic Rule - Early event on Item
    Rule.early_row_event(on_class=models.Item, calling=set_item_unit_price_from_supplier)


def set_item_unit_price_from_supplier(row: models.Item, old_row: models.Item, logic_row):
    """
    Early event: Sets unit_price using AI if suppliers exist, else copy from product.
    
    Pattern:
    1. Check condition (suppliers available?)
    2. Call wrapper function
    3. Extract needed value from returned object
    """
    from logic.logic_discovery.ai_requests.supplier_selection import get_supplier_selection_from_ai
    
    if not logic_row.is_inserted():
        return
    
    product = row.product
    
    # No suppliers - use product's default price
    if product.count_suppliers == 0:
        row.unit_price = product.unit_price
        return
    
    # Product has suppliers - call wrapper
    supplier_req = get_supplier_selection_from_ai(
        product_id=row.product_id,
        item_id=row.id,
        logic_row=logic_row
    )
    
    # Extract value
    row.unit_price = supplier_req.chosen_unit_price


"""
AI HANDLER IMPLEMENTATION
Location: logic/logic_discovery/ai_requests/supplier_selection.py

This module contains:
1. declare_logic() - Registers early event on SysSupplierReq
2. select_supplier_via_ai() - AI handler that calls populate_ai_values()
3. get_supplier_selection_from_ai() - Wrapper that hides Request Pattern
"""

from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database import models
# from logic.system.populate_ai_values import populate_ai_values
#
# def declare_logic():
#     """
#     Register early event on SysSupplierReq to populate chosen_* fields via AI.
#     
#     This Request Pattern approach provides full audit trails and separation of concerns.
#     See: https://apilogicserver.github.io/Docs/Logic/#rule-patterns
#     """
#     Rule.early_row_event(on_class=models.SysSupplierReq, calling=select_supplier_via_ai)
#
# def select_supplier_via_ai(row: models.SysSupplierReq, old_row, logic_row: LogicRow):
#     """
#     Early event (called via insert from wrapper) to populate chosen_* fields via AI.
#     
#     This AI handler gets called automatically when SysSupplierReq is inserted,
#     populating AI Results: chosen_supplier_id and chosen_unit_price.
#     """
#     if not logic_row.is_inserted():
#         return
#     
#     populate_ai_values(
#         row=row,
#         logic_row=logic_row,
#         candidates='product.ProductSupplierList',
#         optimize_for='fastest reliable delivery while keeping costs reasonable',
#         fallback='min:unit_cost'
#     )
#
# def get_supplier_selection_from_ai(product_id: int, item_id: int, logic_row: LogicRow) -> models.SysSupplierReq:
#     """
#     Typically called from Item (Receiver) early event 
#     to get AI results from chosen ProductSupplier (Provider).
# 
#     See: https://apilogicserver.github.io/Docs/Logic-Using-AI/
# 
#     1. Creates SysSupplierReq and inserts it (triggering AI event that populates chosen_* fields)
#     
#     This wrapper hides Request Pattern implementation details.
#     See https://apilogicserver.github.io/Docs/Logic/#rule-patterns.
# 
#     Returns populated SysSupplierReq object with:
#     - Standard AI Audit: request, reason, created_on, fallback_used
#     - Parent Context Links: item_id, product_id
#     - AI Results: chosen_supplier_id, chosen_unit_price
#     """
#     # 1. Create request row using parent's logic_row
#     supplier_req_logic_row = logic_row.new_logic_row(models.SysSupplierReq)
#     supplier_req = supplier_req_logic_row.row
#     
#     # 2. Set parent context (FK links)
#     supplier_req.product_id = product_id
#     supplier_req.item_id = item_id
#     
#     # 3. Insert triggers early event which populates AI values
#     supplier_req_logic_row.insert(reason="AI supplier selection request")
#     
#     # 4. Log filled request object for visibility (use request's logic_row to show proper row details)
#     supplier_req_logic_row.log(f"AI Results from filled request")
#     
#     # 5. Return populated object (chosen_* fields now set by AI)
#     return supplier_req


"""
KEY PATTERNS SUMMARY

1. EARLY EVENT PATTERN
   - Register on receiver: Rule.early_row_event(on_class=models.Item, ...)
   - Ensures AI executes before other rules
   - Event calls wrapper, extracts values

2. WRAPPER FUNCTION
   - Hides Request Pattern complexity
   - Takes simple parameters: product_id, item_id, logic_row
   - Returns populated request object

3. REQUEST PATTERN
   - Create: logic_row.new_logic_row(models.SysXxxReq)
   - Access: req = req_logic_row.row
   - Context: req.product_id = product_id
   - Trigger: req_logic_row.insert(reason="...")
   - Return: return req

4. VALUE EXTRACTION
   - Caller extracts what it needs
   - Single value: row.unit_price = req.chosen_unit_price
   - Multiple values: Extract multiple fields from same object

5. AUTO-DISCOVERY
   - logic_discovery/ scanned recursively
   - ai_requests/ subdirectory auto-discovered
   - Each module's declare_logic() called automatically
"""
