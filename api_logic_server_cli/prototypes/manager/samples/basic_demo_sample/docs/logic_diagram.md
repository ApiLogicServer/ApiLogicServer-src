# Logic Diagram

Visual map of the declarative rule chain — which tables, columns, and rules fire when a row is inserted or updated.

## Viewing

Open [`logic_diagram.svg`](logic_diagram.svg) in a browser (drag-and-drop) or in VSCode with the **SVG Preview** extension.

**Reading the diagram:**

- Tables shown with only the columns involved in logic (derived or used in derivations)
- Light grey lines = FK relationships (schema structure)
- **⚡ trigger node** = the originating event (e.g. `Item inserted`)
- Numbered arrows = logic flow in causal order from the trigger:
  1. **🔵 Blue solid** = `Rule.copy` — parent value flows down to child (exits right of parent col, enters left of child col)
  2. **🟠 Orange dashed** = `Rule.formula` — derived from other columns on same table (self-loop) or cross-table
  3. **🔴 Red dashed** = `Rule.sum` / `Rule.count` — change propagates up to parent (arrowhead at parent col)
  4. **🟢 Green dashed** = event (`after_flush_row_event` etc.) — side-effect after commit
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

Scoped diagrams are written to `docs/logic_diagram_<requirement>.svg`.

The generator reads:
- `logic/declare_logic.py` and all `logic/logic_discovery/**/*.py` files
- `docs/db.dbml` for FK relationships and table rank ordering

Run it any time you add or change logic rules.
