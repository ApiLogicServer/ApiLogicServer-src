"""
TEMPLATE: Probabilistic + Deterministic Rules Implementation

This template provides a clean reference implementation for AI value computation
alongside deterministic rules, using the Request Pattern with early events.

Pattern: Early event with wrapper function that returns populated request object
version: 3.0
date: November 21, 2025
source: docs/training/probabilistic_template.py

See docs/training/probabilistic_logic.prompt for complete documentation.

IMPORTANT: When generating code from this template, include version tracking
in generated files (supplier_selection.py, check_credit.py) with:
  version: 3.0
  date: [current date]
  source: docs/training/probabilistic_logic.prompt
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
    
    Fires on insert AND when product_id changes (same semantics as copy rule).
    
    Pattern:
    1. Check condition (suppliers available?)
    2. Call wrapper function
    3. Extract needed value from returned object
    """
    from logic.logic_discovery.ai_requests.supplier_selection import get_supplier_selection_from_ai
    
    # Skip on delete (old_row is None) - CRITICAL: Check this FIRST
    if logic_row.is_deleted():
        return
    
    # Process on insert OR when product_id changes
    if not (logic_row.is_inserted() or row.product_id != old_row.product_id):
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
2. select_supplier_via_ai() - AI handler that implements supplier selection
3. get_supplier_selection_from_ai() - Wrapper that hides Request Pattern

version: 3.0
date: November 21, 2025
source: docs/training/probabilistic_template.py
"""

from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database import models
from decimal import Decimal
import os

def declare_logic():
    """
    Register early event on SysSupplierReq to populate chosen_* fields via AI.
    
    This Request Pattern approach provides full audit trails and separation of concerns.
    See: https://apilogicserver.github.io/Docs/Logic/#rule-patterns
    """
    Rule.early_row_event(on_class=models.SysSupplierReq, calling=select_supplier_via_ai)

def select_supplier_via_ai(row: models.SysSupplierReq, old_row, logic_row: LogicRow):
    """
    Early event (called via insert from wrapper) to populate chosen_* fields via AI.
    
    This AI handler gets called automatically when SysSupplierReq is inserted,
    populating AI Results: chosen_supplier_id and chosen_unit_price.
    """
    if not logic_row.is_inserted():
        return
    
    # Get candidates (suppliers for this product)
    product = row.product
    suppliers = product.ProductSupplierList if product else []
    
    if not suppliers:
        row.request = f"Select supplier for {product.name if product else 'unknown product'} - No suppliers available"
        row.reason = "No suppliers exist for this product"
        logic_row.log("No suppliers available for AI selection")
        row.fallback_used = True
        return
    
    # Load test context for world conditions (not for predetermined supplier selection)
    from pathlib import Path
    import yaml
    
    config_dir = Path(__file__).resolve().parent.parent.parent.parent / 'config'
    context_file = config_dir / 'ai_test_context.yaml'
    
    test_context = {}
    if context_file.exists():
        with open(str(context_file), 'r') as f:
            test_context = yaml.safe_load(f) or {}
    
    world_conditions = test_context.get('world_conditions', 'normal conditions')
    
    selected_supplier = None
    
    # Try AI (check for API key)
    if True:  # Always try AI unless no key
        api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")
        if api_key:
            try:
                # Call OpenAI API with structured prompt
                from openai import OpenAI
                import json
                
                client = OpenAI(api_key=api_key)
                
                # Build candidate data for prompt - include ALL supplier fields for AI decision
                candidate_data = []
                for supplier in suppliers:
                    supplier_obj = supplier.supplier
                    candidate_data.append({
                        'supplier_id': supplier.supplier_id,
                        'supplier_name': supplier_obj.name if supplier_obj else 'Unknown',
                        'supplier_region': supplier_obj.region if supplier_obj else None,
                        'supplier_contact': supplier_obj.contact_name if supplier_obj else None,
                        'supplier_phone': supplier_obj.phone if supplier_obj else None,
                        'supplier_email': supplier_obj.email if supplier_obj else None,
                        'unit_cost': float(supplier.unit_cost) if supplier.unit_cost else 0.0,
                        'lead_time_days': supplier.lead_time_days if hasattr(supplier, 'lead_time_days') else None,
                        'supplier_part_number': supplier.supplier_part_number if hasattr(supplier, 'supplier_part_number') else None
                    })
                
                prompt = f"""
You are a supply chain optimization expert. Select the best supplier from the candidates below.

World Conditions: {world_conditions}

Optimization Goal: fastest reliable delivery while keeping costs reasonable

Candidates:
{yaml.dump(candidate_data, default_flow_style=False)}

Respond with ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
    "chosen_supplier_id": <id>,
    "chosen_unit_price": <price>,
    "reason": "<brief explanation>"
}}
"""
                
                # Populate request field with actual prompt summary including key fields
                candidate_summary = ', '.join([
                    f"{c['supplier_name']}(${c['unit_cost']}, {c['supplier_region'] or 'unknown region'}, {c['lead_time_days'] or '?'}days)" 
                    for c in candidate_data
                ])
                row.request = f"Select supplier for {product.name}: Candidates=[{candidate_summary}], World={world_conditions}"
                
                logic_row.log(f"Calling OpenAI API with {len(candidate_data)} candidates, world conditions: {world_conditions}")
                
                response = client.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages=[
                        {"role": "system", "content": "You are a supply chain expert. Respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                response_text = response.choices[0].message.content.strip()
                logic_row.log(f"OpenAI response: {response_text}")
                
                # Parse JSON response
                ai_result = json.loads(response_text)
                
                # Find the selected supplier
                selected_supplier = next((s for s in suppliers if s.supplier_id == ai_result['chosen_supplier_id']), None)
                if selected_supplier:
                    supplier_name = selected_supplier.supplier.name if selected_supplier.supplier else 'Unknown'
                    row.reason = f"Selected {supplier_name} (${selected_supplier.unit_cost}) - {ai_result.get('reason', 'No reason provided')}"
                    row.fallback_used = False
                else:
                    logic_row.log(f"AI selected invalid supplier_id {ai_result['chosen_supplier_id']}, using fallback")
                    selected_supplier = min(suppliers, key=lambda s: float(s.unit_cost) if s.unit_cost else 999999.0)
                    fallback_name = selected_supplier.supplier.name if selected_supplier.supplier else 'Unknown'
                    row.reason = f"Fallback: {fallback_name} (${selected_supplier.unit_cost}) - AI returned invalid supplier"
                    row.fallback_used = True
                    
            except Exception as e:
                logic_row.log(f"OpenAI API error: {e}, using fallback")
                selected_supplier = min(suppliers, key=lambda s: float(s.unit_cost) if s.unit_cost else 999999.0)
                fallback_name = selected_supplier.supplier.name if selected_supplier.supplier else 'Unknown'
                candidate_summary = ', '.join([f"{s.supplier.name if s.supplier else 'Unknown'}(${s.unit_cost})" for s in suppliers])
                row.request = f"Select supplier for {product.name}: Candidates=[{candidate_summary}] - API ERROR"
                row.reason = f"Fallback: {fallback_name} (${selected_supplier.unit_cost}) - API error: {str(e)[:100]}"
                row.fallback_used = True
        else:
            # No API key - use fallback strategy (min cost)
            logic_row.log("No API key, using fallback: minimum cost")
            selected_supplier = min(suppliers, key=lambda s: float(s.unit_cost) if s.unit_cost else 999999.0)
            fallback_name = selected_supplier.supplier.name if selected_supplier.supplier else 'Unknown'
            candidate_summary = ', '.join([f"{s.supplier.name if s.supplier else 'Unknown'}(${s.unit_cost})" for s in suppliers])
            row.request = f"Select supplier for {product.name}: Candidates=[{candidate_summary}] - NO API KEY"
            row.reason = f"Fallback: {fallback_name} (${selected_supplier.unit_cost}) - minimum cost (no API key)"
            row.fallback_used = True
    
    # Populate AI results
    if selected_supplier:
        row.chosen_supplier_id = int(selected_supplier.supplier_id)  # Must be int for SQLite FK
        row.chosen_unit_price = selected_supplier.unit_cost
        logic_row.log(f"Selected supplier {selected_supplier.supplier_id} with price {selected_supplier.unit_cost}")

def get_supplier_selection_from_ai(product_id: int, item_id: int, logic_row: LogicRow) -> models.SysSupplierReq:
    """
    Typically called from Item (Receiver) early event 
    to get AI results from chosen ProductSupplier (Provider).

    See: https://apilogicserver.github.io/Docs/Logic-Using-AI/

    1. Creates SysSupplierReq and inserts it (triggering AI event that populates chosen_* fields)
    
    This wrapper hides Request Pattern implementation details.
    See https://apilogicserver.github.io/Docs/Logic/#rule-patterns.

    Returns populated SysSupplierReq object with:
    - Standard AI Audit: request, reason, created_on, fallback_used
    - Parent Context Links: item_id, product_id
    - AI Results: chosen_supplier_id, chosen_unit_price
    """
    # 1. Create request row using parent's logic_row
    supplier_req_logic_row = logic_row.new_logic_row(models.SysSupplierReq)
    supplier_req = supplier_req_logic_row.row
    
    # 2. Set parent context (FK links)
    supplier_req.product_id = product_id
    supplier_req.item_id = item_id
    
    # 3. Insert triggers early event which populates AI values
    supplier_req_logic_row.insert(reason="AI supplier selection request")
    
    # 4. Log filled request object for visibility
    logic_row.log(f"AI Request: {supplier_req.request}")
    logic_row.log(f"AI Results: supplier_id={supplier_req.chosen_supplier_id}, price={supplier_req.chosen_unit_price}, reason={supplier_req.reason}")
    
    # 5. Return populated object (chosen_* fields now set by AI)
    return supplier_req


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
