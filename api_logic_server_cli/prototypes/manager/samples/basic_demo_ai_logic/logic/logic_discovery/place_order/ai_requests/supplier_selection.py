"""
AI Supplier Selection - AI Rules Handler

This module implements AI-driven supplier selection based on cost, lead time,
and world conditions. It uses the Request Pattern for full audit trails.

See: https://apilogicserver.github.io/Docs/Logic-Using-AI/

version: 3.0
date: February 5, 2026
source: docs/training/probabilistic_logic.md (AI Rules)

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
    
    Strategy:
    1. Load test context for INPUT conditions (world conditions like "Suez Canal blocked")
    2. Always try AI with those conditions
    3. If no API key or API fails, use fallback (min cost)
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
    
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent.parent
    context_file = project_root / 'config' / 'ai_test_context.yaml'
    
    test_context = {}
    if context_file.exists():
        with open(str(context_file), 'r') as f:
            test_context = yaml.safe_load(f) or {}
    
    world_conditions = test_context.get('world_conditions', 'normal conditions')
    
    selected_supplier = None
    
    # Try AI (check for API key)
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
                row.reason = f"AI: {supplier_name} (${selected_supplier.unit_cost}) - {ai_result.get('reason', 'No reason provided')}"
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
    Wrapper function called from Item (Receiver) early event.
    
    See: https://apilogicserver.github.io/Docs/Logic-Using-AI/

    1. Creates SysSupplierReq and inserts it (triggering AI event that populates chosen_* fields)
    2. Returns populated object
    
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
    # Note: request/reason fields populated by AI event handler with actual prompt/candidate data
    supplier_req.product_id = product_id
    supplier_req.item_id = item_id
    
    # 3. Insert triggers early event which populates AI values (chosen_* fields, request, reason)
    supplier_req_logic_row.insert(reason="AI supplier selection request")
    
    # 4. Log filled request object for visibility
    logic_row.log(f"AI Request: {supplier_req.request}")
    logic_row.log(f"AI Results: supplier_id={supplier_req.chosen_supplier_id}, price={supplier_req.chosen_unit_price}, reason={supplier_req.reason}")
    
    # 5. Return populated object (chosen_* fields now set by AI)
    return supplier_req
