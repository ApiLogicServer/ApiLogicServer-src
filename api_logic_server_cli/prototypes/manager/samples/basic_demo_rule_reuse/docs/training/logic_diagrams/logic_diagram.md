---
title: Logic Diagram — Generation and Viewing Guide
version: 1.4
changelog:
  - 1.4 (2026-05-21) - Intra-table arcs injected directly into SVG (Graphviz drops self-loops
                        on spline layouts); multiple arcs on same node fan out with staggered
                        bulge distances; ONE arc per formula rule (not one per dep)
  - 1.3 (2026-05-21) - Major redesign: uniform dark-grey arrows (style=type, not colour),
                        LR layout, intra-table formula arcs post-processed to sit in whitespace,
                        calling= function bodies scanned for deps, where= clause cols shown on
                        child table, formula expression shown inline on derived column,
                        scoped diagrams via requirement filter
  - 1.2 (2026-05-21) - SVG post-processor added; feed labels moved outside node; arc tightening
  - 1.1 (2026-05-21) - calling= angle-bracket fix; output moved to docs/requirements/
  - 1.0 (2026-05-21) - Initial version
---

# Logic Diagram

Visual map of the declarative rule chain — which tables, columns, and rules fire when a row is inserted or updated.

## Viewing

Open `docs/requirements/logic_diagram.svg` in a browser (drag-and-drop) or VSCode **SVG Preview** extension.

**Reading the diagram:**

- Tables show only columns involved in logic (derived values, inputs to formulas, where= clause cols)
- Light grey lines = FK relationships (schema structure — background context)
- **⚡ trigger node** = the originating event (e.g. `Item inserted`)
- Numbered dark-grey arrows = logic flow in causal order from the trigger:
  - **Solid** = `Rule.copy` — parent value flows down to child
  - **Dashed** = `Rule.sum` / `Rule.count` — change propagates up to parent (arrowhead at parent)
  - **Dashed lighter** = `Rule.formula` cross-table dependency
  - **Small right-side arc** = intra-table formula dependency (e.g. `unit_price` → `amount`)
  - **Green dashed** = event (`after_flush_row_event` etc.) — side-effect after commit
- Orange annotation on column = formula expression (e.g. `= quantity * unit_price`, `= _clvs_reason(row)`)
- Red-bordered table = has a `Rule.constraint`
- **Rules legend** = numbered natural-language rule descriptions matching the arrows

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

Output: `docs/requirements/logic_diagram[_<requirement>].svg` + matching `.dot` source.

The generator reads:
- `logic/declare_logic.py` + all `logic/logic_discovery/**/*.py`
- `docs/db.dbml` for FK relationships and table rank ordering (parents at top/left)
- For `calling=` rules: scans the function body for `row.attr` dependencies
- For `where=` clauses: registers child-table columns used as filter conditions

Run after adding or changing logic rules.

## Shortcut: generate_logic_diagram.py

Each project includes a convenience script so you don't need to remember the Manager path:

```bash
# From inside the project directory:
python docs/generate_logic_diagram.py

# Scoped:
python docs/generate_logic_diagram.py check_credit
```

## How the Diagram is Built

1. **Parse** — reads all logic files, extracts Rule.* declarations including `calling=` function bodies and `where=` clause columns
2. **Rank** — uses `docs/db.dbml` FK graph to place parent tables left, children right
3. **Render** — writes `.dot`, runs `graphviz dot -Tsvg`
4. **Post-process** — SVG is patched in two ways:
   - Feed-annotation labels (`→col(n)`) moved outside node right boundary
   - Intra-table arcs **injected directly** as SVG bezier paths (Graphviz silently drops
     self-loop edges on spline layouts). Multiple arcs on the same node fan out at staggered
     bulge distances (20, 38, 56 ... px) so they read clearly in the whitespace

## Known Issues

**Intra-table formula arcs** — `Rule.formula` rules where all inputs are on the same table (e.g. `amount = quantity * unit_price`, or `clvs_eligible` depending on `prohibited_commodity_count`) are recorded as `// INTRA:` comments in the `.dot` file and injected as SVG bezier paths in post-processing. If arcs are missing, check that `docs/db.dbml` exists. Multiple arcs on the same node fan out automatically.

**`calling=` dependency tracking** — LogicBank scans the calling function body for `row.attr` references. The diagram generator does the same. If a function calls a helper that references `row.attr`, those deps won't appear in the diagram (same limitation as LogicBank itself — see CE for the correct pattern).
