"""
AI Supplier Selection - Request Pattern handler for Check Credit clause 6.

Not a requirement file: it implements "Use AI to Set Item field unit_price by finding the optimal
Product Supplier based on cost, lead time, and world conditions" (see place_order/check_credit.py).
"""

import json
import os
from pathlib import Path
from datetime import datetime

import yaml
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Register the early event that fills a SysSupplierReq (the AI audit row) when it is inserted."""
    Rule.early_row_event(on_class=models.SysSupplierReq, calling=select_supplier_via_ai)


def _cost(s) -> float:
    return float(s.unit_cost) if s.unit_cost is not None else 999999.0


def select_supplier_via_ai(row: models.SysSupplierReq, old_row, logic_row: LogicRow):
    """SysSupplierReq event: chooses the optimal ProductSupplier by calling OpenAI with the candidates and
    the world conditions from config/ai_test_context.yaml; falls back to minimum cost when there is no API
    key or the call fails, and records request, reason, fallback_used and the choice as the audit trail."""
    if not logic_row.is_inserted():
        return

    row.created_on = datetime.now().isoformat(timespec="seconds")
    product = logic_row.session.get(models.Product, row.product_id)
    suppliers = list(product.ProductSupplierList) if product else []
    if not suppliers:
        row.request = f"Select supplier for {product.name if product else 'unknown product'} - no suppliers"
        row.reason = "No suppliers exist for this product"
        row.fallback_used = True
        return

    context_file = Path(__file__).resolve().parent.parent.parent.parent / "config" / "ai_test_context.yaml"
    test_context = {}
    if context_file.exists():
        with open(str(context_file), "r") as f:
            test_context = yaml.safe_load(f) or {}
    world_conditions = test_context.get("world_conditions", "normal conditions")

    candidates = []
    for ps in suppliers:
        sup = ps.supplier
        candidates.append({"supplier_id": ps.supplier_id, "supplier_name": sup.name if sup else "Unknown",
                           "supplier_region": sup.region if sup else None,
                           "unit_cost": _cost(ps), "lead_time_days": ps.lead_time_days})
    summary = ", ".join(f"{c['supplier_name']}(${c['unit_cost']}, {c['supplier_region'] or 'unknown region'}, "
                        f"{c['lead_time_days'] or '?'}days)" for c in candidates)
    row.request = f"Select supplier for {product.name}: Candidates=[{summary}], World={world_conditions}"

    chosen = None
    api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")
    if not api_key:
        logic_row.log("No API key, using fallback: minimum cost")
        chosen = min(suppliers, key=_cost)
        row.reason = f"Fallback: {chosen.supplier.name} (${chosen.unit_cost}) - minimum cost (no API key)"
        row.fallback_used = True
    else:
        try:
            from openai import OpenAI
            prompt = f"""You are a supply chain optimization expert. Select the best supplier from the candidates below.

World Conditions: {world_conditions}

Optimization Goal: fastest reliable delivery while keeping costs reasonable (consider cost, lead time, and the world conditions)

Candidates:
{yaml.dump(candidates, default_flow_style=False)}

Respond with ONLY valid JSON in this exact format (no markdown, no code blocks):
{{"chosen_supplier_id": <id>, "chosen_unit_price": <price>, "reason": "<brief explanation>"}}"""
            logic_row.log(f"Calling OpenAI with {len(candidates)} candidates, world conditions: {world_conditions}")
            response = OpenAI(api_key=api_key).chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[{"role": "system", "content": "You are a supply chain expert. Respond with valid JSON only."},
                          {"role": "user", "content": prompt}],
                temperature=0.7)
            text = (response.choices[0].message.content or "").strip()
            if text.startswith("```"):
                text = "\n".join(text.split("\n")[1:-1]).strip()
            logic_row.log(f"OpenAI response: {text}")
            result = json.loads(text)
            chosen = next((s for s in suppliers if s.supplier_id == int(result["chosen_supplier_id"])), None)
            if chosen:
                row.reason = f"AI: {chosen.supplier.name} (${chosen.unit_cost}) - {result.get('reason', 'No reason provided')}"
                row.fallback_used = False
            else:
                chosen = min(suppliers, key=_cost)
                row.reason = f"Fallback: {chosen.supplier.name} (${chosen.unit_cost}) - AI returned an invalid supplier"
                row.fallback_used = True
        except Exception as e:
            logic_row.log(f"OpenAI API error: {e}, using fallback")
            chosen = min(suppliers, key=_cost)
            row.reason = f"Fallback: {chosen.supplier.name} (${chosen.unit_cost}) - API error: {str(e)[:100]}"
            row.fallback_used = True

    row.chosen_supplier_id = int(chosen.supplier_id)
    row.chosen_unit_price = chosen.unit_cost
    logic_row.log(f"Selected supplier {chosen.supplier_id} with price {chosen.unit_cost}")


def get_supplier_selection_from_ai(product_id: int, item: models.Item, logic_row: LogicRow) -> models.SysSupplierReq:
    """Item helper: inserts a SysSupplierReq (Request Pattern) for the Item's product, which fires
    select_supplier_via_ai, and returns the populated request row."""
    req_logic_row = logic_row.new_logic_row(models.SysSupplierReq)
    req = req_logic_row.row
    req.product_id = product_id
    req.item = item  # by object: a new Item has no id yet
    req_logic_row.insert(reason="AI supplier selection request")
    logic_row.log(f"AI Request: {req.request}")
    logic_row.log(f"AI Results: supplier_id={req.chosen_supplier_id}, price={req.chosen_unit_price}, reason={req.reason}")
    return req
