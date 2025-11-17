"""
TEMPLATE: Probabilistic + Deterministic Rules Implementation

⚠️ COMPREHENSIVE DOCUMENTATION:
For detailed documentation, see:
- docs/training/genai_logic_patterns.md - Universal framework patterns (CRITICAL IMPORT PATTERNS)
- docs/training/probabilistic_logic_guide.md - Probabilistic logic implementation

This file provides a working code reference for copy/paste.

version: 1.2: 11/17/2025 - CRITICAL: Modern OpenAI API (v1.0.0+)

⚠️ CRITICAL: OpenAI API Version
This template uses the MODERN OpenAI API (v1.0.0+):
  from openai import OpenAI
  client = OpenAI(api_key=api_key)
  response = client.chat.completions.create(...)

DO NOT use the old deprecated API:
  import openai
  openai.api_key = api_key  # ❌ OLD
  response = openai.ChatCompletion.create(...)  # ❌ DEPRECATED

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

⚠️ CRITICAL IMPORTS (Nov 16, 2025 - Demo Prep Learning):
- ✅ ALWAYS import Rule INSIDE declare_logic() function (avoid circular imports)
- ✅ ALWAYS import models at module level only: import database.models as models
- ✅ NEVER import LogicRow, Rule at module level
- ❌ NEVER use: from logic_bank.rule_bank.rule_bank import RuleBank
- ❌ NEVER use: from logic_bank.extensions.rule_extensions import Rule

This is a working reference implementation showing the complete pattern.

⚠️ CRITICAL: OpenAI API Version
This template uses the MODERN OpenAI API (v1.0.0+):
  from openai import OpenAI
  client = OpenAI(api_key=api_key)
  response = client.chat.completions.create(...)

DO NOT use the old deprecated API:
  import openai
  openai.api_key = api_key  # ❌ OLD
  response = openai.ChatCompletion.create(...)  # ❌ DEPRECATED
"""

import database.models as models

def declare_logic():
    from logic_bank.logic_bank import Rule  # ✅ Import inside function to avoid circular imports
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
    def ItemUnitPriceFromSupplier(row: models.Item, old_row: models.Item, logic_row):
        """Formula computes unit_price: AI if suppliers exist, else copy from product."""
        from logic.logic_discovery.ai_requests.supplier_selection import get_supplier_price_from_ai
        
        if row.product.count_suppliers == 0:
            return row.product.unit_price
        
        logic_row.log(f"Item - Product has {row.product.count_suppliers} suppliers, invoking AI")
        return get_supplier_price_from_ai(row=row, logic_row=logic_row)
    
    Rule.formula(derive=models.Item.unit_price, calling=ItemUnitPriceFromSupplier)
    
"""
REUSABLE AI HANDLER PATTERN:

The AI handler lives in a separate module for reusability:
Location: logic/logic_discovery/ai_requests/supplier_selection.py

This module contains:
1. get_supplier_price_from_ai() - Function that encapsulates Request Pattern, returns computed value
2. supplier_id_from_ai() - Event handler that populates audit fields
3. declare_logic() - Self-registers the event handler

KEY ARCHITECTURE DECISIONS:
- AI handler is reusable across multiple use cases
- Request Pattern implementation is HIDDEN in get_supplier_price_from_ai()
- Formula ONLY calls get_supplier_price_from_ai() - NO Request Pattern details
- Returns computed value (price), audit details stay in request table
- Auto-discovered and registered by logic_discovery system
"""

# ========================================
# AI HANDLER REFERENCE (for completeness)
# See logic/logic_discovery/ai_requests/supplier_selection.py for implementation
# ========================================

"""
def declare_logic():
    from logic_bank.logic_bank import Rule
    Rule.early_row_event(on_class=models.SysSupplierReq, calling=supplier_id_from_ai)

def get_supplier_price_from_ai(row, logic_row):
    '''
    Returns optimal supplier price using AI. Encapsulates Request Pattern.
    
    This function hides Request Pattern implementation from the formula.
    Creates SysSupplierReq audit record, triggers AI handler, returns computed price.
    '''
    # Create audit request using LogicBank API
    supplier_req_logic_row = logic_row.new_logic_row(models.SysSupplierReq)
    supplier_req = supplier_req_logic_row.row
    supplier_req_logic_row.link(to_parent=logic_row)
    
    # Set request context
    supplier_req.product_id = row.product_id
    supplier_req.item_id = row.id
    
    # Explicit insert triggers AI handler (supplier_id_from_ai)
    supplier_req_logic_row.insert(reason="AI supplier selection request")
    
    # Return computed value
    return supplier_req.chosen_unit_price

def supplier_id_from_ai(row: models.SysSupplierReq, old_row, logic_row):
    '''
    AI selects optimal supplier based on cost, lead time, and world conditions.
    Fires when SysSupplierReq record is inserted via Request Pattern.
    
    Populates audit fields:
    - chosen_supplier_id: Selected supplier ID
    - chosen_unit_price: Price from selected supplier
    - reason: AI's explanation for the choice
    - fallback_used: True if AI unavailable (uses min cost)
    '''
    if not logic_row.is_inserted():
        return
    
    product = row.product
    if not product or product.count_suppliers == 0:
        logic_row.log("No suppliers available for product")
        return
    
    # Load test context for reproducible testing
    test_context = _load_test_context(logic_row)
    world_conditions = test_context.get('world_conditions', 'normal operations')
    
    # Get list of candidate suppliers with their details
    candidates = []
    for ps in product.ProductSupplierList:
        candidates.append({
            'supplier_id': ps.supplier_id,
            'supplier_name': ps.supplier.company_name,
            'unit_cost': float(ps.unit_cost),
            'lead_time_days': ps.lead_time_days,
            'location': ps.supplier.region
        })
    
    # Call OpenAI API (with fallback to min cost if no API key)
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logic_row.log("No OpenAI API key - using fallback (min cost)")
        min_supplier = min(candidates, key=lambda s: s['unit_cost'])
        row.chosen_supplier_id = min_supplier['supplier_id']
        row.chosen_unit_price = Decimal(str(min_supplier['unit_cost']))
        row.reason = "Fallback: minimum cost supplier (no API key)"
        row.fallback_used = True
        return
    
    # Make AI request (see full implementation in ai_requests/supplier_selection.py)
    ai_result = _call_openai_structured(candidates, world_conditions, api_key, logic_row)
    
    # Populate audit fields with AI decision
    row.chosen_supplier_id = ai_result['chosen_supplier_id']
    row.chosen_unit_price = Decimal(str(ai_result['chosen_unit_price']))
    row.reason = ai_result['reason']
    row.fallback_used = False

def declare_logic():
    from logic_bank.logic_bank import Rule
    # Register AI event handler - fires on SysSupplierReq insert
    Rule.early_row_event(on_class=models.SysSupplierReq, calling=supplier_id_from_ai)
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

2. FUNCTIONAL FORMULA PATTERN
   - Rule.formula(calling=function) - function returns computed value
   - Conditional logic: if count == 0 then default else invoke AI
   - Uses Request Pattern: insert audit record triggers AI event handler
   - Returns value from populated audit record (chosen_unit_price)

3. REQUEST PATTERN FOR AI INVOCATION
   - Formula creates SysSupplierReq audit record using logic_row.new_logic_row()
   - Insert triggers early_row_event handler (supplier_id_from_ai)
   - Handler populates audit fields (chosen_supplier_id, chosen_unit_price, reason)
   - Formula returns the computed value from audit record

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

5. AUTO-DISCOVERY
   - Scans logic/logic_discovery/ recursively
   - AI handlers in ai_requests/ subfolder
   - Each module has declare_logic() to self-register

6. REUSABILITY
   - Multiple use cases can use same Request Pattern with SysSupplierReq
   - AI handler (supplier_id_from_ai) is testable independently
   - Easy to add more AI handlers (price_optimization, route_selection, etc.)
   - Each handler follows same pattern: early_row_event on audit table
"""
