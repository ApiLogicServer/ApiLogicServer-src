---
title: Logic Diagram — Generation and Viewing Guide
version: 1.1
changelog:
  - 1.1 (2026-05-21) - Fixed bug in logic_diagram_gv.py: calling= function names with
                        angle brackets caused Graphviz HTML label parse errors; now strips
                        non-alphanumeric chars before embedding in labels. Output path
                        updated to docs/requirements/ (was docs/).
  - 1.0 (2026-05-21) - Initial version
---

# Logic Diagram

Visual map of the declarative rule chain — which tables, columns, and rules fire when a row is inserted or updated.

## Viewing

Open [`docs/requirements/logic_diagram.svg`](requirements/logic_diagram.svg) in a browser (drag-and-drop) or in VSCode with the **SVG Preview** extension.

**Reading the diagram:**

- Tables shown with only the columns involved in logic (derived or used in derivations)
- Light grey lines = FK relationships (schema structure)
- **⚡ trigger node** = the originating event (e.g. `Item inserted`)
- Numbered arrows = logic flow in causal order from the trigger:
  1. **🔵 Blue solid** = `Rule.copy` — parent value snapshot flows down to child (exits right of parent col, enters left of child col)
  2. **🟠 Orange dashed** = `Rule.formula` — derived from other columns on same table (self-loop) or cross-table
  3. **🔴 Red dashed** = `Rule.sum` / `Rule.count` — change propagates up to parent (arrowhead at parent col)
  4. **🟢 Green dashed** = event (`after_flush_row_event`, `row_event`, etc.) — side-effect after commit
- Red-bordered table = has a `Rule.constraint`
- **Rules legend** at bottom = numbered descriptions matching the arrows

## Regenerating

Requires `graphviz` — install once:
```bash
brew install graphviz          # macOS
# sudo apt install graphviz   # Linux
```

Then from the **Manager root**:

```bash
# Full diagram — all rules, all tables:
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py basic_demo

# Scoped to one requirement (only tables/rules for that use case):
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py basic_demo check_credit
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py basic_demo place_order
```

Output is written to `docs/requirements/logic_diagram[_<requirement>].svg` and a matching `.dot` source file.

The generator reads:
- All `logic/logic_discovery/**/*.py` files (and `logic/declare_logic.py` for full diagrams)
- `docs/db.dbml` for FK relationships and table rank ordering

Run it any time you add or change logic rules.

## Known Issues / Bug Fixes

**v1.1 fix — `calling=` function names in HTML labels**

Rules using `calling=my_func` (instead of `as_expression=lambda`) caused Graphviz to fail with:

```
Error: Unknown HTML element <_clvs_reason> on line 1 in label of node Shipment
```

The generator was embedding the function name wrapped in angle brackets (`<_clvs_reason>`) directly into Graphviz HTML table labels. Fixed in `logic_diagram_gv.py` by stripping non-alphanumeric characters from the calling function name before use in labels and legend text.
