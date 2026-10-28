"""Render an ontology .ttl (domain model + gl:Rule governance) as a business-readable HTML page.
Usage: python render_ontology.py demo_emp_types.ttl [out.html]"""
import re, sys, html
import rdflib
from rdflib import RDF, RDFS, OWL, Namespace
from rdflib.collection import Collection

GL = Namespace("https://apilogicserver.github.io/ontology/genai-logic#")
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"\.ttl$", ".html", src)
g = rdflib.Graph(); g.parse(src, format="turtle")
e = html.escape

def words(uri):
    s = str(uri).split("#")[-1]
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s).replace("_", " ").lower()
def label(n): return str(g.value(n, RDFS.label) or words(n).title())
def comment(n): return str(g.value(n, RDFS.comment) or "")
def members(lst): return list(Collection(g, lst))
def domains(p):
    d = g.value(p, RDFS.domain)
    if d is None: return []
    if isinstance(d, rdflib.BNode) and g.value(d, OWL.unionOf): return members(g.value(d, OWL.unionOf))
    return [d]
def enum_of(p):
    r = g.value(p, RDFS.range)
    if isinstance(r, rdflib.BNode) and g.value(r, OWL.oneOf): return [str(x) for x in members(g.value(r, OWL.oneOf))]
    return []
def rng(p):
    r = g.value(p, RDFS.range)
    en = enum_of(p)
    if en: return "one of: " + ", ".join(en)
    return {"decimal": "amount", "double": "number", "integer": "whole number", "string": "text"}.get(str(r).split("#")[-1], "")

rules = sorted([r for r in g.subjects(RDF.type, None) if any(t in (GL.Sum, GL.Count, GL.Formula, GL.Copy, GL.Constraint) for t in g.objects(r, RDF.type))],
               key=lambda r: (str(g.value(r, GL.sourceFile)), str(r)))
rule_label = {r: label(r) for r in rules}
KIND = {GL.Sum: ("Total", "k-calc"), GL.Count: ("Count", "k-calc"), GL.Formula: ("Calculation", "k-calc"),
        GL.Copy: ("Copied value", "k-copy"), GL.Constraint: ("Check", "k-check")}
def kind(r):
    for t in g.objects(r, RDF.type):
        if t in KIND: return KIND[t]

subtypes = {c for c in g.subjects(RDFS.subClassOf, None) if (c, RDF.type, OWL.Class) in g and any(True for _ in g.objects(c, OWL.equivalentClass))}
base = [c for c in g.subjects(RDF.type, OWL.Class) if isinstance(c, rdflib.URIRef) and c not in subtypes and not str(c).startswith(str(GL))]

def discr(c):  # (property, value) defining a subtype
    for eq in g.objects(c, OWL.equivalentClass):
        for item in members(g.value(eq, OWL.intersectionOf)):
            if isinstance(item, rdflib.BNode) and g.value(item, OWL.hasValue) is not None:
                return g.value(item, OWL.onProperty), str(g.value(item, OWL.hasValue))

def fields(c):
    rows = []
    for p in sorted(g.subjects(RDF.type, OWL.DatatypeProperty), key=str):
        if c in domains(p):
            d = g.value(p, GL.derivedBy)
            rows.append((words(p).capitalize(), rng(p), comment(p), rule_label.get(d) if d else None))
    return rows

def rel_sentences(c):
    out = []
    for p in sorted(g.subjects(RDF.type, OWL.ObjectProperty), key=str):
        if c in domains(p) and g.value(p, RDFS.range) is not None and not g.value(p, GL.derives):
            one = (p, RDF.type, OWL.FunctionalProperty) in g
            out.append(f"{'has at most one' if one else 'has many'} <b>{e(label(g.value(p, RDFS.range)))}</b> via <i>{e(words(p))}</i>"
                       + (f" &mdash; {e(comment(p))}" if comment(p) and one else ""))
    return out

def field_table(c):
    rows = fields(c)
    if not rows: return ""
    t = "<table><tr><th>Field</th><th>Kind of value</th><th>Notes</th></tr>"
    for n, r, cm, d in rows:
        note = (f'<span class="badge b-derived">computed</span> by rule &ldquo;{e(d)}&rdquo; ' if d else "") + e(cm)
        t += f"<tr><td>{e(n)}</td><td>{e(r)}</td><td>{note}</td></tr>"
    return t + "</table>"

title = str(g.value(next(iter(g.subjects(RDF.type, OWL.Ontology))), rdflib.URIRef("http://purl.org/dc/terms/title")) or "Ontology")
P = []
P.append(f"<h1>{e(title)}</h1><p class='lead'>{e(str(g.value(next(iter(g.subjects(RDF.type, OWL.Ontology))), RDFS.comment) or ''))}</p>")
P.append("<h2>1. The things this system knows about</h2>")
for c in sorted(base, key=label):
    P.append(f"<section class='card'><h3>{e(label(c))}</h3><p>{e(comment(c))}</p>")
    for s in rel_sentences(c): P.append(f"<p class='rel'>Each {e(label(c))} {s}</p>")
    P.append(field_table(c) + "</section>")

P.append("<h2>2. Kinds of Employee</h2><p>Employees are classified two independent ways. Every employee is one kind on the first axis, and may <i>also</i> be military.</p><div class='axes'>")
axes = {}
for c in subtypes:
    pv = discr(c)
    if pv: axes.setdefault(pv[0], []).append((pv[1], c))
for prop, items in axes.items():
    exclusive = len(items) > 1
    P.append(f"<div class='axis'><h3>By {e(words(prop))}</h3><p class='note'>{'Exactly one of these:' if exclusive else 'Independent of the other classification:'}</p>")
    for val, c in sorted(items, key=lambda x: str(x[0])):
        P.append(f"<section class='card'><h4>{e(label(c))} <span class='badge'>{e(words(prop))} = {e(val)}</span></h4>")
        for p in g.subjects(RDF.type, OWL.ObjectProperty):
            if c in domains(p) and g.value(p, RDFS.range) and not g.value(p, GL.derives) and (p, RDF.type, OWL.FunctionalProperty) in g:
                P.append(f"<p class='rel'>May have a <b>{e(label(g.value(p, RDFS.range)))}</b>. No other kind of employee can.</p>")
        for p in g.subjects(RDF.type, OWL.ObjectProperty):
            if g.value(p, RDFS.range) == c and (p, RDF.type, OWL.FunctionalProperty) in g:
                P.append(f"<p class='rel'><b>{e(label(g.value(p, RDFS.domain)))}</b> records can belong only to this kind of employee.</p>")
        P.append((field_table(c) or "<p class='note'>No additional fields. Salary is entered directly.</p>" if val == "salaried" else field_table(c)) + "</section>")
    P.append("</div>")
P.append("</div>")

P.append("<h2>3. Business rules</h2><p>Each rule is enforced automatically on every change, and traces to the requirement that asked for it. "
         "<span class='badge b-inferred'>added by AI</span> marks rules nobody asked for in the requirements, so a person should confirm them.</p>")
byfile = {}
for r in rules: byfile.setdefault(str(g.value(r, GL.sourceFile)), []).append(r)
for f, rs in byfile.items():
    use = f.rsplit("/", 1)[-1].removesuffix(".py").replace("_", " ").title()
    P.append(f"<h3>{e(use)}</h3><table class='rules'><tr><th>Rule</th><th>Type</th><th>Requirement</th></tr>")
    for r in rs:
        k, cls = kind(r)
        inf = str(g.value(r, GL.origin)) == "inferred"
        req = str(g.value(r, GL.requirement))
        err = g.value(r, GL.errorMessage)
        P.append(f"<tr><td><b>{e(label(r))}</b>" + ("<br><span class='badge b-inferred'>added by AI</span>" if inf else "") +
                 f"</td><td><span class='badge {cls}'>{k}</span></td><td>{e(req)}" +
                 (f"<br><span class='err'>If violated: {e(re.sub(r'[{]row[.](\w+)[}]', r'[\1]', str(err)))}</span>" if err else "") + "</td></tr>")
    P.append("</table>")

css = """:root{--bg:#fff;--fg:#1d2330;--mut:#5b6577;--card:#f5f7fb;--line:#d9dfea;--acc:#2455c3;--calc:#1b6b4a;--copy:#7a5a00;--chk:#a3262f;--inf:#8a4b00}
@media(prefers-color-scheme:dark){:root{--bg:#10141c;--fg:#e6e9f0;--mut:#9aa4b8;--card:#171d29;--line:#2a3345;--acc:#7da2ff;--calc:#62d3a0;--copy:#e8c25a;--chk:#ff8a92;--inf:#ffb066}}
body{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:980px;margin:0 auto;padding:24px 16px}
h1{margin:.2em 0}h2{margin-top:2em;border-bottom:1px solid var(--line);padding-bottom:.2em}.lead{color:var(--mut)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:4px 16px 12px;margin:12px 0}
.axes{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}.axis h3{margin-bottom:0}.note,.rel{color:var(--mut);margin:.3em 0}
table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0;display:block;overflow-x:auto}th,td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--mut);font-weight:600}
.badge{display:inline-block;font-size:12px;padding:1px 8px;border-radius:99px;border:1px solid var(--line);white-space:nowrap}
.b-derived,.k-calc{color:var(--calc);border-color:var(--calc)}.k-copy{color:var(--copy);border-color:var(--copy)}.k-check{color:var(--chk);border-color:var(--chk)}.b-inferred{color:var(--inf);border-color:var(--inf)}
.err{color:var(--mut);font-size:13px}"""
open(out, "w").write(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{e(title)}</title><style>{css}</style></head><body>{''.join(P)}</body></html>")
print("wrote", out)
