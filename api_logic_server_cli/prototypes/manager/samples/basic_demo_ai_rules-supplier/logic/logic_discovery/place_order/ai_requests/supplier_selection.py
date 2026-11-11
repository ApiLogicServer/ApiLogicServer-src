"""
AI Supplier Selection (Request Pattern): chooses the optimal Product Supplier from cost, lead time and
world conditions (config/ai_test_context.yaml). Every call is audited in SysSupplierReq. With no LLM
configured, or on an LLM error / invalid answer, falls back to the minimum-cost supplier (fallback_used).
"""
import datetime
from pathlib import Path

import yaml
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule

from database import models
from integration.ai.llm_client import chat_json, LLMError, LLMNotAvailable


def declare_logic():
    Rule.early_row_event(on_class=models.SysSupplierReq, calling=select_supplier_via_ai)


def select_supplier_via_ai(row: models.SysSupplierReq, old_row, logic_row: LogicRow):
    """SysSupplierReq event: picks the optimal supplier via the LLM (world conditions from the test context),
    else the minimum-cost supplier; records request, reason, fallback_used and the chosen supplier and price."""
    if not logic_row.is_inserted():
        return
    row.created_on = datetime.datetime.now().isoformat(timespec='seconds')
    product = logic_row.session.get(models.Product, row.product_id)
    suppliers = logic_row.session.query(models.ProductSupplier).filter_by(product_id=row.product_id).all()
    if not suppliers:
        row.request = f"Select supplier for {product.name if product else 'unknown product'} - no suppliers"
        row.reason = "No suppliers exist for this product"
        row.fallback_used = True
        return

    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    context_file = project_root / 'config' / 'ai_test_context.yaml'
    test_context = {}
    if context_file.exists():
        with open(str(context_file), 'r') as f:
            test_context = yaml.safe_load(f) or {}
    world_conditions = test_context.get('world_conditions', 'normal conditions')

    candidate_data = []
    for ps in suppliers:
        supplier = ps.supplier
        candidate_data.append({
            'supplier_id': ps.supplier_id,
            'supplier_name': supplier.name if supplier else 'Unknown',
            'supplier_region': supplier.region if supplier else None,
            'unit_cost': float(ps.unit_cost) if ps.unit_cost is not None else 0.0,
            'lead_time_days': ps.lead_time_days,
        })
    candidate_summary = ', '.join(
        f"{c['supplier_name']}(${c['unit_cost']}, {c['supplier_region'] or 'unknown region'}, {c['lead_time_days'] or '?'}days)"
        for c in candidate_data)
    row.request = f"Select supplier for {product.name}: Candidates=[{candidate_summary}], World={world_conditions}"

    prompt = f"""
You are a supply chain optimization expert. Select the best supplier from the candidates below.

World Conditions: {world_conditions}

Optimization Goal: fastest reliable delivery while keeping costs reasonable

Candidates:
{yaml.dump(candidate_data, default_flow_style=False)}

Respond with ONLY a valid JSON object in this exact format (no markdown, no code blocks):
{{
    "chosen_supplier_id": <id>,
    "chosen_unit_price": <price>,
    "reason": "<brief explanation>"
}}
"""
    selected = None
    ai_result = None
    fallback_cause = None
    try:
        logic_row.log(f"Calling LLM with {len(candidate_data)} candidates, world conditions: {world_conditions}")
        ai_result = chat_json(system="You are a supply chain expert. Respond with valid JSON only.",
                              user=prompt, temperature=0.7)
        logic_row.log(f"LLM response: {ai_result}")
    except LLMNotAvailable:
        fallback_cause = "no LLM configured"
    except LLMError as e:
        fallback_cause = f"LLM error: {str(e)[:100]}"

    if ai_result is not None:
        try:
            chosen_id = int(ai_result['chosen_supplier_id'])
        except (KeyError, TypeError, ValueError):
            chosen_id = None
        selected = next((s for s in suppliers if s.supplier_id == chosen_id), None)
        if selected:
            name = selected.supplier.name if selected.supplier else 'Unknown'
            row.reason = f"AI: {name} (${selected.unit_cost}) - {ai_result.get('reason', 'No reason provided')}"
            row.fallback_used = False
        else:
            fallback_cause = "AI returned an invalid supplier"

    if selected is None:
        logic_row.log(f"Using fallback (minimum cost): {fallback_cause}")
        selected = min(suppliers, key=lambda s: float(s.unit_cost) if s.unit_cost is not None else 999999.0)
        name = selected.supplier.name if selected.supplier else 'Unknown'
        row.reason = f"Fallback: {name} (${selected.unit_cost}) - minimum cost ({fallback_cause})"
        row.fallback_used = True

    row.chosen_supplier_id = int(selected.supplier_id)
    row.chosen_unit_price = selected.unit_cost


def get_supplier_selection_from_ai(product_id: int, item: models.Item, logic_row: LogicRow) -> models.SysSupplierReq:
    """SysSupplierReq wrapper: inserts the request row (which fires the selection event) and returns it populated.
    Links to the Item by object, never by id: a new Item has no id yet in an early event."""
    req_logic_row = logic_row.new_logic_row(models.SysSupplierReq)
    supplier_req = req_logic_row.row
    supplier_req.product_id = product_id
    supplier_req.item = item
    req_logic_row.insert(reason="AI supplier selection request")
    logic_row.log(f"AI Request: {supplier_req.request}")
    logic_row.log(f"AI Results: supplier_id={supplier_req.chosen_supplier_id}, price={supplier_req.chosen_unit_price}, reason={supplier_req.reason}")
    return supplier_req
