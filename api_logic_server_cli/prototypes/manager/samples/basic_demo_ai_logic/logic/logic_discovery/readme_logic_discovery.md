You can declare logic in `declare_logic.py`,
but that can lead to a lot of rules in 1 file.

A *best practice* is to create logic files in this directory,
named after the use case (e.g., `check_credit.py`).  

## Organizing Related Use Cases

For complex scenarios with multiple related use cases, you can organize them hierarchically:

- **Flat structure** (simple cases): `check_credit.py`, `validate_order.py`
- **Hierarchical structure** (complex workflows): 
  - `place_order/check_credit.py` - Credit validation for order placement
  - `place_order/app_integration.py` - External integrations for order placement
  - `ship_order/validate_inventory.py` - Inventory checks for shipping

**When to use hierarchical structure:**
- The prompt describes a parent use case with sub-cases (e.g., "On Placing Orders, Check Credit:")
- Multiple related operations share a common workflow (e.g., order placement, customer onboarding)
- You want to group related logic files for better organization

The easiest way to to copy/paste `use_case.py` to a new file, then
add your logic either by Natural Language (use your Coding Assistant, such as CoPilot),
or your IDE's code completion.
