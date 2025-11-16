"""
TEMPLATE: Probabilistic + Deterministic Rules Implementation

⚠️ COMPREHENSIVE DOCUMENTATION:
For detailed documentation, see:
- docs/training/genai_logic_patterns.md - Universal framework patterns
- docs/training/probabilistic_logic_guide.md - Probabilistic logic implementation

This file provides a working code reference for copy/paste.

---

ARCHITECTURE:
- Business logic: logic/logic_discovery/[use_case].py
- Reusable AI handlers: logic/logic_discovery/ai_requests/[handler].py
- AI as value computation: Function returns computed value, audit stays in request table

KEY PATTERNS:
1. Rule.formula(calling=function) - function returns computed value
2. AI handler in ai_requests/ - reusable across use cases, self-registers
3. get_XXX_from_ai() - encapsulates Request Pattern, returns computed value
4. Auto-discovery scans logic_discovery/ recursively (including ai_requests/)

⚠️ CRITICAL IMPORTS:
- ALWAYS use: from logic_bank.logic_bank import Rule
- NEVER use: from logic_bank.rule_bank.rule_bank import RuleBank
- NEVER use: from logic_bank.extensions.rule_extensions import Rule

This is a working reference implementation showing the complete pattern.
"""

import database.models as models
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule  # ⚠️ CRITICAL: Use this import, not RuleBank
from logic.logic_discovery.ai_requests.supplier_selection import get_supplier_price_from_ai

def declare_logic():
    """
    TEMPLATE STRUCTURE:
    1. Deterministic rules (constraints, sums, formulas)
    2. Conditional formula (decides when AI runs, calls reusable AI handler)
    
    Note: AI event handler lives in ai_requests/supplier_selection.py
    """
    
    # ========================================
    # DETERMINISTIC RULES
    # ========================================
    
    # Rule 1: Constraint - Customer balance must not exceed credit_limit
    Rule.constraint(validate=models.Customer,
        as_condition=lambda row: row.balance <= row.credit_limit,
        error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
    
    # Rule 2: Customer balance is sum of unshipped Order amount_total
    Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total,
        where=lambda row: row.date_shipped is None)
    
    # Rule 3: Order amount_total is sum of Item amounts
    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
    
    # Rule 4: Item amount is quantity * unit_price
    Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    
    # Rule 5a: Count suppliers for each product
    Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)
    
    # ========================================
    # CONDITIONAL FORMULA WITH AI
    # ========================================
    
    # Rule 5b: Item unit_price - Conditional formula with AI integration
    def ItemUnitPriceFromSupplier(row: models.Item, old_row: models.Item, logic_row: LogicRow):
        """
        Conditional formula: determines Item.unit_price based on supplier availability.
        - IF Product has NO suppliers → copy from Product.unit_price
        - IF Product has suppliers → call AI to compute optimal price
        
        KEY PATTERN: Call reusable AI handler that returns computed value
        """
        if row.product.count_suppliers == 0:
            logic_row.log(f"Item - Product has no suppliers, using product.unit_price")
            return row.product.unit_price
        
        # Product has suppliers - use AI to get optimal supplier price
        return get_supplier_price_from_ai(
            row=row,
            logic_row=logic_row,
            candidates='product.ProductSupplierList',
            optimize_for='fastest reliable delivery while keeping costs reasonable',
            fallback='min:unit_cost'
        )
    
    Rule.formula(derive=models.Item.unit_price, calling=ItemUnitPriceFromSupplier)
    
"""
REUSABLE AI HANDLER PATTERN:

The AI handler lives in a separate module for reusability:
Location: logic/logic_discovery/ai_requests/supplier_selection.py

This module contains:
1. get_supplier_price_from_ai() - Function that returns computed value
2. supplier_id_from_ai() - Event handler that populates audit fields
3. declare_logic() - Self-registers the event handler

KEY ARCHITECTURE DECISIONS:
- AI handler is reusable across multiple use cases
- Encapsulates Request Pattern implementation details
- Returns computed value (price), audit details stay in request table
- Auto-discovered and registered by logic_discovery system
"""

# ========================================
# AI HANDLER REFERENCE (for completeness)
# See logic/logic_discovery/ai_requests/supplier_selection.py for implementation
# ========================================

"""
def supplier_id_from_ai(row: models.SysSupplierReq, old_row, logic_row: LogicRow):
        AI selects optimal supplier based on cost, lead time, and world conditions.
        Uses introspection-based utility to automatically discover candidate fields.
        
        Implementation uses compute_ai_value() utility which:
        - Automatically introspects candidate fields from ProductSupplier model
        - Handles API key check with graceful fallback
        - Loads test context from config/ai_test_context.yaml
        - Populates audit fields (chosen_supplier_id, chosen_unit_price, reason)
        - Returns None (audit details stored in row)
        """
        if not logic_row.is_inserted():
            return
        
        from logic.system.ai_value_computation import compute_ai_value
        
        compute_ai_value(
            row=row,
            logic_row=logic_row,
            candidates='product.ProductSupplierList',
            optimize_for='fastest reliable delivery while keeping costs reasonable',
            fallback='min:unit_cost'
        )

def declare_logic():
    # Register AI event handler
    Rule.early_row_event(
        on_class=models.SysSupplierReq,
        calling=supplier_id_from_ai
    )
"""

# ========================================
# KEY PATTERNS SUMMARY
# ========================================
"""
NEW ARCHITECTURE (Post-Refactoring):

1. SEPARATION OF CONCERNS
   - Use case logic: logic/logic_discovery/check_credit.py
   - Reusable AI handlers: logic/logic_discovery/ai_requests/supplier_selection.py
   - Framework utilities: logic/system/ai_value_computation.py

2. AI AS VALUE COMPUTATION
   - get_supplier_price_from_ai() returns the computed value (unit_price)
   - Audit details (supplier_id, reason) remain in request table
   - Encapsulates Request Pattern implementation

3. FORMULA PATTERN
   - Rule.formula(calling=function) - function returns value
   - Conditional logic: if count == 0 then default else call AI
   - Clean abstraction - formula doesn't know about Request Pattern

4. LOGICBANK TRIGGERED INSERT PATTERN (CRITICAL)
   - Use logic_row.new_logic_row(models.SysSupplierReq) to create audit record
   - Use logic_row.insert(reason="...") instead of session.add() + session.flush()
   - This avoids "Session is already flushing" error
   - Event handler fires DURING formula execution, populates fields
   - Formula returns the populated value from audit record
   
   Example from ref_impl:
   ```python
   # Inside formula - create audit record using LogicBank API
   sys_supplier_req_logic_row = logic_row.new_logic_row(models.SysSupplierReq)
   sys_supplier_req = sys_supplier_req_logic_row.row
   sys_supplier_req_logic_row.link(to_parent=logic_row)
   sys_supplier_req.product_id = row.product_id
   sys_supplier_req.item_id = row.id
   sys_supplier_req_logic_row.insert(reason="Supplier AI Request")
   return sys_supplier_req.chosen_unit_price  # Value populated by event handler
   ```
   
   See: https://apilogicserver.github.io/Docs/Logic-Use/#in-logic

4. AUTO-DISCOVERY
   - Scans logic/logic_discovery/ recursively
   - AI handlers in ai_requests/ subfolder
   - Each module has declare_logic() to self-register

5. REUSABILITY
   - Multiple use cases can call get_supplier_price_from_ai()
   - AI handler is testable independently
   - Easy to add more AI handlers (price_optimization, route_selection, etc.)
"""
