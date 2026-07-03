"""
logic_diagram_gv.py — Generate a Graphviz logic dependency diagram.

Two-layer design (matches LogicBank wiki style):
  - Schema layer : table boxes (only tables involved in logic), FK crow's-foot lines
  - Logic layer  : numbered arrows showing rule chain, starting from a trigger node
  - Legend       : numbered rule list at bottom-center

Usage (from Manager root):
    python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py <project> [<requirement>]

    <requirement> is optional — matches logic file names or directory names:
        (none)              → all rules, all tables
        check_credit        → only rules in files matching *check_credit*
        place_order         → all files under logic_discovery/place_order/
        clvs_eligibility    → only rules in *clvs_eligibility*

Output:
    docs/requirements/logic_diagram[_<req>].svg
    docs/requirements/logic_diagram[_<req>].dot

Requires: graphviz dot binary (brew install graphviz)

Changelog:
  1.2 - Uniform dark-grey logic arrows (style distinguishes type, not colour)
        Explicit left/right port boxes flanking each attribute name
        Intra-table formula shown as annotation on column, not self-loop
        Event nodes clustered on right margin
        Inline edge labels dropped — number only, legend carries description
        More breathing room (ranksep/nodesep increased)
  1.1 - calling= function names stripped of angle brackets (Graphviz HTML fix)
        Output moved to docs/requirements/
  1.0 - Initial version
"""

import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict


# ── colours ───────────────────────────────────────────────────────────────────
C_TABLE_FILL    = "#4a6fa5"   # table header
C_TABLE_FONT    = "white"
C_COL_FILL      = "#dbe4f0"   # column cell background
C_COL_FONT      = "#1a1a2e"
C_PORT_FILL     = "#b8cce8"   # left/right anchor port cells — slightly darker
C_CONSTRAINT    = "#c0392b"   # red border on constrained table
C_TRIGGER_FILL  = "#e8f5e9"
C_TRIGGER_BORD  = "#27ae60"

# Logic flow arrows — all uniform dark grey; style (solid/dashed) distinguishes type
C_FLOW          = "#444444"   # all logic arrows
C_FLOW_LIGHT    = "#444444"   # logic arrows
C_INTRA_ARC     = "#445544"   # sentinel colour for intra-table arcs — post-processor finds these
C_EVENT         = "#27ae60"   # events stay green — genuinely different (side-effects)
C_FK            = "#e0e0e0"   # very faint FK lines

# Formula annotation colour on column cell
C_FORMULA_ANN   = "#e67e22"   # orange text annotation inside column


# ── regex ─────────────────────────────────────────────────────────────────────
_RE_SUM     = re.compile(r'Rule\.sum\s*\([^)]*derive\s*=\s*([^\s,)]+)[^)]*as_sum_of\s*=\s*([^\s,)]+)([^)]*\))', re.DOTALL)
_RE_COUNT   = re.compile(r'Rule\.count\s*\([^)]*derive\s*=\s*([^\s,)]+)[^)]*as_count_of\s*=\s*([^\s,)]+)([^)]*\))', re.DOTALL)
_RE_FORMULA = re.compile(r'Rule\.formula\s*\([^)]*derive\s*=\s*([^\s,)]+)[^)]*as_expression\s*=\s*lambda\s+row\s*:(.*?)(?=\)|,\s*no_prune)', re.DOTALL)
_RE_FORMULA_CALL = re.compile(r'Rule\.formula\s*\([^)]*derive\s*=\s*([^\s,)]+)[^)]*calling\s*=\s*([^\s,)]+)', re.DOTALL)
_RE_COPY    = re.compile(r'Rule\.copy\s*\([^)]*derive\s*=\s*([^\s,)]+)[^)]*from_parent\s*=\s*([^\s,)]+)', re.DOTALL)
_RE_CONSTR  = re.compile(r'Rule\.constraint\s*\([^)]*validate\s*=\s*([^\s,)]+)', re.DOTALL)
_RE_EVENT   = re.compile(
    r'Rule\.(after_flush_row_event|commit_row_event|early_row_event)\s*\('
    r'[^)]*on_class\s*=\s*([^\s,)]+)[^)]*calling\s*=\s*([^\s,)]+)', re.DOTALL)
_RE_ROW_ATTR = re.compile(r'row\.([A-Za-z_][A-Za-z0-9_]*)')

# DBML: Ref: Child.(fk_col) > Parent.(id)
_RE_DBML_REF = re.compile(r'Ref:\s*(\w+)\.\((\w+)\)\s*>\s*(\w+)\.\((\w+)\)')

_SKIP_ATTRS = {'order', 'customer', 'product', 'item', 'supplier',
               'order_list', 'item_list', 'product_supplier_list',
               'sys_email', 'sysemail'}


def _strip(name):
    return re.sub(r'^models\.', '', name.strip())

def _cls(dotted):
    return dotted.split('.')[0]

def _col(dotted):
    parts = dotted.split('.')
    return parts[1] if len(parts) > 1 else dotted

def _port(dotted):
    return re.sub(r'[^A-Za-z0-9_]', '_', dotted)

def _clean(name):
    """Strip angle brackets and other Graphviz-unsafe chars."""
    return re.sub(r'[<>]', '', name)


# ── DBML parser ───────────────────────────────────────────────────────────────

def parse_dbml(project_dir: Path):
    dbml_path = project_dir / "docs" / "db.dbml"
    if not dbml_path.exists():
        return [], {}
    src = dbml_path.read_text(encoding="utf-8")
    fk_edges = []
    fk_parents = defaultdict(set)
    for m in _RE_DBML_REF.finditer(src):
        child, child_col, parent, parent_col = m.groups()
        fk_edges.append((child, child_col, parent, parent_col))
        fk_parents[child].add(parent)
    return fk_edges, fk_parents


def topo_rank(tables, fk_parents, all_fk_parents=None):
    fk = all_fk_parents if all_fk_parents else fk_parents
    ranks = {}
    for _ in range(len(tables) + 2):
        changed = False
        for t in list(tables):
            parents_in_diagram = fk.get(t, set()) & set(tables)
            parents_full       = fk.get(t, set())
            if not parents_full:
                new_rank = 0
            elif not parents_in_diagram:
                new_rank = 0
            else:
                parent_ranks = [ranks.get(p) for p in parents_in_diagram]
                if any(r is None for r in parent_ranks):
                    continue
                new_rank = max(parent_ranks) + 1
            if ranks.get(t) != new_rank:
                ranks[t] = new_rank
                changed = True
        if not changed:
            break
    for t in tables:
        if t not in ranks:
            ranks[t] = 0
    return ranks


# ── logic file parser ─────────────────────────────────────────────────────────

def find_logic_files(project_dir: Path, requirement: str = None):
    files = []
    declare = project_dir / "logic" / "declare_logic.py"
    if declare.exists() and requirement is None:
        files.append((declare, "logic/declare_logic.py"))

    disc = project_dir / "logic" / "logic_discovery"
    if disc.exists():
        for py in sorted(disc.rglob("*.py")):
            if py.name in ("auto_discovery.py", "__init__.py", "use_case.py"):
                continue
            rel = str(py.relative_to(project_dir))
            if requirement is None or requirement.lower() in rel.lower():
                files.append((py, rel))
    return files


def _scan_function_docstring(src, func_name):
    """Return the first line of the docstring for func_name, or '' if none."""
    pat = re.compile(
        r'def\s+' + re.escape(func_name) + r'\s*\(.*?\).*?:\s*\n\s*"""(.*?)"""',
        re.DOTALL
    )
    m = pat.search(src)
    if not m:
        return ''
    # First line only
    first = m.group(1).strip().splitlines()[0].strip()
    return first


def _scan_function_body(src, func_name):
    """
    Find the body of a named function in src and return all row.attr references.
    Used to resolve deps for Rule.formula(calling=func_name).
    """
    # Match: def func_name(row, ...) up to next def/class at same indent level
    pat = re.compile(
        r'def\s+' + re.escape(func_name) + r'\s*\(.*?\).*?:\n(.*?)(?=\ndef |\nclass |\Z)',
        re.DOTALL
    )
    m = pat.search(src)
    if not m:
        return []
    return _RE_ROW_ATTR.findall(m.group(1))


def parse_rules(files):
    rules = []
    seen_constraints = set()
    for path, rel in files:
        src = path.read_text(encoding="utf-8")
        for m in _RE_SUM.finditer(src):
            where_cols = [a for a in _RE_ROW_ATTR.findall(m.group(3) or "")
                          if a.lower() not in _SKIP_ATTRS]
            rules.append({"type":"sum", "derive":_strip(m.group(1)),
                          "source":_strip(m.group(2)),
                          "where_cols": where_cols, "file":rel})
        for m in _RE_COUNT.finditer(src):
            where_cols = [a for a in _RE_ROW_ATTR.findall(m.group(3) or "")
                          if a.lower() not in _SKIP_ATTRS]
            rules.append({"type":"count", "derive":_strip(m.group(1)),
                          "source":_strip(m.group(2)),
                          "where_cols": where_cols, "file":rel})
        for m in _RE_FORMULA.finditer(src):
            derive = _strip(m.group(1))
            expr_body = m.group(2).strip()
            deps = [f"{_cls(derive)}.{a}" for a in _RE_ROW_ATTR.findall(expr_body)
                    if a.lower() not in _SKIP_ATTRS]
            deps = [d for d in deps if d != derive]
            if not deps:
                deps = [_cls(derive)]
            # Store cleaned expression for annotation: strip "row." prefix
            expr_clean = re.sub(r'row\.', '', expr_body).strip()
            rules.append({"type":"formula", "derive":derive, "deps":deps,
                          "expr": expr_clean, "file":rel})
        for m in _RE_FORMULA_CALL.finditer(src):
            derive = _strip(m.group(1))
            calling = re.sub(r'[^A-Za-z0-9_.]', '', m.group(2).strip())
            # Scan the actual function body for row.attr deps
            body_attrs = _scan_function_body(src, calling.split('.')[-1])
            deps = [f"{_cls(derive)}.{a}" for a in body_attrs
                    if a.lower() not in _SKIP_ATTRS]
            deps = [d for d in deps if d != derive]
            if not deps:
                # fallback: show the function name as dep
                deps = [f"{_cls(derive)}.{calling}"]
            rules.append({"type":"formula", "derive":derive, "deps":deps,
                          "calling":calling, "file":rel})
        for m in _RE_COPY.finditer(src):
            rules.append({"type":"copy", "derive":_strip(m.group(1)),
                          "source":_strip(m.group(2)), "file":rel})
        for m in _RE_CONSTR.finditer(src):
            entity = _strip(m.group(1))
            if entity not in seen_constraints:
                seen_constraints.add(entity)
                rules.append({"type":"constraint", "entity":entity, "file":rel})
        for m in _RE_EVENT.finditer(src):
            rules.append({"type":"event", "kind":m.group(1),
                          "on":_strip(m.group(2)), "calling":m.group(3).strip(), "file":rel})
    return rules


def tables_in_rules(rules):
    tables = set()
    for r in rules:
        t = r["type"]
        if t in ("sum", "copy"):
            tables.add(_cls(r["derive"])); tables.add(_cls(r["source"]))
        elif t == "formula":
            tables.add(_cls(r["derive"]))
            for d in r["deps"]: tables.add(_cls(d))
        elif t == "count":
            tables.add(_cls(r["derive"])); tables.add(r["source"])
        elif t == "constraint":
            tables.add(r["entity"])
        elif t == "event":
            tables.add(r["on"])
    return {t for t in tables if '<' not in t and '.' not in t}


def cols_in_rules(rules):
    table_cols = defaultdict(list)
    # collect intra-table formula annotations: derive -> [dep_col, ...]
    intra_formula = defaultdict(list)

    def reg(dotted):
        if '.' not in dotted:
            return
        t, c = _cls(dotted), _col(dotted)
        if c not in table_cols[t]:
            table_cols[t].append(c)

    for r in rules:
        t = r["type"]
        if t in ("sum", "copy"):
            reg(r["derive"]); reg(r["source"])
        elif t == "formula":
            reg(r["derive"])
            for d in r["deps"]:
                if _cls(d) == _cls(r["derive"]):
                    # intra-table dep — register the col AND note for annotation
                    col_name = _col(d)
                    tbl = _cls(d)
                    if col_name not in table_cols[tbl]:
                        table_cols[tbl].append(col_name)
                    intra_formula[r["derive"]].append(col_name)
                else:
                    reg(d)
        elif t == "count":
            reg(r["derive"])
            # where= clause attrs belong to the child/source table
            src = r["source"]
            for wc in r.get("where_cols", []):
                if wc not in table_cols[src]:
                    table_cols[src].append(wc)
        elif t == "sum":
            # where= clause attrs belong to the child/source table
            src_t = _cls(r["source"])
            for wc in r.get("where_cols", []):
                if wc not in table_cols[src_t]:
                    table_cols[src_t].append(wc)

    return table_cols, intra_formula


def infer_trigger(rules, fk_parents):
    derived_by_agg   = {_cls(r["derive"]) for r in rules if r["type"] in ("sum","count")}
    has_formula_copy = {_cls(r["derive"]) for r in rules if r["type"] in ("formula","copy")}
    candidates = has_formula_copy - derived_by_agg
    if not candidates:
        tables = tables_in_rules(rules)
        ranks  = topo_rank(tables, fk_parents)
        if ranks:
            max_rank   = max(ranks.values())
            candidates = {t for t, r in ranks.items() if r == max_rank}
    if candidates:
        counts = defaultdict(int)
        for r in rules:
            if r["type"] in ("formula","copy"):
                counts[_cls(r["derive"])] += 1
        return max(candidates, key=lambda t: counts.get(t, 0))
    return None


# ── DOT builder ───────────────────────────────────────────────────────────────

def build_dot(rules, project_name, fk_edges, fk_parents, req_label=None):

    involved_tables  = tables_in_rules(rules)
    table_cols, intra_formula = cols_in_rules(rules)
    constraint_tbls  = {r["entity"] for r in rules if r["type"] == "constraint"}
    event_rules      = [r for r in rules if r["type"] == "event"]

    visible_fks = [(c, cc, p, pc) for (c, cc, p, pc) in fk_edges
                   if c in involved_tables and p in involved_tables]

    ranks = topo_rank(involved_tables, fk_parents, all_fk_parents=fk_parents)
    rank_groups = defaultdict(list)
    for t, r in ranks.items():
        rank_groups[r].append(t)

    # causal order: copy → formula → sum/count (deepest child first)
    sums_counts = [r for r in rules if r["type"] in ("sum","count")]
    sums_counts.sort(key=lambda r: -ranks.get(_cls(r["source"]), 0))
    chain_rules = (
        [r for r in rules if r["type"] == "copy"] +
        [r for r in rules if r["type"] == "formula"] +
        sums_counts
    )

    trigger_table = infer_trigger(rules, fk_parents)

    title = f"Logic Diagram — {project_name}"
    if req_label:
        title += f"  [{req_label}]"

    # Choose layout direction based on table count.
    # TB (top-to-bottom): good for small diagrams — wide ranks, compact height.
    # LR (left-to-right): better for large diagrams — hierarchy flows left→right,
    #   fewer nodes share a rank, so the diagram is tall rather than very wide.
    n_tables = len(involved_tables)
    rankdir  = 'LR' if n_tables > 6 else 'TB'
    nodesep  = 0.35 if rankdir == 'LR' else 0.9
    ranksep  = 0.7 if rankdir == 'LR' else 1.1

    lines = []
    w = lines.append

    w('digraph logic {')
    w(f'  graph [rankdir={rankdir}, fontname="Helvetica", fontsize=13,')
    w(f'         label=<<B>{title}</B>>, labelloc=t,')
    w(f'         pad=0.4, nodesep={nodesep:.2f}, ranksep={ranksep:.2f}, bgcolor="white",')
    w(f'         splines=spline]')
    w(f'  node  [fontname="Helvetica", fontsize=11, shape=plaintext]')
    w(f'  edge  [fontname="Helvetica", fontsize=10]')
    w('')

    # ── trigger node ──────────────────────────────────────────────────────────
    if trigger_table:
        w('  // ── trigger ─────────────────────────────────────────────────────')
        w(f'  TRIGGER [label=<<TABLE BORDER="2" CELLBORDER="0" CELLPADDING="5" '
          f'BGCOLOR="{C_TRIGGER_FILL}" COLOR="{C_TRIGGER_BORD}">'
          f'<TR><TD><FONT COLOR="{C_TRIGGER_BORD}"><B>&#9889; {trigger_table} inserted</B>'
          f'</FONT></TD></TR></TABLE>>, shape=plaintext]')
        w('')

    # ── schema nodes ──────────────────────────────────────────────────────────
    # Each column row: [narrow port_w cell][attr name — with formula annotation][narrow port_e cell]
    w('  // ── schema layer ──────────────────────────────────────────────────')
    for table in sorted(involved_tables):
        cols         = table_cols.get(table, [])
        border_color = C_CONSTRAINT if table in constraint_tbls else C_TABLE_FILL
        border_width = 3 if table in constraint_tbls else 1

        # header spans all 3 columns
        col_rows = (f'<TR>'
                    f'<TD COLSPAN="3" BGCOLOR="{C_TABLE_FILL}">'
                    f'<FONT COLOR="{C_TABLE_FONT}"><B> {table} </B></FONT>'
                    f'</TD></TR>')

        # build calling= name lookup for annotation: derive -> function name
        calling_map = {r["derive"]: r["calling"].split(".")[-1]
                       for r in rules if r["type"] == "formula" and r.get("calling")}

        # build "feeds" lookup: col -> list of (seq, derived_col_short)
        # so plain input cols can show "→ amount (2)" inline
        feeds_map = defaultdict(list)
        for seq_r, r in enumerate(chain_rules, 1):
            if r["type"] == "formula":
                dst = r["derive"]
                dst_short = _col(dst)
                plain_intra_deps = [
                    d for d in r["deps"]
                    if _cls(d) == _cls(dst) and d != dst
                    and d not in {r2["derive"] for r2 in rules if r2["type"] in ("sum","count","formula")}
                ]
                for dep in plain_intra_deps:
                    feeds_map[dep].append((seq_r, dst_short))

        for c in cols:
            port   = _port(f"{table}.{c}")
            port_w = port + "_w"
            port_e = port + "_e"

            # formula annotation — prefer "= _func(row)" for calling= rules,
            # fall back to "= f(a, b)" for inline lambdas with few deps
            ann = ""
            full_col = f"{table}.{c}"
            # find matching formula rule for this column
            formula_rule = next((r for r in rules
                                 if r["type"] == "formula" and r["derive"] == full_col), None)
            if full_col in calling_map:
                fn = calling_map[full_col]
                ann = (f' <FONT COLOR="{C_FORMULA_ANN}" POINT-SIZE="9">'
                       f'= {fn}(row)</FONT>')
            elif formula_rule and formula_rule.get("expr"):
                expr = formula_rule["expr"]
                # cap length for readability
                if len(expr) > 30:
                    expr = expr[:27] + "..."
                ann = (f' <FONT COLOR="{C_FORMULA_ANN}" POINT-SIZE="9">'
                       f'= {expr}</FONT>')
            elif full_col in intra_formula:
                deps = intra_formula[full_col][:3]
                deps_str = ", ".join(deps)
                ann = (f' <FONT COLOR="{C_FORMULA_ANN}" POINT-SIZE="9">'
                       f'= f({deps_str})</FONT>')

            # input col feed annotation in right port cell: "→ amount (2)"
            feed_ann = ""
            if full_col in feeds_map:
                targets = feeds_map[full_col]
                feed_ann = "  ".join(f"&#8594;{dst}({seq_r})"
                                     for seq_r, dst in targets)

            col_rows += (
                f'<TR>'
                f'<TD PORT="{port_w}" WIDTH="6" HEIGHT="18" BGCOLOR="{C_PORT_FILL}"> </TD>'
                f'<TD PORT="{port}" ALIGN="LEFT" BGCOLOR="{C_COL_FILL}" CELLPADDING="3">'
                f'<FONT COLOR="{C_COL_FONT}"> {c} </FONT>{ann}</TD>'
                f'<TD PORT="{port_e}" WIDTH="6" HEIGHT="18" BGCOLOR="{C_PORT_FILL}"> </TD>'
                f'</TR>'
            )

        if not cols:
            col_rows += (f'<TR><TD></TD>'
                         f'<TD BGCOLOR="{C_COL_FILL}"><FONT COLOR="{C_COL_FONT}">  </FONT></TD>'
                         f'<TD></TD></TR>')

        label = (f'<<TABLE BORDER="{border_width}" CELLBORDER="0" CELLSPACING="0" '
                 f'COLOR="{border_color}">{col_rows}</TABLE>>')
        w(f'  {table} [label={label}]')

    # ── rank hints ────────────────────────────────────────────────────────────
    w('  // ── rank groupings ────────────────────────────────────────────────')
    if trigger_table:
        rank_groups[ranks.get(trigger_table, 0)].append('TRIGGER')

    max_rank = max(rank_groups.keys()) if rank_groups else 0
    for rank_level in sorted(rank_groups.keys()):
        members = rank_groups[rank_level]
        # TB layout: rank=min = top, rank=max = bottom.
        # Parents (rank 0) → top (min), deepest children/trigger → bottom (max).
        if rank_level == 0:
            kw = "min"        # parents at top
        elif rank_level == max_rank:
            kw = "max"        # trigger/children at bottom
        else:
            kw = "same"
        w(f'  {{ rank={kw}; {"; ".join(members)} }}')

    w('')

    # ── FK lines — very faint, passive (constraint=false) ─────────────────────
    if visible_fks:
        w('  // ── FK relationships ───────────────────────────────────────────')
        for (child, child_col, parent, parent_col) in visible_fks:
            w(f'  {child} -> {parent} [color="{C_FK}", style=solid, '
              f'arrowhead=none, arrowtail=crow, dir=both, '
              f'penwidth=0.7, constraint=false, weight=1]')
        w('')

    # ── trigger edge ──────────────────────────────────────────────────────────
    if trigger_table:
        w('  // ── trigger edge ──────────────────────────────────────────────')
        w(f'  TRIGGER -> {trigger_table} [color="{C_TRIGGER_BORD}", '
          f'style=bold, arrowhead=vee, penwidth=2, weight=10]')
        w('')

    # ── logic edges — number only on arrow, description in legend ─────────────
    w('  // ── logic edges ────────────────────────────────────────────────────')

    # Track intra-arc count per table so post-processor can stagger bulge distances
    intra_arc_index = defaultdict(int)   # table -> count of arcs emitted so far

    for seq, r in enumerate(chain_rules, 1):
        t = r["type"]

        if t == "copy":
            # LEFT side (_w): parent→child, hierarchy flow
            src_t  = _cls(r["source"])
            src_pw = _port(r["source"]) + "_w"
            dst_t  = _cls(r["derive"])
            dst_pw = _port(r["derive"]) + "_w"
            w(f'  {src_t}:{src_pw} -> {dst_t}:{dst_pw} '
              f'[label="{seq}", color="{C_FLOW}", fontcolor="{C_FLOW}", '
              f'arrowhead=vee, penwidth=1.8, weight=8]')

        elif t == "formula":
            # RIGHT side (_e): cross-table formula deps
            dst_t  = _cls(r["derive"])
            dst_pe = _port(r["derive"]) + "_e"
            derived_cols = {r2["derive"] for r2 in rules if r2["type"] in ("sum","count","formula")}
            cross_deps = [d for d in r["deps"] if _cls(d) != dst_t]
            intra_derived_deps = list(dict.fromkeys(
                d for d in r["deps"]
                if _cls(d) == dst_t and d != r["derive"] and d in derived_cols
            ))
            plain_intra = list(dict.fromkeys(
                d for d in r["deps"]
                if _cls(d) == dst_t and d != r["derive"] and d not in derived_cols
            ))
            intra_plain_single = [plain_intra[-1]] if plain_intra else []
            for dep in cross_deps:
                dep_t  = _cls(dep)
                dep_pe = _port(dep) + "_e"
                w(f'  {dep_t}:{dep_pe} -> {dst_t}:{dst_pe} '
                  f'[label="{seq}", color="{C_FLOW_LIGHT}", fontcolor="{C_FLOW_LIGHT}", '
                  f'arrowhead=vee, penwidth=1.5, style=dashed, weight=8]')
            # Derived and plain intra-table arcs:
            # Graphviz silently drops self-loop edges with constraint=false on spline layouts.
            # Instead we record them for the SVG post-processor to inject directly.
            # Format: "INTRA:<table>:<src_col>:<dst_col>:<seq>:<arc_idx>"
            if intra_derived_deps:
                dep     = intra_derived_deps[0]
                src_col = _col(dep)
                dst_col = _col(r["derive"])
                arc_idx = intra_arc_index[dst_t]
                intra_arc_index[dst_t] += 1
                w(f'  // INTRA:{dst_t}:{src_col}:{dst_col}:{seq}:{arc_idx}')

            if intra_plain_single:
                dep     = intra_plain_single[0]
                src_col = _col(dep)
                dst_col = _col(r["derive"])
                arc_idx = intra_arc_index[dst_t]
                intra_arc_index[dst_t] += 1
                w(f'  // INTRA:{dst_t}:{src_col}:{dst_col}:{seq}:{arc_idx}')

        elif t == "sum":
            # LEFT side (_w): child→parent, upward aggregation
            src_t  = _cls(r["source"])
            src_pw = _port(r["source"]) + "_w"
            dst_t  = _cls(r["derive"])
            dst_pw = _port(r["derive"]) + "_w"
            w(f'  {src_t}:{src_pw} -> {dst_t}:{dst_pw} '
              f'[label="{seq}", color="{C_FLOW}", fontcolor="{C_FLOW}", '
              f'arrowhead=vee, penwidth=2, style=dashed, weight=8]')

        elif t == "count":
            # LEFT side (_w): child table → parent _w, upward aggregation
            dst_t  = _cls(r["derive"])
            dst_pw = _port(r["derive"]) + "_w"
            src_t  = r["source"]
            w(f'  {src_t} -> {dst_t}:{dst_pw} '
              f'[label="{seq}", color="{C_FLOW}", fontcolor="{C_FLOW}", '
              f'arrowhead=vee, penwidth=2, style=dashed, weight=8, tailport=w]')

    # ── event nodes — clustered on right ──────────────────────────────────────
    if event_rules:
        w('')
        w('  // ── events (right cluster) ─────────────────────────────────────')
        w('  subgraph cluster_events {')
        w(f'    style=invis')   # invisible cluster border — just controls placement
        for r in event_rules:
            fn   = re.sub(r'[^A-Za-z0-9_]', '_', r['calling'].split('.')[-1])
            sink = 'evt_' + fn
            kind = (r['kind'].replace('after_flush_row_event', 'after_flush')
                             .replace('commit_row_event', 'commit')
                             .replace('early_row_event', 'early'))
            w(f'    {sink} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLPADDING="4" '
              f'BGCOLOR="{C_TRIGGER_FILL}" COLOR="{C_TRIGGER_BORD}">'
              f'<TR><TD><FONT COLOR="{C_EVENT}" POINT-SIZE="10">&#9889; {fn}</FONT>'
              f'</TD></TR></TABLE>>, shape=plaintext]')
        w('  }')
        for r in event_rules:
            fn   = re.sub(r'[^A-Za-z0-9_]', '_', r['calling'].split('.')[-1])
            sink = 'evt_' + fn
            kind = (r['kind'].replace('after_flush_row_event', 'after_flush')
                             .replace('commit_row_event', 'commit')
                             .replace('early_row_event', 'early'))
            w(f'  {r["on"]} -> {sink} '
              f'[label="{kind}", color="{C_EVENT}", style=dashed, '
              f'arrowhead=open, penwidth=1.2, fontcolor="{C_EVENT}", constraint=false]')

    # Legend removed — rule summary is in logic_flow_*.md instead

    w('}')
    return "\n".join(lines)


# ── Logic flow markdown builder ───────────────────────────────────────────────

def build_logic_flow_md(rules, files, project_name, svg_path, ranks,
                        requirement=None, svg_rel=None):
    """
    Build logic_flow_<project>[_<req>].md — a human-readable summary of the rule chain.

    Content:
      - Inline SVG diagram
      - Numbered rule summary (one line per rule)
        * Simple rules: natural expression  e.g. "balance = sum(amount_total where unshipped)"
        * calling= rules: func_name + first docstring line (or mechanical fallback)
      - Generation timestamp
    """
    from datetime import datetime

    import ast as _ast

    # Build a src lookup: func_name -> src text (for docstring scanning)
    # Also collect module-level docstrings as the NL requirements
    src_by_func = {}
    nl_specs = []   # list of (filename, docstring)
    for path, rel in files:
        src = path.read_text(encoding='utf-8')
        for m in re.finditer(r'def\s+(\w+)\s*\(', src):
            src_by_func[m.group(1)] = src
        try:
            tree = _ast.parse(src)
            doc  = _ast.get_docstring(tree)
            if doc and doc.strip():
                nl_specs.append((path.stem, doc.strip()))
        except SyntaxError:
            pass

    # Causal ordering same as diagram
    sums_counts = [r for r in rules if r["type"] in ("sum","count")]
    sums_counts.sort(key=lambda r: -ranks.get(_cls(r["source"]), 0))
    chain = (
        [r for r in rules if r["type"] == "copy"] +
        [r for r in rules if r["type"] == "formula"] +
        sums_counts
    )
    events      = [r for r in rules if r["type"] == "event"]
    constraints = [r for r in rules if r["type"] == "constraint"]

    def short(dotted):
        parts = dotted.split('.')
        return parts[-1] if len(parts) > 1 else dotted

    def where_str(r):
        """Abbreviate where= clause for sum/count."""
        wc = r.get("where_cols", [])
        if wc:
            return f" where {', '.join(wc)}"
        return ""

    lines = []
    seq = 0

    for r in chain:
        seq += 1
        t = r["type"]
        if t == "copy":
            lines.append(f"{seq}. `{short(r['derive'])} = copy({short(r['source'])})`")
        elif t == "formula":
            calling = r.get("calling", "")
            expr    = r.get("expr", "")
            if calling:
                fn = calling.split(".")[-1]
                doc = _scan_function_docstring(src_by_func.get(fn, ""), fn)
                if not doc:
                    # mechanical fallback: list the key deps
                    deps = list(dict.fromkeys(short(d) for d in r["deps"]))[:4]
                    doc = f"derives {short(r['derive'])} from {', '.join(deps)}"
                lines.append(f"{seq}. `{short(r['derive'])} = {fn}(row)` — {doc}")
            elif expr:
                e = expr if len(expr) <= 50 else expr[:47] + "..."
                lines.append(f"{seq}. `{short(r['derive'])} = {e}`")
            else:
                deps = list(dict.fromkeys(short(d) for d in r["deps"]))[:3]
                lines.append(f"{seq}. `{short(r['derive'])} = f({', '.join(deps)})`")
        elif t == "sum":
            lines.append(f"{seq}. `{short(r['derive'])} = sum({short(r['source'])}{where_str(r)})`")
        elif t == "count":
            lines.append(f"{seq}. `{short(r['derive'])} = count({r['source']}{where_str(r)})`")

    for r in constraints:
        lines.append(f"C. constraint: `{r['entity']}`")

    for r in events:
        fn   = r['calling'].split('.')[-1]
        kind = r['kind'].replace('_row_event','').replace('after_flush','after_flush')
        doc  = _scan_function_docstring(src_by_func.get(fn, ""), fn)
        suffix = f" — {doc}" if doc else ""
        lines.append(f"E. `{r['on']}` → `{fn}` ({kind}){suffix}")

    # Assemble markdown
    title = f"Logic Flow — {project_name}"
    if requirement:
        title += f" [{requirement}]"

    svg_name = svg_rel if svg_rel else svg_path.name
    rule_block = "\n".join(lines) if lines else "_No rules found._"

    scope_note = ""
    if requirement:
        scope_note = f"\n> Scoped to requirement: **{requirement}**\n"

    # NL requirements section — one block per file that has a module docstring
    req_section = ""
    if nl_specs:
        parts = []
        for stem, doc in nl_specs:
            # skip generic/template files
            if "use_case" in stem or "declare_logic" in stem:
                continue
            parts.append(f"```\n{doc}\n```")
        if parts:
            req_section = "## Requirements\n\n" + "\n\n".join(parts) + "\n\n"

    md = f"""# {title}
{scope_note}
{req_section}![logic flow]({svg_name})

## Rules

{rule_block}

---
_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}_
"""
    return md


# ── SVG post-processor ────────────────────────────────────────────────────────

def _postprocess_svg(svg_path: Path, dot_path: Path = None):
    """
    Three fixes applied to the rendered SVG:

    1. Feed-annotation text ("→col(n)") — move outside node right edge.
       Graphviz renders HTML table cell content inside the bounding box; we
       shift these small labels just past the right border.

    2. Intra-table arcs (sentinel colour #445544) — replace the big Graphviz
       self-loop path with a tight bezier that curves within the node, going

    3. Viewbox crop — recompute viewBox/width/height from the actual drawn
       element bounds so excess Graphviz pad whitespace is eliminated.
       from the source row's right edge up to the dest row's right edge.
    """
    import xml.etree.ElementTree as ET
    import re as _re

    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

    tree  = ET.parse(svg_path)
    root  = tree.getroot()
    SVG   = 'http://www.w3.org/2000/svg'
    INTRA = '#445544'

    # ── helper: bounding box of a node <g> from its polygons ─────────────────
    def node_bbox(g):
        xs, ys = [], []
        for poly in g.iter(f'{{{SVG}}}polygon'):
            for pair in poly.get('points', '').split():
                try:
                    x, y = pair.split(',')
                    xs.append(float(x)); ys.append(float(y))
                except ValueError:
                    pass
        if not xs:
            return None
        return min(xs), max(xs), min(ys), max(ys)   # x_min, x_max, y_min, y_max

    # ── collect node bboxes keyed by their title text ─────────────────────────
    node_boxes = {}   # table_name -> (x_min, x_max, y_min, y_max)
    for g in root.iter(f'{{{SVG}}}g'):
        if g.get('class') != 'node':
            continue
        bb = node_bbox(g)
        if bb is None:
            continue
        # first bold text is the table header
        for t in g.iter(f'{{{SVG}}}text'):
            txt = (t.text or '').strip()
            if txt:
                node_boxes[txt] = bb
                break

    # ── helper: row centre-y for a text label within a node ──────────────────
    def row_y_in_node(g, col_name):
        """Return the centre y of the row whose label matches col_name."""
        for t in g.iter(f'{{{SVG}}}text'):
            if (t.text or '').strip() == col_name:
                return float(t.get('y', 0))
        return None

    # ── build map: (src_col, dst_col) -> (src_y, dst_y, right_x) per node ─────
    # We need this to replace intra-arc paths.
    # We'll populate it lazily from the edge <title> elements.

    # ── 1. Move feed-annotation text outside node ─────────────────────────────
    moved_text = 0
    for g in root.iter(f'{{{SVG}}}g'):
        if g.get('class') != 'node':
            continue
        bb = node_bbox(g)
        if bb is None:
            continue
        x_min, x_max, y_min, y_max = bb
        for text_el in list(g.iter(f'{{{SVG}}}text')):
            full = (text_el.text or '') + ''.join((c.text or '') for c in text_el)
            if '→' not in full:
                continue
            text_el.set('x', str(round(x_max + 6, 2)))
            text_el.set('text-anchor', 'start')
            moved_text += 1

    # ── 2. Inject intra-table arcs directly into SVG ─────────────────────────
    # Graphviz silently drops self-loop edges with constraint=false on spline layouts.
    # We read INTRA directives from the .dot comments and inject SVG paths directly.

    # Build node geometry: table_name -> (right_x, {col_name -> mid_y})
    node_geom = {}
    for ng in root.iter(f'{{{SVG}}}g'):
        if ng.get('class') != 'node':
            continue
        tname = None
        for t in ng.iter(f'{{{SVG}}}text'):
            txt = (t.text or '').strip()
            if txt and not txt.startswith('=') and not txt.startswith('→'):
                tname = txt
                break
        if not tname:
            continue
        bb = node_bbox(ng)
        if not bb:
            continue
        right_x = bb[1]
        col_y = {}
        for t in ng.iter(f'{{{SVG}}}text'):
            txt = (t.text or '').strip()
            if txt and txt != tname and not txt.startswith('=') and not txt.startswith('→') and '.' not in txt:
                try:
                    col_y[txt] = float(t.get('y', 0))
                except ValueError:
                    pass
        node_geom[tname] = (right_x, col_y)

    # Parse INTRA directives from dot source
    intra_directives = []
    if dot_path and dot_path.exists():
        for line in dot_path.read_text(encoding='utf-8').splitlines():
            m = _re.match(r'\s*//\s*INTRA:(\w+):(\w+):(\w+):(\d+):(\d+)', line)
            if m:
                intra_directives.append((
                    m.group(1), m.group(2), m.group(3),
                    int(m.group(4)), int(m.group(5))
                ))

    # Find SVG graph group to inject into
    graph_g = next(
        (g for g in root.iter(f'{{{SVG}}}g') if g.get('class') == 'graph'),
        root
    )

    tightened = 0
    max_intra_x = 0.0   # track rightmost extent reached by injected arcs + labels
    for (table, src_col, dst_col, seq, arc_idx) in intra_directives:
        if table not in node_geom:
            continue
        right_x, col_y = node_geom[table]
        if src_col not in col_y or dst_col not in col_y:
            continue

        src_y = col_y[src_col]
        dst_y = col_y[dst_col]
        # dst (derived col) should be higher on screen = smaller y value

        base_x = right_x
        bulge  = 22 + arc_idx * 24   # stagger: 22, 46, 70 ... wider fan
        mid_y  = (src_y + dst_y) / 2

        d = (f'M{base_x},{src_y} '
             f'C{base_x+bulge},{src_y} '
             f'{base_x+bulge},{dst_y} '
             f'{base_x},{dst_y}')

        path_el = ET.SubElement(graph_g, f'{{{SVG}}}path')
        path_el.set('d', d)
        path_el.set('stroke', INTRA)
        path_el.set('stroke-width', '1.2')
        path_el.set('fill', 'none')

        s = 4
        poly_el = ET.SubElement(graph_g, f'{{{SVG}}}polygon')
        poly_el.set('points', f'{base_x},{dst_y} {base_x+s},{dst_y-s} {base_x+s},{dst_y+s}')
        poly_el.set('stroke', INTRA)
        poly_el.set('fill', INTRA)

        label_x = base_x + bulge + 3
        text_el = ET.SubElement(graph_g, f'{{{SVG}}}text')
        text_el.set('x', str(round(label_x, 1)))
        text_el.set('y', str(round(mid_y + 4, 1)))
        text_el.set('font-family', 'Helvetica,sans-Serif')
        text_el.set('font-size', '10')
        text_el.set('fill', INTRA)
        text_el.text = str(seq)

        # reserve room for the label text (~7pt per digit, generous for 1-2 digit seq numbers)
        max_intra_x = max(max_intra_x, label_x + 7 * len(str(seq)))

        tightened += 1

    # ── crop viewBox to remove Graphviz pad whitespace ────────────────────────

    # Graphviz pad=0.4in = 28.8pt on every side.  Crop it down to a small border
    # by shrinking the viewBox inward and reducing width/height to match.
    # We work in Graphviz's own coordinate system (no transform manipulation needed).
    try:
        orig_w = float(root.get('width',  '0').replace('pt',''))
        orig_h = float(root.get('height', '0').replace('pt',''))
        vb     = root.get('viewBox', '').split()
        if len(vb) == 4 and orig_w > 0 and orig_h > 0:
            vx, vy, vw, vh = float(vb[0]), float(vb[1]), float(vb[2]), float(vb[3])
            KEEP = 10.0   # pt border to keep on each side (was 28.8)
            TRIM = 28.8 - KEEP   # how much to trim per side
            new_vx = vx + TRIM
            new_vy = vy + TRIM
            new_vw = vw - 2 * TRIM
            new_vh = vh - 2 * TRIM
            # Injected intra-table arcs (and their labels) can extend past graphviz's
            # own right edge, since graphviz never laid them out — widen the canvas
            # to cover them instead of letting the crop clip them off.
            if max_intra_x > 0:
                needed_w = (max_intra_x - vx) + KEEP
                new_vw = max(new_vw, needed_w)
            if new_vw > 0 and new_vh > 0:
                root.set('viewBox', f'{new_vx:.2f} {new_vy:.2f} {new_vw:.2f} {new_vh:.2f}')
                root.set('width',  f'{new_vw:.0f}pt')
                root.set('height', f'{new_vh:.0f}pt')
    except (ValueError, AttributeError):
        pass

    tree.write(svg_path, encoding='unicode', xml_declaration=False)

    return moved_text, tightened


# ── main ──────────────────────────────────────────────────────────────────────

def generate(project_name: str, requirement: str = None, manager_root: Path = None):
    if manager_root is None:
        manager_root = Path.cwd()

    project_dir = manager_root / project_name
    if not project_dir.exists():
        print(f"ERROR: project not found: {project_dir}")
        sys.exit(1)

    fk_edges, fk_parents = parse_dbml(project_dir)
    files = find_logic_files(project_dir, requirement)
    if not files:
        print(f"No logic files found matching '{requirement}'")
        sys.exit(0)

    rules = parse_rules(files)
    if not rules:
        print("No rules found.")
        sys.exit(0)

    dot_src = build_dot(rules, project_name, fk_edges, fk_parents, req_label=requirement)

    # ── output layout ──────────────────────────────────────────────────────────
    # Scoped:  docs/requirements/<requirement>/
    #            logic_flow_<requirement>.md        ← human-readable summary
    #            logic_diagrams/
    #              logic_diagram_<requirement>.svg
    #              logic_diagram_<requirement>.dot
    #
    # Full:    docs/requirements/
    #            logic_flow_<project>.md
    #            logic_diagrams/
    #              logic_diagram.svg
    #              logic_diagram.dot
    req_dir = project_dir / "docs" / "requirements"
    if requirement:
        req_dir = req_dir / requirement
    diag_dir = req_dir / "logic_diagrams"
    diag_dir.mkdir(parents=True, exist_ok=True)

    suffix   = f"_{requirement}" if requirement else ""
    dot_path = diag_dir / f"logic_diagram{suffix}.dot"
    svg_path = diag_dir / f"logic_diagram{suffix}.svg"

    dot_path.write_text(dot_src, encoding="utf-8")

    result = subprocess.run(
        ["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR running dot:\n{result.stderr}")
        sys.exit(1)

    moved_text, tightened = _postprocess_svg(svg_path, dot_path)
    if moved_text or tightened:
        print(f"   (post-processed: {moved_text} feed labels moved, {tightened} arcs tightened)")

    # ── generate logic_flow md ────────────────────────────────────────────────
    involved_tables = tables_in_rules(rules)
    ranks = topo_rank(involved_tables, fk_parents, all_fk_parents=fk_parents)

    project_basename = Path(project_name).name   # strip any subdirectory prefix (e.g. "samples/demo_emp_types")
    flow_name = f"logic_flow_{requirement}.md" if requirement else f"logic_flow_{project_basename}.md"
    flow_path = req_dir / flow_name
    # SVG ref is relative from flow_path to svg_path
    svg_rel   = f"logic_diagrams/{svg_path.name}"
    flow_md = build_logic_flow_md(rules, files, project_name, svg_path,
                                   ranks, requirement=requirement,
                                   svg_rel=svg_rel)
    flow_path.write_text(flow_md, encoding="utf-8")
    print(f"   logic flow → {flow_path.relative_to(project_dir)}")

    print(f"✅  {svg_path}")
    print(f"   {len(rules)} rules across {len(files)} file(s)"
          + (f"  [filter: {requirement}]" if requirement else ""))
    return svg_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python logic_diagram_gv.py <project> [<requirement>]")
        sys.exit(1)
    req = sys.argv[2] if len(sys.argv) > 2 else None
    generate(sys.argv[1], req)
