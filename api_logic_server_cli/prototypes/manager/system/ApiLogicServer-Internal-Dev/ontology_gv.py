#!/usr/bin/env python3
"""
ontology_gv.py - generate an ontology, SHACL shapes and column lineage for a GenAI-Logic project.

Usage (from the Manager root):
    python system/ApiLogicServer-Internal-Dev/ontology_gv.py <project_name> [--no-validate]

Reads (deterministic, no AI, no running server):
    database/models.py                 classes, columns, foreign keys
    ui/admin/admin.yaml                subtype groups (show_when), as the logic diagram does
    logic/logic_discovery/**/*.py      every Rule.* call, its dependencies, its requirement text

Writes docs/ontology/:
    genai-logic.ttl            the shared vocabulary for rules (gl:)           - same for every project
    <project>.ttl              OWL: classes, subtypes (defined classes), properties, rules as individuals
    <project>.shapes.ttl       SHACL: constraints expressed as shapes where the pattern allows
    <project>.html             plain-English page: model, subtypes, rules, lineage, validation
    lineage.csv, lineage.json  column-level lineage (which columns feed which)

Needs no packages to generate. If rdflib (and pyshacl) are installed, the files are parsed and the
project's own data (database/db.sqlite) is validated against the shapes; otherwise that step is skipped.

version: 1.0 (Nov 3 2026)
"""

import ast
import csv
import html
import json
import re
import sqlite3
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

BASE = "https://apilogicserver.github.io/ontology/"
GL_NS = BASE + "genai-logic#"
RULE_CALLS = {"sum", "count", "formula", "copy", "constraint", "commit_constraint"}
XSD = {"Text": "string", "String": "string", "Integer": "integer", "Float": "double", "Numeric": "decimal",
       "DECIMAL": "decimal", "DateTime": "dateTime", "Date": "date", "Boolean": "boolean"}
GL_CLASS = {"sum": "Sum", "count": "Count", "formula": "Formula", "copy": "Copy",
            "constraint": "Constraint", "commit_constraint": "Constraint"}


# ── models.py ──────────────────────────────────────────────────────────────────

def _call_name(call):
    f = call.func
    return f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")


def parse_models(path: Path):
    """class -> {table, cols: {attr: {type, fk_table, nullable, required}}, rels: {attr: (class, is_list)}}"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    classes = OrderedDict()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        table, cols, rels = None, OrderedDict(), {}
        for st in node.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                name = st.targets[0].id
                if name == "__tablename__":
                    table = st.value.value
                elif isinstance(st.value, ast.Call) and _call_name(st.value) == "Column":
                    kws = {k.arg: k.value for k in st.value.keywords}
                    typ, fk = "Text", None
                    for a in st.value.args:
                        if isinstance(a, ast.Call) and _call_name(a) == "ForeignKey":
                            fk = a.args[0].value.split(".")[0]
                        elif isinstance(a, ast.Call):
                            typ = _call_name(a)
                        elif isinstance(a, ast.Name):
                            typ = a.id
                    nullable = not (isinstance(kws.get("nullable"), ast.Constant) and kws["nullable"].value is False)
                    cols[name] = dict(type=typ, fk_table=fk, nullable=nullable,
                                      pk="primary_key" in kws, has_default="server_default" in kws)
            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and isinstance(st.value, ast.Call) \
                    and _call_name(st.value) == "relationship":
                text = ast.unparse(st.annotation)
                m = re.search(r'["\'](\w+)["\']', text)
                if m:
                    rels[st.target.id] = (m.group(1), "List[" in text)
        if table:
            classes[node.name] = dict(table=table, cols=cols, rels=rels)
    return classes


# ── subtype groups (same source as the logic diagram) ───────────────────────────

_RE_RES = re.compile(r"^  (\w+):\s*$")
_RE_ATTR = re.compile(r"^\s*-\s*name:\s*(\w+)\s*$")
_RE_SW = re.compile(r'show_when:\s*record\["(\w+)"\]\s*==\s*"(\w+)"')


def parse_admin_groups(project: Path):
    """table -> [(discriminator, value, [columns])] from admin.yaml show_when entries (2+ groups per table)."""
    p = project / "ui" / "admin" / "admin.yaml"
    if not p.exists():
        return {}
    groups = defaultdict(lambda: OrderedDict())
    res = attr = None
    in_res = in_attrs = False
    for line in p.read_text(encoding="utf-8").splitlines():
        if line == "resources:":
            in_res = True
            continue
        if not in_res:
            continue
        m = _RE_RES.match(line)
        if m:
            res, in_attrs = m.group(1), False
            continue
        s = line.strip()
        if s == "attributes:":
            in_attrs = True
            continue
        if res and in_attrs:
            m = _RE_ATTR.match(line)
            if m:
                attr = m.group(1)
                continue
            m = _RE_SW.search(line)
            if m and attr:
                groups[res].setdefault((m.group(1), m.group(2)), []).append(attr)
    return {t: [(d, v, cols) for (d, v), cols in g.items()] for t, g in groups.items() if len(g) >= 2}


def infer_subtype_groups(project):
    """
    Subtype groups (single-table inheritance) read from the rule code, so they need no admin.yaml.
    A column belongs to a group when every guarded read of it sits in that group's branch (`if row.type == 'hourly':`,
    code after `if row.type != 'hourly': return ...`, or a lambda like `row.type == 'hourly' or row.union_id is None`).
    A derived column whose formula branches over 2+ groups is shared; one whose same-table inputs all sit in one group joins it.
    Returns {table: OrderedDict[(discriminator column, value)] -> [columns, in model order]}, 2+ groups per table.
    """
    project = Path(project)
    cols_of = OrderedDict()
    tree = ast.parse((project / "database" / "models.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            cols = [st.targets[0].id for st in node.body if isinstance(st, ast.Assign) and len(st.targets) == 1
                    and isinstance(st.targets[0], ast.Name) and isinstance(st.value, ast.Call)
                    and getattr(st.value.func, "id", getattr(st.value.func, "attr", "")) == "Column"]
            if cols:
                cols_of[node.name] = cols
    ld = project / "logic" / "logic_discovery"
    files = sorted(p for p in ld.rglob("*.py") if p.name not in ("auto_discovery.py", "use_case.py", "__init__.py")
                   and "system" not in p.parts and "__pycache__" not in p.parts)
    evidence = defaultdict(set)      # (table, col) -> {(disc, value)} seen in guarded branches
    discs = defaultdict(set)         # table -> discriminator columns
    blocked = set()                  # (table, col) derived by a formula that branches over 2+ groups
    derived = []                     # (table, col, [same-table input cols])

    def _name(n):
        return n.attr if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "row" else None

    def _attrs(node, table, aliases):
        out = set()
        for n in ast.walk(node):
            c = _name(n)
            if c and c in cols_of.get(table, []):
                out.add(c)
        return out

    def _guards(test, table, aliases):
        """[(disc, value, positive)] for `row.col == 'v'` / `!= 'v'` (directly or through an alias) inside the test."""
        found = []
        for n in ast.walk(test):
            if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.comparators[0], ast.Constant) \
                    and isinstance(n.comparators[0].value, str) and isinstance(n.ops[0], (ast.Eq, ast.NotEq)):
                c = _name(n.left) or aliases.get(getattr(n.left, "id", None))
                if c in cols_of.get(table, []) and n.comparators[0].value != "no":
                    found.append((c, n.comparators[0].value, isinstance(n.ops[0], ast.Eq)))
        return found

    def _ends(stmts):
        return bool(stmts) and isinstance(stmts[-1], (ast.Return, ast.Raise))

    def _visit(stmts, table, aliases, group, seen):
        """group None = unguarded; a (disc, value) tuple = inside that subtype's branch; a [group] list = its complement."""
        for st in stmts:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name) and _name(st.value):
                aliases[st.targets[0].id] = _name(st.value)
            if isinstance(st, ast.If):
                gs = _guards(st.test, table, aliases)
                pos = [g for g in gs if g[2]]
                neg = [g for g in gs if not g[2]]
                for g in gs:
                    discs[table].add(g[0])
                if pos and not neg:
                    g = (pos[0][0], pos[0][1])
                    seen.add(g)
                    for c in _attrs(st.test, table, aliases) - {pos[0][0]}:
                        evidence[(table, c)].add(g)
                    _visit(st.body, table, aliases, g, seen)
                    _visit(st.orelse, table, aliases, [g], seen)
                    if _ends(st.body):
                        group = [g]
                elif neg and not pos and _ends(st.body):
                    g = (neg[0][0], neg[0][1])
                    seen.add(g)
                    for c in _attrs(st.test, table, aliases) - {neg[0][0]}:
                        evidence[(table, c)].add(g)
                    _visit(st.orelse, table, aliases, [g], seen)
                    group = g
                else:
                    _visit(st.body, table, aliases, group, seen)
                    _visit(st.orelse, table, aliases, group, seen)
                continue
            if isinstance(group, tuple):
                for c in _attrs(st, table, aliases):
                    evidence[(table, c)].add(group)
            elif isinstance(group, list):   # complement of a guard: `x is None` checks say the column belongs to the guard's group
                for n in ast.walk(st):
                    if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.ops[0], ast.Is) \
                            and isinstance(n.comparators[0], ast.Constant) and n.comparators[0].value is None \
                            and _name(n.left) in cols_of.get(table, []):
                        evidence[(table, _name(n.left))].add(group[0])
        return group

    for f in files:
        mod = ast.parse(f.read_text(encoding="utf-8"))
        funcs = {n.name: n for n in ast.walk(mod) if isinstance(n, ast.FunctionDef)}
        for call in [n for n in ast.walk(mod) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                     and isinstance(n.func.value, ast.Name) and n.func.value.id == "Rule"]:
            kw = {k.arg: k.value for k in call.keywords}
            if call.func.attr not in ("constraint", "commit_constraint", "formula", "sum", "count"):
                continue
            tgt = kw.get("derive") or kw.get("validate")
            parts = ast.unparse(tgt).replace("models.", "").split(".")
            table = parts[0] if call.func.attr in ("constraint", "commit_constraint") else parts[-2] if len(parts) > 1 else None
            if table not in cols_of:
                continue
            derive_col = parts[-1] if call.func.attr in ("formula", "sum", "count") else None
            callee = kw.get("calling")
            body = funcs.get(callee.id) if isinstance(callee, ast.Name) else kw.get("as_condition") or kw.get("as_expression")
            if body is None:
                continue
            seen = set()
            if isinstance(body, ast.FunctionDef):
                _visit(body.body, table, {}, None, seen)
            else:   # lambda: `row.type == 'hourly' or row.union_id is None`
                gs = _guards(body.body, table, {})
                for g in gs:
                    discs[table].add(g[0])
                    seen.add((g[0], g[1]))
                if len(gs) == 1:
                    for c in _attrs(body.body, table, {}) - {gs[0][0]}:
                        evidence[(table, c)].add((gs[0][0], gs[0][1]))
            if derive_col:
                if len(seen) >= 2:
                    blocked.add((table, derive_col))
                derived.append((table, derive_col, sorted(_attrs(body, table, {}) - {derive_col})))
    groups = defaultdict(OrderedDict)
    assigned = {}
    for (table, col), ev in evidence.items():
        if col not in discs[table] and len(ev) == 1 and (table, col) not in blocked and col != "id":
            assigned[(table, col)] = next(iter(ev))
    changed = True
    while changed:
        changed = False
        for table, col, ins in derived:
            if (table, col) in assigned or (table, col) in blocked or col in discs[table]:
                continue
            ins = [c for c in ins if c not in discs[table]]
            gs = {assigned.get((table, c)) for c in ins}
            if ins and None not in gs and len(gs) == 1:
                assigned[(table, col)] = gs.pop()
                changed = True
    for table, cols in cols_of.items():
        for col in cols:
            g = assigned.get((table, col))
            if g:
                groups[table].setdefault(g, []).append(col)
    return {t: g for t, g in groups.items() if len(g) >= 2}


# ── logic files ────────────────────────────────────────────────────────────────

def _dotted(node):
    parts = ast.unparse(node).split(".")
    return [p for p in parts if p != "models"]


def _row_attrs(node, rels_of_owner):
    """Attributes read from `row` in an AST: ('col',) or ('rel','col') for a parent hop."""
    found = []
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute):
            if isinstance(n.value, ast.Name) and n.value.id == "row":
                found.append((n.attr,))
            elif isinstance(n.value, ast.Attribute) and isinstance(n.value.value, ast.Name) \
                    and n.value.value.id == "row" and n.value.attr in rels_of_owner:
                found.append((n.value.attr, n.attr))
    return found


def parse_logic(project: Path, classes):
    ld = project / "logic" / "logic_discovery"
    files = sorted(p for p in ld.rglob("*.py")
                   if p.name not in ("auto_discovery.py", "use_case.py", "__init__.py") and "system" not in p.parts
                   and "__pycache__" not in p.parts)
    rules = []
    for f in files:
        src = f.read_text(encoding="utf-8")
        tree = ast.parse(src)
        doc = (ast.get_docstring(tree) or "")
        req_lines = []
        for ln in doc.splitlines():
            if re.match(r"^(version|created|created_by):", ln.strip()):
                break
            if ln.strip():
                req_lines.append(ln.strip())
        consts = {}
        for st in tree.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name) \
                    and isinstance(st.value, (ast.Tuple, ast.List)) and all(isinstance(e, ast.Constant) for e in st.value.elts):
                consts[st.targets[0].id] = [e.value for e in st.value.elts]
        funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and isinstance(n.func.value, ast.Name) and n.func.value.id == "Rule" and n.func.attr in RULE_CALLS]
        for c in sorted(calls, key=lambda n: n.lineno):
            kw = {k.arg: k.value for k in c.keywords}
            kind = c.func.attr
            r = dict(kind=kind, file=str(f.relative_to(project)), use_case=f.stem, req_lines=req_lines, consts=consts,
                     expr=" ".join(ast.get_source_segment(src, c).split()), deps=[], guards=[], pattern=None,
                     error_msg=None, derive=None, validate=None, where_attrs=[])
            owner = None
            if kind in ("sum", "count", "formula", "copy"):
                owner, col = _dotted(kw["derive"])[-2:]
                r["derive"] = (owner, col)
            else:
                owner = _dotted(kw["validate"])[-1]
                r["validate"] = owner
            rels_owner = classes.get(owner, {}).get("rels", {})
            body = None
            if kind in ("sum", "count"):
                srcn = kw.get("as_sum_of") or kw.get("as_count_of")
                parts = _dotted(srcn)
                child = parts[-2] if kind == "sum" else parts[-1]
                r["deps"].append((child, parts[-1] if kind == "sum" else None))
                if kw.get("where") is not None:
                    for a in _row_attrs(kw["where"], {}):
                        if a[0] in classes.get(child, {}).get("cols", {}):
                            r["deps"].append((child, a[0]))
            elif kind == "copy":
                parts = _dotted(kw["from_parent"])
                r["deps"].append((parts[-2], parts[-1]))
            else:
                callee = kw.get("calling")
                if isinstance(callee, ast.Name) and callee.id in funcs:
                    body = funcs[callee.id]
                    r["doc"] = ast.get_docstring(body)
                elif kw.get("as_condition") is not None:
                    body = kw["as_condition"]
                elif kw.get("as_expression") is not None:
                    body = kw["as_expression"]
                if body is not None:
                    for a in _row_attrs(body, rels_owner):
                        if len(a) == 1 and a[0] in classes.get(owner, {}).get("cols", {}):
                            r["deps"].append((owner, a[0]))
                        elif len(a) == 2:
                            tgt = rels_owner[a[0]][0]
                            r["deps"].append((tgt, a[1]))
                    for m in re.finditer(r"SysConfig\.current\([^)]*\)\.(\w+)", ast.unparse(body)):
                        r["deps"].append(("SysConfig", m.group(1)))
                if isinstance(kw.get("as_condition"), ast.Lambda):
                    r["pattern"] = match_pattern(kw["as_condition"].body, consts)
                r["body"] = body
            em = kw.get("error_msg")
            if isinstance(em, ast.Constant):
                r["error_msg"] = em.value
            seen, deps = set(), []
            for d in r["deps"]:
                if d not in seen and d != r["derive"]:
                    seen.add(d)
                    deps.append(d)
            r["deps"] = deps
            rules.append(r)
    for i, r in enumerate(rules, 1):
        r["id"] = f"rule_{i:02d}"
    return rules


def _row_col(n):
    return n.attr if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "row" else None


def _const_list(n, consts):
    if isinstance(n, ast.Name) and n.id in consts:
        return consts[n.id]
    if isinstance(n, (ast.Tuple, ast.List)) and all(isinstance(e, ast.Constant) for e in n.elts):
        return [e.value for e in n.elts]
    return None


def match_pattern(b, consts):
    """Translate the constraint shapes that SHACL can state; anything else stays descriptive."""
    if isinstance(b, ast.Compare) and len(b.ops) == 1:
        a, op, v = _row_col(b.left), b.ops[0], b.comparators[0]
        if a and isinstance(op, ast.In) and _const_list(v, consts) is not None:
            return ("in", a, _const_list(v, consts))
        if a and isinstance(op, ast.LtE) and _row_col(v):
            return ("lte", a, _row_col(v))
    if isinstance(b, ast.BoolOp) and isinstance(b.op, ast.Or) and len(b.values) == 2:
        x, y = b.values
        if isinstance(x, ast.Compare) and isinstance(y, ast.Compare) and len(x.ops) == len(y.ops) == 1:
            xa, ya = _row_col(x.left), _row_col(y.left)
            if xa and isinstance(x.ops[0], ast.Eq) and isinstance(x.comparators[0], ast.Constant) and ya:
                yc = y.comparators[0]
                if isinstance(y.ops[0], ast.Is) and isinstance(yc, ast.Constant) and yc.value is None:
                    return ("null_unless", xa, x.comparators[0].value, ya)
                if isinstance(y.ops[0], ast.Eq) and isinstance(yc, ast.Constant):
                    return ("value_unless", xa, x.comparators[0].value, ya, yc.value)
            if xa and isinstance(x.ops[0], ast.Is) and isinstance(x.comparators[0], ast.Constant) \
                    and x.comparators[0].value is None and ya == xa and isinstance(y.ops[0], ast.In) \
                    and _const_list(y.comparators[0], consts) is not None:
                return ("in", xa, _const_list(y.comparators[0], consts))
    return None


# ── requirement text and origin ────────────────────────────────────────────────

def _words(text):
    return {w.lower() for w in re.findall(r"[A-Za-z_]{5,}", text or "") if not w.startswith("row")}


def requirement_for(r, classes):
    """Best-matching requirement lines for a rule, and whether the requirement states it (specified) or not."""
    toks = set()
    if r["derive"]:
        toks.add(r["derive"][1])
    toks |= {c for (_, c) in r["deps"] if c}
    if r["pattern"] and r["pattern"][0] in ("in",):
        toks.add(r["pattern"][1])
    if r["pattern"] and r["pattern"][0] in ("null_unless", "value_unless"):
        toks.add(r["pattern"][3])
    stems = {w[:5] for w in _words(r["error_msg"])}
    best, lines = 0, []
    for ln in r["req_lines"]:
        score = sum(1 for t in toks if re.search(r"\b%s\b" % re.escape(t), ln))
        score += len({w[:5] for w in _words(ln)} & stems)
        if score > best:
            best, lines = score, [ln]
        elif score == best and score > 0:
            lines.append(ln)
    origin = "specified" if best > 0 else "inferred"
    p = r["pattern"]
    if p and p[0] in ("null_unless", "value_unless"):
        lines = [ln for ln in lines if re.search(r"\bonly\b", ln, re.I)] or lines
        origin = "specified" if any(re.search(r"\bonly\b", ln, re.I) for ln in lines) else "inferred"
    if p and p[0] == "in":
        origin = "specified" if any(re.search(r"\b%s\b" % re.escape(str(v)), ln) for ln in lines for v in p[2]) else "inferred"
    return (" / ".join(lines[:3]) if origin == "specified" else ""), origin


# ── model assembly ─────────────────────────────────────────────────────────────

def camel(s):
    return "".join(w.capitalize() for w in re.split(r"[_\s]+", s))


def build(project: Path):
    classes = parse_models(project / "database" / "models.py")
    rules = parse_logic(project, classes)
    admin = parse_admin_groups(project)
    merged = defaultdict(OrderedDict)  # table -> {(column, value): [columns]}; admin.yaml first, then inferred from the rules
    for table, gl in admin.items():
        for disc, val, gcols in gl:
            col = next((c for c in classes[table]["cols"] if c.lower() == disc.lower()), None)
            if col:
                merged[table].setdefault((col, val), []).extend(c for c in gcols if c not in merged[table].get((col, val), []))
    for table, groups in infer_subtype_groups(project).items():
        for key, cols in groups.items():
            have = merged[table].setdefault(key, [])
            have.extend(c for c in cols if c not in have and not any(c in v for v in merged[table].values()))
    admin = {t: [(c, v, cols) for (c, v), cols in g.items()] for t, g in merged.items() if len(g) >= 2}
    enums = {}  # (table, col) -> allowed values, from `in` constraints
    for r in rules:
        if r["pattern"] and r["pattern"][0] == "in":
            enums[(r["validate"], r["pattern"][1])] = r["pattern"][2]
    subtypes = []  # dicts: cls, base, col, value, columns
    disjoint = []
    for table, groups in admin.items():
        cols = classes[table]["cols"]
        by_disc = defaultdict(list)
        for disc, val, gcols in groups:
            col = next((c for c in cols if c.lower() == disc.lower()), None)
            if col:
                by_disc[col].append((val, gcols))
        for col, items in by_disc.items():
            allowed = enums.get((table, col)) or [v for v, _ in items]
            boolean = set(map(str, allowed)) <= {"yes", "no"}
            gcols_by_val = dict(items)
            members = []
            for val in ([v for v in allowed if str(v) != "no"] if boolean else allowed):
                name = (camel(col) if boolean else camel(str(val))) + table
                subtypes.append(dict(cls=name, base=table, col=col, value=val, columns=gcols_by_val.get(val, [])))
                members.append(name)
            if not boolean and len(members) > 1:
                disjoint.append(members)
    for r in rules:
        r["req"], r["origin"] = requirement_for(r, classes)
        r["applies"] = []
        body = r.get("body")
        if body is not None:
            for n in ast.walk(body):
                if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.comparators[0], ast.Constant):
                    c = _row_col(n.left)
                    for s in subtypes:
                        if c == s["col"] and n.comparators[0].value == s["value"] and s["cls"] not in r["applies"]:
                            r["applies"].append(s["cls"])
    return dict(classes=classes, rules=rules, subtypes=subtypes, disjoint=disjoint, project=project.name, enums=enums)


# ── Turtle ─────────────────────────────────────────────────────────────────────

def lit(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def pv(v):
    return str(v).lower() if isinstance(v, bool) else (str(v) if isinstance(v, (int, float)) else lit(v))


def P(cls, col):
    return f":{cls}.{col}"


def rule_label(r):
    if r["kind"] == "sum":
        return f"{r['derive'][0]}.{r['derive'][1]} = sum({r['deps'][0][0]}.{r['deps'][0][1]})"
    if r["kind"] == "count":
        return f"{r['derive'][0]}.{r['derive'][1]} = count({r['deps'][0][0]})"
    if r["kind"] == "copy":
        return f"{r['derive'][0]}.{r['derive'][1]} copied from {r['deps'][0][0]}.{r['deps'][0][1]}"
    if r["kind"] == "formula":
        return f"{r['derive'][0]}.{r['derive'][1]} derived by formula"
    msg = re.sub(r"\s*\([^)]*\{row\.[^)]*\)", "", r["error_msg"] or "")
    return re.sub(r"\s*\{row\.[^}]*\}", "", msg).strip() or f"{r['validate']} constraint"


def vocabulary_ttl():
    return f"""@prefix gl:   <{GL_NS}> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dct:  <http://purl.org/dc/terms/> .

# GenAI-Logic rule vocabulary. Shared by every project; generated by ontology_gv.py.
# Constraints are also expressed as SHACL shapes (see <project>.shapes.ttl); derivations have no standard equivalent.

<{BASE}genai-logic> a owl:Ontology ; dct:title "GenAI-Logic rule vocabulary" ;
    rdfs:comment "Declarative business rules (LogicBank) as linked, enforced governance artifacts: what they derive or validate, what they depend on, and the requirement behind them." .

gl:Rule a owl:Class ; rdfs:comment "An enforced, declarative rule. Fires on every commit, over every change path." .
gl:Derivation a owl:Class ; rdfs:subClassOf gl:Rule ; rdfs:comment "Rule that computes a property value." .
gl:Sum     a owl:Class ; rdfs:subClassOf gl:Derivation ; rdfs:comment "Parent total of a child property, adjusted by the delta of each change." .
gl:Count   a owl:Class ; rdfs:subClassOf gl:Derivation ; rdfs:comment "Parent count of child rows, adjusted by the delta of each change." .
gl:Formula a owl:Class ; rdfs:subClassOf gl:Derivation ; rdfs:comment "Value computed from the row's own and parent properties; re-derived when they change." .
gl:Copy    a owl:Class ; rdfs:subClassOf gl:Derivation ; rdfs:comment "Snapshot copy from a parent at insert time; not re-derived when the parent changes later." .
gl:Constraint a owl:Class ; rdfs:subClassOf gl:Rule ; rdfs:comment "Condition that must hold at every commit; a violation rejects the transaction." .

gl:derives   a owl:ObjectProperty ; rdfs:domain gl:Derivation ; rdfs:comment "The property this rule computes." .
gl:derivedBy a owl:ObjectProperty ; owl:inverseOf gl:derives ; rdfs:comment "The rule that computes this property." .
gl:validates a owl:ObjectProperty ; rdfs:domain gl:Constraint ; rdfs:comment "The class whose instances the constraint governs." .
gl:dependsOn a owl:ObjectProperty ; rdfs:domain gl:Rule ; rdfs:comment "A property (or class, for a count) the rule reads: its inputs in the dependency graph. This is column-level lineage." .
gl:appliesToType a owl:ObjectProperty ; rdfs:domain gl:Rule ; rdfs:comment "A subtype the rule is scoped to by a type guard." .
gl:shape a owl:ObjectProperty ; rdfs:domain gl:Constraint ; rdfs:comment "The SHACL shape that states this constraint." .
gl:requirement a owl:AnnotationProperty ; rdfs:comment "The requirement text this rule traces to." .
gl:expression a owl:AnnotationProperty ; rdfs:comment "The rule as declared in code." .
gl:errorMessage a owl:AnnotationProperty .
gl:sourceFile a owl:AnnotationProperty .
gl:useCase a owl:AnnotationProperty .
gl:origin a owl:AnnotationProperty ; rdfs:comment "'specified' if the requirement text states it; 'inferred' if the AI added it (see ad-libs.md). Derived by matching the rule to the requirement lines." .
"""


def domain_ttl(m):
    c, rules, subs = m["classes"], m["rules"], m["subtypes"]
    out = [f"""@prefix :     <{BASE}{m['project']}#> .
@prefix gl:   <{GL_NS}> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix dct:  <http://purl.org/dc/terms/> .

# Generated by ontology_gv.py from database/models.py, ui/admin/admin.yaml and logic/logic_discovery/*.py.
# Do not edit: regenerate. Constraints are in {m['project']}.shapes.ttl (SHACL).

<{BASE}{m['project']}> a owl:Ontology ; dct:title {lit(m['project'])} ;
    owl:imports <{BASE}genai-logic> .

# ---- Classes (tables) ----"""]
    for cls, d in c.items():
        out.append(f":{cls} a owl:Class ; rdfs:label {lit(cls)} ; rdfs:comment {lit('table ' + d['table'])} .")
    if subs:
        out.append("\n# ---- Subtypes (single-table inheritance): defined classes, membership inferred from the discriminator ----")
    for s in subs:
        out.append(f""":{s['cls']} a owl:Class ; rdfs:label {lit(s['cls'])} ; rdfs:subClassOf :{s['base']} ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( :{s['base']} [ a owl:Restriction ; owl:onProperty {P(s['base'], s['col'])} ; owl:hasValue {lit(s['value'])} ] ) ] .""")
    for members in m["disjoint"]:
        out.append("[] a owl:AllDisjointClasses ; owl:members ( " + " ".join(":" + x for x in members) + " ) .")
    out.append("\n# ---- Properties ----")
    sub_of_col = {}
    for s in subs:
        for col in s["columns"]:
            sub_of_col.setdefault((s["base"], col), s["cls"])
    derived = {}
    for r in rules:
        if r["derive"]:
            derived[r["derive"]] = r["id"]
    tables = {d["table"]: cls for cls, d in c.items()}
    for cls, d in c.items():
        for col, cd in d["cols"].items():
            if cd["pk"]:
                continue
            dom = sub_of_col.get((cls, col), cls)
            extra = f" ; gl:derivedBy :{derived[(cls, col)]}" if (cls, col) in derived else ""
            if cd["fk_table"]:
                tgt = tables.get(cd["fk_table"], cd["fk_table"])
                rel = next((a for a, (k, lst) in d["rels"].items() if k == tgt and not lst), col)
                out.append(f"{P(cls, rel)} a owl:ObjectProperty , owl:FunctionalProperty ; rdfs:domain :{dom} ; rdfs:range :{tgt} ; "
                           f"rdfs:comment {lit('column ' + col)} .")
            else:
                out.append(f"{P(cls, col)} a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:domain :{dom} ; "
                           f"rdfs:range xsd:{XSD.get(cd['type'], 'string')}{extra} .")
        for rel, (tgt, lst) in d["rels"].items():
            if lst:
                out.append(f"{P(cls, rel)} a owl:ObjectProperty ; rdfs:domain :{cls} ; rdfs:range :{tgt} .")
    out.append("\n# ---- Rules, as linked governance artifacts ----")
    fk_rel = {}
    for cls, d in c.items():
        for col, cd in d["cols"].items():
            if cd["fk_table"]:
                tgt = tables.get(cd["fk_table"], cd["fk_table"])
                fk_rel[(cls, col)] = next((a for a, (k, lst) in d["rels"].items() if k == tgt and not lst), col)
    for r in rules:
        parts = [f"rdfs:label {lit(rule_label(r))}",
                 f"gl:useCase {lit(r['use_case'])}", f"gl:sourceFile {lit(r['file'])}", f"gl:origin {lit(r['origin'])}"]
        if r["req"]:
            parts.append(f"gl:requirement {lit(r['req'])}")
        parts.append(f"gl:expression {lit(r['expr'][:400])}")
        if r["error_msg"]:
            parts.append(f"gl:errorMessage {lit(r['error_msg'])}")
        if r["derive"]:
            parts.append(f"gl:derives {P(*r['derive'])}")
        if r["validate"]:
            parts.append(f"gl:validates :{r['validate']}")
            parts.append(f"gl:shape :shape_{r['id']}")
        if r["applies"]:
            parts.append("gl:appliesToType " + " , ".join(":" + a for a in r["applies"]))
        deps = [(P(k, fk_rel.get((k, col), col)) if col else f":{k}") for (k, col) in r["deps"]]
        if deps:
            parts.append("gl:dependsOn " + " , ".join(deps))
        out.append(f":{r['id']} a gl:{GL_CLASS[r['kind']]} ;\n    " + " ;\n    ".join(parts) + " .")
    return "\n".join(out) + "\n"


def shapes_ttl(m):
    c = m["classes"]
    out = [f"""@prefix :     <{BASE}{m['project']}#> .
@prefix gl:   <{GL_NS}> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# Generated by ontology_gv.py. SHACL shapes for the constraints the engine enforces.
# 'translated' shapes state the condition in SHACL; 'descriptive' shapes carry the message only (the condition is code).
# The engine rejects a violating write; these shapes let any SHACL tool check data after the fact.
"""]
    tables = {d["table"]: cls for cls, d in c.items()}
    fk_rel = {}
    for cls, d in c.items():
        for col, cd in d["cols"].items():
            if cd["fk_table"]:
                tgt = tables.get(cd["fk_table"], cd["fk_table"])
                fk_rel[(cls, col)] = next((a for a, (k, lst) in d["rels"].items() if k == tgt and not lst), col)
    for cls, d in c.items():
        req = [(col, cd) for col, cd in d["cols"].items() if not cd["pk"] and not cd["nullable"]]
        if req:
            props = " ; ".join(f"sh:property [ sh:path {P(cls, fk_rel.get((cls, col), col))} ; sh:minCount 1 ]" for col, _ in req)
            out.append(f":shape_required_{cls} a sh:NodeShape ; sh:targetClass :{cls} ; {props} ; "
                       f"sh:message {lit(cls + ': required columns are present')} .")
    for r in m["rules"]:
        if not r["validate"]:
            continue
        v, p = r["validate"], r["pattern"]
        head = f":shape_{r['id']} a sh:NodeShape ; sh:targetClass :{v} ; sh:message {lit(rule_label(r))} ; gl:origin {lit(r['origin'])} ;"
        if p and p[0] == "in":
            body = f" sh:property [ sh:path {P(v, p[1])} ; sh:in ( {' '.join(pv(x) for x in p[2])} ) ] ; rdfs:comment \"translated\" ."
        elif p and p[0] == "lte":
            body = f" sh:property [ sh:path {P(v, p[1])} ; sh:lessThanOrEquals {P(v, p[2])} ] ; rdfs:comment \"translated\" ."
        elif p and p[0] == "null_unless":
            body = (f" sh:or ( [ sh:property [ sh:path {P(v, p[1])} ; sh:hasValue {pv(p[2])} ] ] "
                    f"[ sh:property [ sh:path {P(v, fk_rel.get((v, p[3]), p[3]))} ; sh:maxCount 0 ] ] ) ; rdfs:comment \"translated\" .")
        elif p and p[0] == "value_unless":
            body = (f" sh:or ( [ sh:property [ sh:path {P(v, p[1])} ; sh:hasValue {pv(p[2])} ] ] "
                    f"[ sh:property [ sh:path {P(v, p[3])} ; sh:hasValue {pv(p[4])} ] ] ) ; rdfs:comment \"translated\" .")
        else:
            body = " rdfs:comment \"descriptive\" ."
        out.append(head + body)
    return "\n".join(out) + "\n"


# ── lineage ────────────────────────────────────────────────────────────────────

def lineage(m):
    edges = []
    for r in m["rules"]:
        if r["derive"]:
            tgt = f"{r['derive'][0]}.{r['derive'][1]}"
            for (k, col) in r["deps"]:
                edges.append(dict(source=f"{k}.{col}" if col else f"{k} (rows)", target=tgt, rule=r["id"],
                                  kind=r["kind"], use_case=r["use_case"]))
    return edges


def closure(edges, node):
    down, todo = [], [node]
    while todo:
        n = todo.pop()
        for e in edges:
            if e["source"] == n and e["target"] not in down:
                down.append(e["target"])
                todo.append(e["target"])
    return down


# ── validation (optional) ──────────────────────────────────────────────────────

def validate(project: Path, m, files):
    try:
        import rdflib
    except ImportError:
        return dict(status="skipped", note="rdflib is not installed: files were written but not parsed or validated")
    res = dict(status="parsed", triples={})
    graphs = {}
    for name, path in files.items():
        g = rdflib.Graph()
        g.parse(path, format="turtle")
        graphs[name] = g
        res["triples"][name] = len(g)
    try:
        import pyshacl
    except ImportError:
        res["note"] = "pyshacl is not installed: shapes were parsed but data was not validated"
        return res
    db = project / "database" / "db.sqlite"
    if not db.exists():
        res["note"] = "database/db.sqlite not found: shapes parsed, data not validated"
        return res
    ns = rdflib.Namespace(f"{BASE}{m['project']}#")
    data = rdflib.Graph()
    con = sqlite3.connect(db)
    tables = {d["table"]: cls for cls, d in m["classes"].items()}
    rows = 0
    for cls, d in m["classes"].items():
        pk = next((c for c, cd in d["cols"].items() if cd["pk"]), "id")
        for row in con.execute(f'select * from "{d["table"]}"'):
            rec = dict(zip([x[0] for x in con.execute(f'select * from "{d["table"]}" limit 0').description], row))
            me = ns[f"{cls}/{rec[pk]}"]
            data.add((me, rdflib.RDF.type, ns[cls]))
            rows += 1
            for col, cd in d["cols"].items():
                if cd["pk"] or rec.get(col) is None:
                    continue
                if cd["fk_table"]:
                    tgt = tables.get(cd["fk_table"], cd["fk_table"])
                    rel = next((a for a, (k, lst) in d["rels"].items() if k == tgt and not lst), col)
                    data.add((me, ns[f"{cls}.{rel}"], ns[f"{tgt}/{rec[col]}"]))
                else:
                    data.add((me, ns[f"{cls}.{col}"], rdflib.Literal(rec[col])))
    ok, _, text = pyshacl.validate(data, shacl_graph=graphs["shapes"], inference="none")
    res.update(status="validated", conforms=bool(ok), rows=rows, report=("" if ok else text[:3000]))
    return res


# ── HTML ───────────────────────────────────────────────────────────────────────

def words(name):
    return re.sub(r"[_\s]+", " ", name).strip().lower()


def spaced(name):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)


VALUE_KIND = {"string": "text", "integer": "whole number", "double": "number", "decimal": "amount",
              "dateTime": "date and time", "date": "date", "boolean": "yes / no"}
KIND_BADGE = {"sum": ("Total", "k-calc"), "count": ("Count", "k-calc"), "formula": ("Calculation", "k-calc"),
              "copy": ("Copied value", "k-copy"), "constraint": ("Check", "k-chk"), "commit_constraint": ("Check", "k-chk")}


def bizify(text):
    """Code names to business words: SysConfig.x_y -> 'the system setting x y'; a.b_c -> 'a b c'; x_y -> 'x y'."""
    text = re.sub(r"SysConfig\.(\w+)", lambda x: "the system setting " + x.group(1), text or "")
    text = re.sub(r"\b([a-z]\w*)\.([a-z]\w*)\b", r"\1 \2", text)
    return re.sub(r"(?<=[A-Za-z])_(?=[A-Za-z])", " ", text)


def up(text):
    return text[:1].upper() + text[1:]


def rule_note(r):
    """What the rule does, short enough to follow the target it computes."""
    doc = (r.get("doc") or "").strip().splitlines()[0] if r.get("doc") else ""
    doc = re.sub(r"^(Derive \w+|\w+ constraint|Constraint):\s*", "", doc).rstrip(".")
    if r["kind"] == "sum":
        sc, scol = r["deps"][0]
        return f"the total of its {spaced(sc)} {words(scol)}"
    if r["kind"] == "count":
        return f"the number of its {spaced(r['deps'][0][0])} records"
    if r["kind"] == "copy":
        pc, pcol = r["deps"][0]
        return f"copied from {spaced(pc)} {words(pcol)}"
    if r["kind"] == "formula":
        return bizify(doc) if doc else "calculated by a formula"
    return bizify(doc) or bizify(rule_label(r))


def rule_title(r):
    """A rule in plain English, for the rules table."""
    if r["derive"]:
        c, col = r["derive"]
        return f"{spaced(c)} {words(col)}: {rule_note(r)}"
    if r.get("doc"):
        return up(rule_note(r))
    return up(bizify(clean_msg(rule_label(r))))


def clean_msg(msg):
    return bizify(re.sub(r"\{row\.(\w+)\}", lambda x: "[" + words(x.group(1)) + "]", msg or ""))


def page(m, edges, val):
    e = html.escape
    cls, subs, rules = m["classes"], m["subtypes"], m["rules"]
    tables = {d["table"]: k for k, d in cls.items()}
    derived = {r["derive"]: r for r in rules if r["derive"]}
    sub_of_col = {}
    for sb in subs:
        for col in sb["columns"]:
            sub_of_col.setdefault((sb["base"], col), sb["cls"])

    def fk_target(cname, col):
        return tables.get(cls[cname]["cols"][col]["fk_table"])

    def field_rows(cname, only_sub=None):
        rows = []
        for col, cd in cls[cname]["cols"].items():
            if cd["pk"] or cd["fk_table"] or sub_of_col.get((cname, col)) != only_sub:
                continue
            kind = ("one of: " + ", ".join(str(x) for x in m["enums"][(cname, col)])) if (cname, col) in m["enums"] \
                else VALUE_KIND.get(XSD.get(cd["type"], "string"), "text")
            notes = []
            if (cname, col) in derived:
                notes.append(f"<span class='badge b-derived'>computed</span> {e(rule_note(derived[(cname, col)]))}")
            elif not cd["nullable"]:
                notes.append("required")
            rows.append((words(col).capitalize(), kind, " ".join(notes)))
        return rows

    def field_table(rows):
        if not rows:
            return ""
        t = "<table><tr><th>Field</th><th>Kind of value</th><th>Notes</th></tr>"
        for n, k, note in rows:
            t += f"<tr><td>{e(n)}</td><td>{e(k)}</td><td>{note}</td></tr>"
        return t + "</table>"

    title = f"{spaced(camel(m['project']))}: what the system knows"
    P = [f"<h1>{e(title)}</h1><p class='lead'>The things this system keeps track of, the kinds of each, and the business "
         "rules that keep the data true. The rules are enforced automatically on every change, whether it comes from "
         "a screen, an API or a message. This page is generated from the system itself.</p>",
         "<h2>1. The things this system knows about</h2>"]
    for cname, d in cls.items():
        P.append(f"<section class='card'><h3>{e('System settings (global rates and limits)' if cname == 'SysConfig' else spaced(cname))}</h3>")
        for col, cd in d["cols"].items():
            if cd["fk_table"] and sub_of_col.get((cname, col)) is None:
                t = fk_target(cname, col)
                P.append(f"<p class='rel'>Each {e(spaced(cname))} {'belongs to one' if not cd['nullable'] else 'may belong to one'} "
                         f"<b>{e(spaced(t))}</b>.</p>")
        for rel, (t, lst) in d["rels"].items():
            if lst:
                P.append(f"<p class='rel'>Each {e(spaced(cname))} has many <b>{e(spaced(t))}</b> records.</p>")
        P.append(field_table(field_rows(cname)) + "</section>")

    if subs:
        P.append("<h2>2. Kinds of " + e(spaced(subs[0]["base"])) + "</h2>")
        axes = OrderedDict()
        for sb in subs:
            axes.setdefault((sb["base"], sb["col"]), []).append(sb)
        P.append("<p>They are classified in independent ways. Each record is exactly one kind on each way that is exclusive, "
                 "and may also be a kind from the others.</p><div class='axes'>")
        for (base, col), items in axes.items():
            exclusive = len(items) > 1
            P.append(f"<div class='axis'><h3>By {e(words(col))}</h3><p class='note'>"
                     f"{'Exactly one of these:' if exclusive else 'Independent of the other classifications:'}</p>")
            for sb in items:
                P.append(f"<section class='card'><h4>{e(spaced(sb['cls']))} <span class='badge'>{e(words(col))} = {e(str(sb['value']))}</span></h4>")
                for c2, cd in cls[base]["cols"].items():
                    if cd["fk_table"] and sub_of_col.get((base, c2)) == sb["cls"]:
                        P.append(f"<p class='rel'>May have one <b>{e(spaced(fk_target(base, c2)))}</b>. No other kind of {e(spaced(base).lower())} can.</p>")
                rows = field_rows(base, only_sub=sb["cls"])
                P.append(field_table(rows) or "<p class='note'>No additional fields.</p>")
                P.append("</section>")
            P.append("</div>")
        P.append("</div>")

    P.append("<h2>3. Business rules</h2><p>Each rule traces to the requirement that asked for it. "
             "<span class='badge b-inferred'>added by AI</span> marks rules the requirement did not state, so a person "
             "should confirm them (the judgment calls are listed in <code>ad-libs.md</code>).</p>")
    by_uc = OrderedDict()
    for r in rules:
        by_uc.setdefault(r["use_case"], []).append(r)
    for uc, rs in by_uc.items():
        P.append(f"<h3>{e(spaced(camel(uc)))}</h3><table class='rules'><tr><th>Rule</th><th>Type</th><th>Requirement</th></tr>")
        for r in rs:
            k, kc = KIND_BADGE[r["kind"]]
            inf = r["origin"] == "inferred"
            applies = (f"<br><span class='err'>Applies to: {e(', '.join(spaced(a) for a in r['applies']))}</span>") if r["applies"] else ""
            err = (f"<br><span class='err'>If violated: {e(clean_msg(r['error_msg']))}</span>" if r["error_msg"] else "")
            P.append(f"<tr><td><b>{e(rule_title(r))}</b>" + ("<br><span class='badge b-inferred'>added by AI</span>" if inf else "")
                     + f"</td><td><span class='badge {kc}'>{k}</span></td><td>{e(r['req'] or '(not stated in the requirement)')}"
                     f"{applies}{err}</td></tr>")
        P.append("</table>")

    def nice(node):
        return spaced(node.replace(".", " ").replace("_", " ")).replace("  ", " ").capitalize() if "(rows)" not in node \
            else spaced(node.replace(" (rows)", "")) + " records"

    P.append("<h2>4. What feeds what</h2><p>Where each calculated value comes from, and what a change ripples to. "
             "The same information is in <code>lineage.csv</code> and <code>lineage.json</code> for catalog tools.</p>")
    targets = OrderedDict()
    for x in edges:
        targets.setdefault(x["target"], []).append(x["source"])
    P.append("<table><tr><th>This value</th><th>is calculated from</th></tr>")
    for t, srcs in targets.items():
        P.append(f"<tr><td><b>{e(nice(t))}</b></td><td>{e(', '.join(nice(x) for x in srcs))}</td></tr>")
    P.append("</table><table><tr><th>If this changes</th><th>these are recalculated</th></tr>")
    sources = [x for x in OrderedDict.fromkeys(x["source"] for x in edges) if x not in targets]
    for sname in sources:
        P.append(f"<tr><td><b>{e(nice(sname))}</b></td><td>{e(', '.join(nice(x) for x in closure(edges, sname)))}</td></tr>")
    P.append("</table><h2>5. Check of the current data</h2>")
    if val["status"] == "validated":
        if val["conforms"]:
            P.append(f"<p>All {val['rows']} records in the system satisfy every check that can be stated as a standard "
                     "SHACL shape (<code>" + e(m["project"]) + ".shapes.ttl</code>).</p>")
        else:
            msgs = re.findall(r"Message:\s*(.+)", val["report"])
            P.append(f"<p><b>Some records do not satisfy the checks.</b> The system rejects such changes, so this means data "
                     "that entered by another route:</p><ul>" + "".join(f"<li>{e(x)}</li>" for x in dict.fromkeys(msgs)) + "</ul>")
    else:
        P.append(f"<p>{e(val.get('note', 'Not run.'))}</p>")
    P.append("<p class='note'>Technical files in this folder: " + ", ".join(f"<code>{x}</code>" for x in (
        f"{m['project']}.ttl", f"{m['project']}.shapes.ttl", "genai-logic.ttl", "lineage.csv", "lineage.json")) + ".</p>")
    css = """:root{--bg:#fff;--fg:#1d2330;--mut:#5b6577;--card:#f5f7fb;--line:#d9dfea;--calc:#1b6b4a;--copy:#7a5a00;--chk:#a3262f;--inf:#8a4b00}
@media(prefers-color-scheme:dark){:root{--bg:#10141c;--fg:#e6e9f0;--mut:#9aa4b8;--card:#171d29;--line:#2a3345;--calc:#62d3a0;--copy:#e8c25a;--chk:#ff8a92;--inf:#ffb066}}
body{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:980px;margin:0 auto;padding:24px 16px}
h1{margin:.2em 0}h2{margin-top:2em;border-bottom:1px solid var(--line);padding-bottom:.2em}.lead{color:var(--mut)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:4px 16px 12px;margin:12px 0}
.axes{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}.axis h3{margin-bottom:0}.note,.rel{color:var(--mut);margin:.3em 0}
table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0;display:block;overflow-x:auto}th,td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--mut);font-weight:600}
.badge{display:inline-block;font-size:12px;padding:1px 8px;border-radius:99px;border:1px solid var(--line);white-space:nowrap}
.b-derived,.k-calc{color:var(--calc);border-color:var(--calc)}.k-copy{color:var(--copy);border-color:var(--copy)}.k-chk{color:var(--chk);border-color:var(--chk)}.b-inferred{color:var(--inf);border-color:var(--inf)}
.err{color:var(--mut);font-size:13px}code{background:var(--card);padding:0 .25rem;border-radius:4px}"""
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{e(title)}</title><style>{css}</style></head><body>{''.join(P)}</body></html>")


# ── main ───────────────────────────────────────────────────────────────────────

def generate(project_arg: str, do_validate: bool = True, manager_root: Path = None):
    root = manager_root or Path.cwd()
    project = (root / project_arg).resolve()
    if not (project / "database" / "models.py").exists():
        sys.exit(f"{project}: no database/models.py (run from the Manager root: ontology_gv.py <project_name>)")
    m = build(project)
    out = project / "docs" / "ontology"
    out.mkdir(parents=True, exist_ok=True)
    name = project.name
    files = {"vocabulary": out / "genai-logic.ttl", "domain": out / f"{name}.ttl", "shapes": out / f"{name}.shapes.ttl"}
    files["vocabulary"].write_text(vocabulary_ttl(), encoding="utf-8")
    files["domain"].write_text(domain_ttl(m), encoding="utf-8")
    files["shapes"].write_text(shapes_ttl(m), encoding="utf-8")
    edges = lineage(m)
    with open(out / "lineage.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source", "target", "rule", "kind", "use_case"])
        w.writeheader()
        w.writerows(edges)
    nodes = sorted({x["source"] for x in edges} | {x["target"] for x in edges})
    (out / "lineage.json").write_text(json.dumps(dict(nodes=nodes, edges=edges), indent=1), encoding="utf-8")
    val = validate(project, m, files) if do_validate else dict(status="skipped", note="validation not requested")
    (out / f"{name}.html").write_text(page(m, edges, val), encoding="utf-8")
    n_inf = sum(1 for r in m["rules"] if r["origin"] == "inferred")
    n_tr = sum(1 for r in m["rules"] if r["validate"] and r["pattern"])
    n_con = sum(1 for r in m["rules"] if r["validate"])
    print(f"ontology: {len(m['classes'])} classes, {len(m['subtypes'])} subtypes, {len(m['rules'])} rules "
          f"({n_inf} inferred), {n_tr}/{n_con} constraints translated to SHACL, {len(edges)} lineage edges")
    print(f"  validation: {val['status']}" + (f" - {'conforms' if val.get('conforms') else 'DOES NOT CONFORM'} ({val['rows']} rows)"
                                              if val["status"] == "validated" else f" - {val.get('note', '')}"))
    print(f"  written to {out.relative_to(root) if out.is_relative_to(root) else out}")
    return val


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    generate(args[0], do_validate="--no-validate" not in sys.argv)
