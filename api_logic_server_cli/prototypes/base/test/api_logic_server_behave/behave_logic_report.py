from pathlib import Path
from collections import OrderedDict
from urllib.parse import quote
import datetime
import html
import os
import ast
import re
import shutil
import subprocess
import sys
import click

"""
Behave Logic Report - a governance exhibit, generated as one markdown file.

Sections, in the order an auditor reads them (each is an H2, so each shows in a TOC):

    1. Requirements Traceability To Rules  forward (requirement -> rules/handlers/grants -> tests) and
                                        backward (implementation, tests -> requirement); coverage
                                        summary, matrix, rule coverage by tests, per-requirement detail,
                                        logic diagrams (hide/show) when generated
    2. Data Model                       db diagram (yours, or generated) + derived columns
    3. Security (RBAC)                  roles x CRUD, and row-level grants
    4. Messages and APIs                topics in/out, API endpoints, message shapes
    5. Tests and Results                Behave scenarios, pass/fail, and the logic each one exercised

Sections 1-4 are STATIC: they are derived from the project's files (AST / text), so they
work with no tests defined and no server running.  Section 6 is the original report -
test/behave/behave.log combined with the per-scenario logic logs.

Db diagram convention (you own it if you drew it):
    docs/db_diagram.png|svg|jpg      -> embedded as-is
    otherwise                        -> generated from docs/db.dbml (graphviz 'dot'),
                                        written to reports/db_diagram.generated.svg
                                        (never overwrites yours)

Tips
* use 2 spaces (at end) for newline
* for tab: & emsp;

Changelog:
  2.0 - Rewrite of 1.1.
        * Sections that need no tests and no running server: requirements traceability (forward and
          backward, coverage summary, matrix, rule coverage by tests), data model (your
          docs/db_diagram.* or a generated graphviz diagram, plus derived columns), security (RBAC),
          messages and APIs.
        * Test results: pass/fail per scenario, read from behave.log; a failure is shown prominently
          (banner, red X, the assertion or traceback, skipped steps marked).
        * Logic log per scenario: every transaction, Rules Used as the union across them, in one
          hide/show block; scenarios that fired no rules get no empty box; the scaffold's
          about.feature is skipped.
        * Project summary (readme Summary/Overview, else the creation prompt), table of contents,
          hide/show how-tos for logic diagrams and for creating tests.
        * Runs from any folder (it changes to its own folder, as behave_run.py does).
  1.1 - behave.log combined with the per-scenario logic logs.

"""

__version__ = "2.0"

tab = "&emsp;"
behave_debug_info = " # "
wiki_data = []
debug_scenario = "XXGood Order Custom Service"

scenario_doc_strings = {}
""" dict of scenario_name, array of strings """

PLACEHOLDER_FEATURES = {"About Sample"}
""" the scaffold's about.feature - not a real test """

SKIP_FILES = {"auto_discovery.py", "__init__.py", "use_case.py"}
API_STUB_FILES = {"auto_discovery.py", "system.py", "new_service.py", "newer_service.py",
                  "mcp_discovery.py", "__init__.py"}
""" api_discovery scaffold files - not project APIs """

C_HEADER = "#3f6792"
C_ROW = "#f2f2f2"
C_DERIVED = "#dbe6f3"
C_EDGE = "#9b9ca4"
C_CANVAS = "#fbfbfb"


# ======================================================================================
#  Test evidence (original report logic)
# ======================================================================================

def remove_trailer(line: str) -> str:
    """ remove everything after the ## """
    end_here = line.find("\t\t##")
    result = line[0:end_here]
    return result


def clean_rule_line(line: str) -> str:
    """ tidy an engine rule line: drop the where-lambda repr (' - <function ... at 0x1093>'),
        the python class repr, and the doubled 'Where where=' """
    line = re.sub(r'\s*-\s*<function .*? at 0x[0-9a-fA-F]+>', '', line)
    line = re.sub(r"<class 'database\.models\.(\w+)'>", r'\1', line)
    return line.replace("Where where=", "Where ")


def line_spacer():
    wiki_data.append("\n")
    wiki_data.append("&nbsp;")
    wiki_data.append("&nbsp;")
    wiki_data.append("\n")


def get_truncated_scenario_name(scenario_name: str) -> str:
    """ address max file length (chop at 26), illegal characters """
    scenario_trunc = scenario_name
    if scenario_trunc is not None and len(scenario_trunc) >= 26:
        scenario_trunc = scenario_name[0:25]
    scenario_trunc = f'{str(scenario_trunc).replace(" ", "_")}'
    return scenario_trunc


def log_sections(logic_lines: list) -> list:
    """ one section per transaction in a scenario's logic log: its rule lines (as printed by the
        engine under 'These Rules Fired') and where its logic log starts/ends. Transactions in
        which no rule fired are dropped. """
    sections = []
    i = 0
    while i < len(logic_lines):
        if "These Rules Fired" in logic_lines[i]:
            start_pos = i + 1
            end_pos = start_pos
            while end_pos < len(logic_lines):
                if 'Logic Phase:' in logic_lines[end_pos] and 'COMPLETE' in logic_lines[end_pos]:
                    break
                end_pos += 1
            rule_lines = [remove_trailer(l) for l in logic_lines[start_pos:end_pos]]
            rule_lines = [l for l in rule_lines if l.strip() and not l.startswith('Logic Phase:')]
            log_start = i - 1
            while log_start > 0:
                if 'Logic Phase:' in logic_lines[log_start] and 'ROW LOGIC' in logic_lines[log_start]:
                    if logic_lines[log_start - 1].strip():
                        log_start -= 1   # the scenario header line
                    break
                log_start -= 1
            if rule_lines:
                sections.append({"rules": rule_lines, "log": (log_start, i)})
            i = end_pos
        else:
            i += 1
    return sections


def rules_used(sections: list) -> OrderedDict:
    """ union of the rules fired across a scenario's transactions: owner -> [rule text], first-seen order """
    used = OrderedDict()
    for sec in sections:
        owner = None
        for line in sec["rules"]:
            if re.match(r'^\s+\d+\.', line):
                text = re.sub(r'^\s+\d+\.\s*', '', clean_rule_line(line)).rstrip()
                if text not in used.setdefault(owner, []):
                    used[owner].append(text)
            else:
                owner = line.strip()
    return used


def show_logic(scenario: str, logic_logs_dir: str):
    """ insert {logic_logs_dir}/scenario.log into wiki_data as a disclosure area:
        every transaction in the scenario (each 'These Rules Fired' section), with Rules Used
        as the union across them. A scenario that fired no rules gets no disclosure area. """
    scenario_trunc = get_truncated_scenario_name(scenario)
    logic_file_name_path = Path(f'{logic_logs_dir}/{scenario_trunc}.log')
    if not logic_file_name_path.is_file():
        wiki_data.append("_No logic log for this scenario: the test does not open one, so no rules are shown "
                         "for it (see \"How to add more tests\")._")
        return
    with open(logic_file_name_path) as logic:
        logic_lines = logic.readlines()
    sections = log_sections(logic_lines)
    if not sections:
        wiki_data.append("_No rules fired in this scenario's logic log._")
        return   # nothing fired: no empty boxes
    used = rules_used(sections)

    plural = "transaction" if len(sections) == 1 else "transactions"
    wiki_data.append("<details markdown>")
    wiki_data.append(f"<summary>Rules exercised and logic log ({len(sections)} {plural})</summary>")
    line_spacer()
    if scenario_trunc in scenario_doc_strings:
        wiki_data.append(f'**Logic Doc** for scenario: {scenario}')
        wiki_data.append("   ")
        for each_doc_string_line in scenario_doc_strings[scenario_trunc]:
            wiki_data.append(each_doc_string_line[0: -1])
        line_spacer()
    wiki_data.append(f'**Rules Used** in Scenario: {scenario}')
    wiki_data.append("```")
    n = 0
    for owner, texts in used.items():
        wiki_data.append(f"  {owner}  ")
        for text in texts:
            n += 1
            wiki_data.append(f"    {n}. {text}  ")
    wiki_data.append("```")
    wiki_data.append(f'**Logic Log** in Scenario: {scenario} ({len(sections)} {plural})')
    wiki_data.append("```")
    for k, sec in enumerate(sections):
        if k:
            wiki_data.append("")
        start, end = sec["log"]
        for each_logic_log in logic_lines[start:end]:
            wiki_data.append(clean_rule_line(remove_trailer(each_logic_log)))
    wiki_data.append("```")
    wiki_data.append("</details>")


def get_docStrings(steps_dir: str):
    if not Path(steps_dir).is_dir():
        return
    steps_dir_files = os.listdir(steps_dir)
    indent = 4  # skip leading blanks
    for each_steps_dir_file in steps_dir_files:
        each_steps_dir_file_path = Path(steps_dir).joinpath(each_steps_dir_file)
        if each_steps_dir_file_path.is_file() and each_steps_dir_file_path.suffix == ".py":
            with open(each_steps_dir_file_path) as f:
                step_code = f.readlines()
            for index, each_step_code_line in enumerate(step_code):
                if each_step_code_line.startswith('@when'):
                    comment_start = index + 2
                    if comment_start < len(step_code) and '"""' in step_code[comment_start]:
                        doc_string_line = comment_start+1
                        doc_string = []
                        while (True):
                            if '"""' in step_code[doc_string_line]:
                                break
                            doc_string.append(step_code[doc_string_line][indent:])
                            doc_string_line += 1
                        scenario_line = doc_string_line+1
                        if 'scenario_name' not in step_code[scenario_line]:
                            print(f'\n** Warning - scenario_name not found '
                                  f'in file {str(each_steps_dir_file_path)}, '
                                  f'after line {scenario_line} -- skipped')
                        else:
                            scenario_code_line = step_code[scenario_line]
                            scenario_name_start = scenario_code_line.find("'") + 1
                            scenario_name_end = scenario_code_line[scenario_name_start+1:].find("'")
                            scenario_name = scenario_code_line[scenario_name_start:
                                scenario_name_end + scenario_name_start+1]
                            scenario_trunc = get_truncated_scenario_name(scenario_name)
                            scenario_doc_strings[scenario_trunc] = doc_string


def build_test_evidence(behave_log: str, scenario_logs: str) -> list:
    """ behave.log + per-scenario logic logs, as markdown lines: each scenario's steps (with its
        result), a failure shown prominently, then its rules exercised and logic log """
    global wiki_data
    wiki_data = []
    get_docStrings(steps_dir="features/steps")

    with open(behave_log) as f:
        contents = f.read().splitlines()

    results = scenario_results(behave_log) or {}
    skipping = False
    feature_name = None
    open_scenario = None   # scenario whose steps are being listed; its logic block follows when it ends
    failure = None         # None, 'assert' or 'trace': inside a failure message under a failing step

    def close_failure():
        nonlocal failure
        if failure == "trace":
            wiki_data.append("```")
        failure = None

    def close_scenario():
        nonlocal open_scenario
        close_failure()
        if open_scenario:
            wiki_data.append("")
            show_logic(scenario=open_scenario, logic_logs_dir=scenario_logs)
            open_scenario = None

    for line in contents:
        m = re.match(r'^Feature:\s*(.*?)(?:\s+#\s.*)?$', line)
        if m:
            close_scenario()
            feature_name = m.group(1).strip()
            skipping = feature_name in PLACEHOLDER_FEATURES   # the scaffold's about.feature is not a real test
            if not skipping:
                wiki_data += ["", "&nbsp;", "&nbsp;", "", f"### Feature: {feature_name}  "]
            continue
        if skipping:
            continue
        m = re.match(r'^  Scenario(?: Outline)?:\s*(.*?)(?:\s+#\s.*)?$', line)
        if m:
            close_scenario()
            name = m.group(1).strip()
            open_scenario = name
            mark = {"passed": " ✅", "failed": " ❌ FAILED"}.get(results.get((feature_name, name)), "")
            wiki_data += ["", "&nbsp;", "&nbsp;", "", f"#### Scenario: {name}{mark}",
                          f"{tab}  Scenario: {name}  "]
            continue
        m = re.match(r'^    (Given|When|Then|And|But) (.*?)(?:\s+#\s(.*))?$', line)
        if m:
            close_failure()
            skipped = (m.group(3) or "").strip() == "None"   # behave lists steps after a failure with no location
            wiki_data.append(f"{tab}{tab}    {m.group(1)} {m.group(2)}" + ("  _(skipped)_" if skipped else "") + "  ")
            continue
        if open_scenario and re.match(r'^\s{6,}\S', line):   # a failure message under a failing step
            text = line.strip()
            if failure is None:
                if text.startswith("Assertion Failed"):
                    failure = "assert"
                    wiki_data += ["", f"{tab}{tab}**❌ {text.split(':', 1)[0]}:** {text.split(':', 1)[1].strip()}  "]
                else:
                    failure = "trace"
                    wiki_data += ["", f"{tab}{tab}**❌ Error**", "", "```", line[6:]]
            elif failure == "trace":
                wiki_data.append(line[6:])
            else:
                wiki_data.append(f"{tab}{tab}{text}  ")
            continue
        if not line.strip():
            if failure == "trace":
                close_failure()
            continue
        close_scenario()   # the run's trailing lines ('completed at ...') follow the last scenario
        wiki_data.append(line + "  ")

    close_scenario()
    return wiki_data


# ======================================================================================
#  Static analysis helpers
# ======================================================================================

def _read(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _seg(src: str, node) -> str:
    return ast.get_source_segment(src, node) or ""


def _tidy(text: str) -> str:
    """ drop model prefixes, collapse whitespace """
    text = re.sub(r'\b(?:database\.)?models\.', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _body(src: str, node) -> str:
    """ lambda -> its body, minus 'row.' prefixes; anything else -> its source """
    if isinstance(node, ast.Lambda):
        text = _tidy(_seg(src, node.body))
    else:
        text = _tidy(_seg(src, node))
    return re.sub(r'\brow\.', '', text)


def _doc1(fn) -> str:
    """ first paragraph of a function's docstring, on one line """
    doc = ast.get_docstring(fn) if fn is not None else None
    if not doc:
        return ""
    para = doc.strip().split("\n\n")[0]
    return re.sub(r'\s+', ' ', para).strip()


def _cell(text: str) -> str:
    """ markdown table cell """
    return str(text).replace("|", "\\|").replace("\n", " ")


def _code(text: str) -> str:
    return f"`{_cell(text)}`" if text else ""


def _module_doc(path: Path) -> str:
    try:
        return ast.get_docstring(ast.parse(_read(path))) or ""
    except SyntaxError:
        return ""


def _first_line(text: str) -> str:
    for each in text.splitlines():
        if each.strip():
            return each.strip()
    return ""


def logic_files(root: Path) -> list:
    base = root / "logic" / "logic_discovery"
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*.py")
                  if p.name not in SKIP_FILES and "__pycache__" not in p.parts)


# ======================================================================================
#  Rules
# ======================================================================================

EVENT_RULES = {"early_row_event", "row_event", "commit_row_event", "after_flush_row_event"}
POSITIONAL = {"sum": ["derive", "as_sum_of", "where"],
              "count": ["derive", "as_count_of", "where"],
              "formula": ["derive", "as_expression"],
              "copy": ["derive", "from_parent"],
              "constraint": ["validate"],
              "commit_constraint": ["validate"]}


def extract_rules(path: Path, root: Path) -> list:
    """ every Rule.* / Allocate(...) call in a logic file, as plain text (no import of the project) """
    src = _read(path)
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name not in functions:
            functions[node.name] = node

    rules = []
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    for call in sorted(calls, key=lambda n: (n.lineno, n.col_offset)):
        kind = None
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) \
                and call.func.value.id == "Rule":
            kind = call.func.attr
        elif isinstance(call.func, ast.Name) and call.func.id == "Allocate":
            kind = "Allocate"
        if kind is None:
            continue
        args = {}
        for i, each in enumerate(call.args):
            names = POSITIONAL.get(kind, [])
            if i < len(names):
                args[names[i]] = each
        for each in call.keywords:
            if each.arg:
                args[each.arg] = each.value

        def cls_of(node) -> str:
            return _tidy(_seg(src, node)) if node is not None else ""

        def calling_text(node):
            """ (name, docstring) of a calling= function """
            if node is None:
                return "", ""
            name = _tidy(_seg(src, node))
            if isinstance(node, ast.Name):
                return name, _doc1(functions.get(node.id))
            return name, ""

        rule = {"kind": kind, "file": _rel(path, root), "derive": None,
                "how": "declarative", "text": "", "desc": "", "line": call.lineno}
        derive = cls_of(args.get("derive"))
        if kind == "sum":
            where = args.get("where")
            rule["derive"] = derive
            rule["text"] = f"{derive} = sum({cls_of(args.get('as_sum_of'))})" + \
                           (f" where {_body(src, where)}" if where is not None else "")
        elif kind == "count":
            where = args.get("where")
            rule["derive"] = derive
            rule["text"] = f"{derive} = count({cls_of(args.get('as_count_of'))})" + \
                           (f" where {_body(src, where)}" if where is not None else "")
        elif kind == "copy":
            rule["derive"] = derive
            rule["text"] = f"{derive} = copy of {cls_of(args.get('from_parent'))}"
        elif kind == "formula":
            rule["derive"] = derive
            if "calling" in args:
                name, doc = calling_text(args["calling"])
                rule["how"] = "Python function"
                rule["text"] = f"{derive} = {name}()"
                rule["desc"] = doc or "(no docstring)"
            else:
                rule["text"] = f"{derive} = {_body(src, args.get('as_expression'))}"
        elif kind in ("constraint", "commit_constraint"):
            cls = cls_of(args.get("validate"))
            if "calling" in args:
                name, doc = calling_text(args["calling"])
                rule["how"] = "Python function"
                cond = f"{name}()"
                rule["desc"] = doc or "(no docstring)"
            else:
                cond = _body(src, args.get("as_condition"))
                msg = args.get("error_msg")
                if isinstance(msg, ast.Constant):
                    rule["desc"] = f"Error: {msg.value}"
            rule["text"] = f"{cls}: {cond}"
        elif kind in EVENT_RULES:
            cls = cls_of(args.get("on_class"))
            name, doc = calling_text(args.get("calling"))
            rule["how"] = "event (Python)"
            cond = args.get("if_condition")
            rule["text"] = f"{cls}.{kind} → {name}()" + \
                           (f" [if {_body(src, cond)}]" if cond is not None else "")
            rule["desc"] = doc or "(no docstring)"
            calling_node = args.get("calling")
            rule["call_src"] = _seg(src, call)   # the Rule.* call itself (may carry with_args={"topic": ...})
            rule["fn_src"] = _seg(src, functions[calling_node.id]) \
                if isinstance(calling_node, ast.Name) and calling_node.id in functions else ""
        elif kind.endswith("_all_classes"):
            name, doc = calling_text(args.get(kind) or args.get("calling"))
            rule["how"] = "event (Python)"
            rule["text"] = f"all classes.{kind.replace('_all_classes', '')} → {name}()"
            rule["desc"] = doc or "(no docstring)"
        elif kind == "Allocate":
            rule["text"] = (f"Allocate {cls_of(args.get('provider'))} to "
                            f"{cls_of(args.get('creating_allocation'))}"
                            f" (recipients: {cls_of(args.get('recipients'))})")
            allocator = args.get("while_calling_allocator")
            if allocator is not None:
                name, doc = calling_text(allocator)
                rule["text"] += f" using {name}()"
                rule["desc"] = doc
            rule["how"] = "declarative (Allocate)"
        else:
            rule["text"] = _tidy(_seg(src, call))[:140]
        rules.append(rule)
    return rules


def collect_rules(root: Path) -> list:
    """ every rule in every logic file """
    rules = []
    for each in logic_files(root):
        rules.extend(extract_rules(each, root))
    return rules


# ======================================================================================
#  Requirements -> implementation
# ======================================================================================

def _requirement_text(section: str) -> list:
    """ requirement body as clean lines: no front matter, comments or code-fence markers """
    lines = [l for l in section.splitlines() if not l.strip().startswith("```")]
    return _cap(_clean_markdown(lines), 25)[0]


def parse_requirements(root: Path) -> list:
    """ requirement items from docs/requirements/**/requirements.md:
        '## N. Title' sections (with Feature: lines), else one item per use-case folder """
    items = OrderedDict()
    base = root / "docs" / "requirements"
    if not base.is_dir():
        return []
    for each in sorted(base.rglob("requirements.md")):
        text = _read(each)
        rel = _rel(each, root)
        heads = list(re.finditer(r'^##\s+(\d+)\.\s+(.+?)\s*$', text, re.M))
        if heads:
            for i, m in enumerate(heads):
                end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
                section = text[m.end():end]
                key = (int(m.group(1)), m.group(2))
                item = items.setdefault(key, {"num": int(m.group(1)), "title": m.group(2),
                                              "features": set(), "sources": []})
                item["features"] |= {f.strip() for f in re.findall(r'Feature:\s*(.+)', section)}
                if not item.get("text"):
                    item["text"] = _requirement_text(section)
                if rel not in item["sources"]:
                    item["sources"].append(rel)
        else:
            use_case = each.parent.name
            key = (None, use_case)
            item = items.setdefault(key, {"num": None, "title": use_case,
                                          "features": set(), "sources": []})
            item["features"] |= {f.strip() for f in re.findall(r'Feature:\s*(.+)', text)}
            if not item.get("text"):
                item["text"] = _requirement_text(text)
            item["sources"].append(rel)
    return sorted(items.values(), key=lambda i: (i["num"] is None, i["num"] or 0, i["title"]))


def implementation_files(root: Path) -> list:
    """ files that can implement a requirement """
    found = list(logic_files(root))
    for pattern in ("integration/kafka/kafka_*_discovery/*.py", "integration/*.py",
                    "api/api_discovery/*.py", "security/declare_security.py"):
        for each in sorted(root.glob(pattern)):
            if each.name not in SKIP_FILES and each.name not in API_STUB_FILES \
                    and "__pycache__" not in each.parts:
                found.append(each)
    unique = []
    for each in found:
        if each not in unique:
            unique.append(each)
    return unique


def _norm(name: str) -> str:
    """ 'Check Credit' and 'check_credit' compare equal """
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')


def parse_features(root: Path) -> dict:
    """ Feature name -> scenario count, from features/*.feature (placeholders excluded) """
    result = {}
    base = root / "test" / "api_logic_server_behave" / "features"
    if not base.is_dir():
        return result
    for each in sorted(base.glob("*.feature")):
        text = _read(each)
        m = re.search(r'^\s*Feature:\s*(.+)$', text, re.M)
        if not m:
            continue
        name = m.group(1).strip()
        if name in PLACEHOLDER_FEATURES:
            continue
        result[name] = len(re.findall(r'^\s*Scenario', text, re.M))
    return result


def _rule_row(r: dict, root: Path, report_dir: Path) -> str:
    where = f"[{Path(r['file']).name}]({_link(root / r['file'], report_dir)})"
    return f"| {_code(r['text'])} | {r['kind']} | {r['how']} | {_cell(r['desc'])} | {where} |"


def _artifact_rows(rel: str, root: Path, report_dir: Path, msg_rows: list) -> list:
    """ table rows for a matched file that has no Rule.* calls: handlers, endpoints, grants, modules """
    where = f"[{Path(rel).name}]({_link(root / rel, report_dir)})"
    rows = []
    if rel == "security/declare_security.py":
        for grant in security_summary(root):
            rows.append(f"| {_code(grant)} | grant | declarative |  | {where} |")
        return rows
    for m in (m for m in msg_rows if m["file"] == rel and m["handler"]):
        label = f"{m['channel']} {'in' if m['direction'] == 'in' else 'out'}: {m['name']}"
        rows.append(f"| {_code(label)} | {m['channel'].lower()} | handler (Python) | "
                    f"{_cell(m['desc'])} | {where} |")
    if not rows:
        first = _first_line(_module_doc(root / rel))
        rows.append(f"| {_code(Path(rel).name)} | module |  | {_cell(first)} | {where} |")
    return rows


def _diagram_blocks(stems: list, root: Path, report_dir: Path) -> list:
    """ hide/show blocks for scoped logic diagrams that already exist """
    out = []
    for stem in stems:
        svg = root / "docs" / "requirements" / stem / "logic_diagrams" / f"logic_diagram_{stem}.svg"
        if svg.is_file():
            out += ["", "<details markdown>", f"<summary>Logic diagram: {stem}</summary>", "",
                    f"![logic diagram: {stem}]({_link(svg, report_dir)})", "", "</details>"]
    return out


TABLE_HEAD = ["| Rule / item | Type | Logic | Description | Where |", "|---|---|---|---|---|"]


def diagram_howto(root: Path, missing: bool) -> list:
    """ hide/show block: how to create (or refresh) the per-requirement logic diagrams, with this
        project's real command """
    manager = next((p for p in root.parents
                    if (p / "system" / "ApiLogicServer-Internal-Dev" / "logic_diagram_gv.py").is_file()), None)
    project = root.relative_to(manager).as_posix() if manager else "<project>"
    title = "How to create the missing logic diagrams" if missing else "How to create or refresh the logic diagrams"
    return [
        "<details markdown>",
        f"<summary>{title}</summary>",
        "",
        "Needs Graphviz (`brew install graphviz`). Tell your AI assistant:",
        "",
        "```",
        "create logic diagram for each requirement",
        "```",
        "",
        "or run this from the Manager root" + (f" (`{manager.name}`)" if manager else "") + ":",
        "",
        "```",
        f"python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py {project} --each",
        "```",
        "",
        "Each diagram is saved under `docs/requirements/<name>/logic_diagrams/`. Then regenerate this report "
        "(`python behave_logic_report.py run`, from `test/api_logic_server_behave`).",
        "",
        "</details>",
        "",
        "&nbsp;",
        "",
    ]


def scenario_results(behave_log: str):
    """ {(feature, scenario): 'passed' | 'failed'} read from behave.log, or None if there is no run.
        Behave writes 'Assertion Failed: ...' or a Traceback under a failing step; a scenario with
        neither passed. (The scaffold's placeholder feature is left out.) """
    log = Path(behave_log)
    if not log.is_file() or log.stat().st_size == 0:
        return None
    results, feature, current = OrderedDict(), None, None
    for line in _read(log).splitlines():
        m = re.match(r'^Feature:\s*(.*?)\s*(#.*)?$', line)
        if m:
            feature, current = m.group(1).strip(), None
            continue
        m = re.match(r'^\s+Scenario(?: Outline)?:\s*(.*?)\s*(#.*)?$', line)
        if m and feature not in PLACEHOLDER_FEATURES:
            current = (feature, m.group(1).strip())
            results[current] = "passed"
            continue
        if current and re.match(r'^\s+(Assertion Failed|Traceback \(most recent call last\))', line):
            results[current] = "failed"
    return results or None


def _static_key(rule: dict):
    """ how to recognise a declared rule in the engine's log, or None if it cannot be matched """
    if rule["derive"]:
        return ("derive", rule["derive"])
    if rule["kind"] in ("constraint", "commit_constraint"):
        return ("constraint", rule["text"].split(":")[0].strip())
    m = re.match(r'^(\w+)\.\w+ → (\w+)\(\)', rule["text"])
    if m and rule["how"].startswith("event"):
        return ("event", m.group(1), m.group(2))
    return None


def _engine_keys(used: OrderedDict) -> set:
    """ the same keys, from the rules the engine reported firing in a scenario """
    keys = set()
    for owner, texts in used.items():
        for text in texts:
            m = re.match(r'^Derive (\w+\.\w+) as', text)
            if m:
                keys.add(("derive", m.group(1)))
                continue
            m = re.match(r'^\w*RowEvent (\w+)\.(\w+)\(\)', text)
            if m:
                keys.add(("event", m.group(1), m.group(2)))
                continue
            if text.startswith("Constraint") and owner:
                keys.add(("constraint", owner))
    return keys


def rule_coverage(rules: list, behave_log: str, scenario_logs: str):
    """ which scenarios' logic logs show each declared rule being run.
        returns None if there is no test run, else (coverage, with_log, total, shared_used):
          coverage {rule index: [scenario names] | None if the rule cannot be matched}
          with_log / total: scenarios (placeholder excluded) that have their own logic log / all scenarios
          shared_used: the scaffold's placeholder scenario has a log with rules in it. Tests that never open a
                       log of their own write into whichever log was open last, which is often that one,
                       so it is counted (as '<name> (shared log)'). """
    log = Path(behave_log)
    if not log.is_file() or log.stat().st_size == 0:
        return None
    scenarios, feature = [], None   # (display name, log name, is_placeholder)
    for line in _read(log).splitlines():
        m = re.match(r'^Feature:\s*(.*?)\s*(#.*)?$', line)
        if m:
            feature = m.group(1).strip()
            continue
        m = re.match(r'^\s+Scenario(?: Outline)?:\s*(.*?)\s*(#.*)?$', line)
        if m:
            name = m.group(1).strip()
            placeholder = feature in PLACEHOLDER_FEATURES
            scenarios.append((f"{name} (shared log)" if placeholder else name, name, placeholder))
    fired, with_log, total, shared_used = {}, 0, 0, False
    for display, name, placeholder in scenarios:
        total += 0 if placeholder else 1
        path = Path(scenario_logs) / f"{get_truncated_scenario_name(name)}.log"
        if not path.is_file():
            continue
        keys = _engine_keys(rules_used(log_sections(_read(path).splitlines(True))))
        if placeholder:
            if keys:
                fired[display] = keys
                shared_used = True
        else:
            with_log += 1
            fired[display] = keys
    if not fired:
        return None
    coverage = {}
    for i, rule in enumerate(rules):
        key = _static_key(rule)
        coverage[i] = None if key is None else [n for n, keys in fired.items() if key in keys]
    return coverage, with_log, total, shared_used


def _tests_text(rec: dict, results, defined: bool) -> str:
    """ '9 scenario(s)' plus, when there is a test run, how many passed / failed """
    if not rec["scenarios"]:
        return "⚠ none defined" if defined else "none defined"
    text = f"{rec['scenarios']} scenario(s)"
    if results is not None:
        ran = rec["passed"] + rec["failed"]
        icon = "❌ " if rec["failed"] else ("✅ " if ran >= rec["scenarios"] else "")
        text = icon + text + f": {rec['passed']} passed" + (f", **{rec['failed']} FAILED**" if rec["failed"] else "")
        if ran < rec["scenarios"]:
            text += f", {rec['scenarios'] - ran} not run"
    return text


def _gap_list(labels: list) -> str:
    return ", ".join(labels) if labels else "none"


def sec_requirements(root: Path, report_dir: Path, rules: list, msg_rows: list,
                     behave_log: str = "logs/behave.log", scenario_logs: str = "logs/scenario_logic_logs") -> tuple:
    """ requirements traceability: coverage summary, matrix, rule coverage by tests, detail per requirement.
        returns (lines, req_by_file, features) """
    lines = ["## Requirements Traceability To Rules", ""]
    items = parse_requirements(root)
    files = implementation_files(root)
    features = parse_features(root)
    req_by_file = {}

    declarative = sum(1 for r in rules if r["how"].startswith("declarative"))
    python_fn = sum(1 for r in rules if r["how"] == "Python function")
    events = sum(1 for r in rules if r["how"].startswith("event"))
    n_files = len({r["file"] for r in rules})

    lines.append("Traceability here is **forward** (requirement, to the rules, handlers and grants that "
                 "implement it, to the tests that exercise it) and **backward** (implementation and tests, "
                 "to the requirement they serve). Anything with no requirement is listed as untraced, and "
                 "every requirement with no implementation or no test is listed as a gap. "
                 "Links are made by the `Feature:` names and `§N` tags that requirements, code and tests carry.")
    lines.append("")

    sources = {_rel(f, root): _read(f) for f in files}
    records, traced = [], set()
    missing_diagram = False
    for item in items:
        if item["num"] is not None and not item["features"]:
            continue   # a numbered section with no Feature: (e.g. "How to Test") is a note, not a requirement
        label = f"§{item['num']} {item['title']}" if item["num"] is not None else item["title"]
        matched = []
        for rel, src in sources.items():
            hit = any(f and re.search(r'Feature:\s*' + re.escape(f) + r'\s*$', src, re.M)
                      for f in item["features"])
            if not hit and item["num"] is not None:
                hit = re.search(rf'§\s*{item["num"]}\b', src) is not None
            if not hit and item["num"] is None:
                hit = Path(rel).stem == item["title"]
            if hit:
                matched.append(rel)
                traced.add(rel)
                req_by_file.setdefault(rel, []).append(label)
        wanted = {_norm(f) for f in item["features"]} | {_norm(item["title"])}
        scenarios = sum(n for name, n in features.items() if _norm(name) in wanted)
        records.append({"item": item, "label": label, "matched": matched, "wanted": wanted,
                        "scenarios": scenarios,
                        "n_rules": sum(1 for r in rules if r["file"] in matched)})

    # ---- coverage summary
    all_wanted = set().union(*[r["wanted"] for r in records]) if records else set()
    tests_untraced = [name for name in features if _norm(name) not in all_wanted]
    no_impl = [r["label"] for r in records if not r["matched"]]
    no_tests = [r["label"] for r in records if not r["scenarios"]]
    untraced_files = [rel for rel in sources if rel not in traced
                      and "/system/" not in rel and rel.endswith(".py")]
    loose = [r for r in rules if r["file"] not in traced]
    cov = rule_coverage(rules, behave_log, scenario_logs)
    coverage = cov[0] if cov else None
    results = scenario_results(behave_log)
    for rec in records:
        mine = [status for (feature, _), status in (results or {}).items() if _norm(feature) in rec["wanted"]]
        rec["passed"], rec["failed"] = mine.count("passed"), mine.count("failed")
    lines += ["### Coverage summary", "", "| Measure | Result |", "|---|---|"]
    n = len(records)
    lines.append(f"| Requirements | {n} |")
    lines.append(f"| Implemented (at least one file) | {n - len(no_impl)} of {n}"
                 + (f" - gap: {_gap_list(no_impl)}" if no_impl else "") + " |")
    lines.append(f"| Tested (at least one scenario) | {n - len(no_tests)} of {n}"
                 + (f" - gap: {_gap_list(no_tests)}" if no_tests else "") + " |")
    untraced_all = list(untraced_files) + [f for f in dict.fromkeys(r["file"] for r in loose)
                                           if f not in untraced_files]
    lines.append(f"| Implementation not traced to a requirement | "
                 f"{_cell(_gap_list([f'`{u}`' for u in untraced_all]))} |")
    lines.append(f"| Tests not traced to a requirement | {_cell(_gap_list(tests_untraced))} |")
    if results is None:
        lines.append("| Test results | no test run found |")
    else:
        failing = [r["label"] for r in records if r["failed"]]
        n_failed = list(results.values()).count('failed')
        lines.append(f"| Test results (last run) | {'❌' if n_failed else '✅'} "
                     f"{list(results.values()).count('passed')} passed, {n_failed} failed"
                     + (f" - failing: {_cell(_gap_list(failing))}" if failing else "") + " |")
    if coverage is None:
        lines.append("| Rules seen in a scenario's log | no test run found |")
    else:
        lines.append(f"| Scenarios with a logic log | {cov[1]} of {cov[2]}"
                     + (" (plus the scaffold's shared log, which is included)" if cov[3] else "") + " |")
        matchable = [i for i, v in coverage.items() if v is not None]
        never = [rules[i] for i in matchable if not coverage[i]]
        cannot = len(coverage) - len(matchable)
        never_text = _gap_list([_code(r["text"]) for r in never])
        lines.append(f"| Rules seen in at least one scenario's log | {len(matchable) - len(never)} of {len(matchable)}"
                     + (f" - not seen: {never_text}" if never else "")
                     + (f" ({cannot} rule(s) cannot be matched to the engine's log)" if cannot else "") + " |")
    lines.append("")
    lines.append("_Test results are read from `logs/behave.log`, so they are only as current as that run. "
                 "Not recorded here: which version of a requirement the code was built against, and "
                 "which clause of a requirement a given rule serves._")

    # ---- traceability matrix
    lines += ["", "### Traceability matrix", ""]
    if not records:
        lines.append("No requirements found, so there is nothing to trace yet. Requirements live in "
                     "`docs/requirements/<name>/requirements.md`; tell your AI assistant "
                     "`implement reqs <name>` to turn them into rules, and name the same `Feature:` in the "
                     "logic file and the tests so this report can link them.")
    else:
        lines += ["| Requirement | Implemented by | Rules | Tests |", "|---|---|---|---|"]
    for rec in records:
        impl = "<br>".join(f"[{m}]({_link(root / m, report_dir)})" for m in rec["matched"]) \
            if rec["matched"] else "⚠ none found"
        tests = _tests_text(rec, results, defined=True)
        lines.append(f"| {_cell(rec['label'])} | {impl} | {rec['n_rules']} | {tests} |")

    # ---- rule coverage by tests
    lines += ["", "### Rule coverage by tests", ""]
    if coverage is None:
        lines.append("No test run found, so rule coverage cannot be shown. Run the tests (see "
                     "Tests and Results) and regenerate this report.")
    else:
        lines += ["| Rule | Requirement | Seen in |", "|---|---|---|"]
        for i, rule in enumerate(rules):
            reqs = "; ".join(req_by_file.get(rule["file"], [])) or "(none)"
            hit = coverage[i]
            if hit is None:
                shown = "n/a - cannot be matched to the engine's log"
            elif not hit:
                shown = "⚠ not seen in any scenario's log"
            else:
                shown = f"{len(hit)}: " + "; ".join(hit[:3]) + (f"; +{len(hit) - 3} more" if len(hit) > 3 else "")
            lines.append(f"| {_code(rule['text'])} | {_cell(reqs)} | {_cell(shown)} |")
        lines += ["", "_\"Seen\" means the engine reported running the rule in that scenario's logic log. "
                  "A scenario can only contribute if it has a log (see the coverage summary): a test that does not "
                  "open one writes into whichever log was open last, and its rules are then credited to that "
                  "scenario, or to the shared log. An event's function runs on every commit of its class, and "
                  "its own condition decides whether it acts, so seen does not mean it took effect. A constraint "
                  "appears in the log only when it rejects a transaction, so it is seen only in scenarios that make "
                  "it reject. \"Not seen\" therefore means no log shows it, not that no test ran it._"]

    # ---- inventory line + per-requirement detail
    lines += ["", "### Requirements in detail", "",
              f"**{len(rules)} rules** in {n_files} files: {declarative} declarative (sum, count, copy, "
              f"formula and constraint expressions), {python_fn} backed by a Python function, "
              f"{events} events (Python). _Declarative rules are read directly from their declarations; "
              f"functions and events are Python, so the report shows each one's docstring, not an analysis "
              f"of its code._", "",
              "Each requirement is followed by the rules and handlers in the files that implement it. "
              "Logic diagrams are shown (click to expand) where they exist."]
    full = root / "docs" / "requirements" / "logic_diagrams" / "logic_diagram.svg"
    if full.is_file():
        lines += ["", "<details markdown>", "<summary>Logic diagram: all rules</summary>", "",
                  f"![logic diagram: all rules]({_link(full, report_dir)})", "", "</details>"]

    details = []
    for rec in records:
        item, matched = rec["item"], rec["matched"]
        tests = _tests_text(rec, results, defined=False)
        block = ["", f"#### {rec['label']}", "", f"Tests: {tests}", "", "```"]
        block += item.get("text") or ["(no requirement text found)"]
        block += ["```", ""]
        rows = []
        for rel in matched:
            file_rules = [r for r in rules if r["file"] == rel]
            rows.extend(_rule_row(r, root, report_dir) for r in file_rules)
            if not file_rules:
                rows.extend(_artifact_rows(rel, root, report_dir, msg_rows))
        if rows:
            block += TABLE_HEAD + rows
        else:
            block.append("⚠ no implementing file found")
        stems = [Path(m).stem for m in matched if any(r["file"] == m for r in rules)]
        diagrams = _diagram_blocks(stems, root, report_dir)
        missing_diagram = missing_diagram or len(diagrams) < len([st for st in stems if st])
        block += diagrams
        details.append(block)
    lines += diagram_howto(root, missing_diagram)
    for block in details:
        lines.extend(block)

    if loose:
        lines += ["", "#### Rules not traced to a requirement", ""]
        lines += TABLE_HEAD + [_rule_row(r, root, report_dir) for r in loose]
    return lines, req_by_file, features


# ======================================================================================
#  Data model
# ======================================================================================

def parse_dbml(path: Path) -> tuple:
    """ (tables: OrderedDict name -> [(col, type, is_pk)], refs: [(child, col, parent, col)]) """
    text = _read(path)
    tables = OrderedDict()
    for m in re.finditer(r'Table\s+"?(\w+)"?\s*\{(.*?)\}', text, re.S):
        cols = []
        for line in m.group(2).splitlines():
            c = re.match(r'\s*"?(\w+)"?\s+([\w\(\),]+)\s*(\[.*\])?', line)
            if c:
                cols.append((c.group(1), c.group(2), "primary key" in (c.group(3) or "")))
        tables[m.group(1)] = cols
    refs = []
    for m in re.finditer(r'Ref:\s*"?(\w+)"?\.\(?(\w+)\)?\s*([<>-])\s*"?(\w+)"?\.\(?(\w+)\)?', text):
        a, a_col, op, b, b_col = m.groups()
        if op == "<":
            refs.append((b, b_col, a, a_col))
        else:
            refs.append((a, a_col, b, b_col))
    return tables, refs


def build_dot(tables: OrderedDict, refs: list, derived: set) -> str:
    """ ER diagram in graphviz: parents above children (rankdir=TB, edge parent -> child) """
    fk_cols = {(child, col) for child, col, _, _ in refs}
    out = ['digraph db {',
           f'  graph [rankdir=TB, bgcolor="{C_CANVAS}", pad=0.3, nodesep=0.6, ranksep=0.9, fontname="Helvetica"];',
           '  node [shape=plain, fontname="Helvetica", fontsize=11];',
           f'  edge [color="{C_EDGE}", penwidth=1.2, dir=both, arrowtail=tee, arrowhead=crow, arrowsize=0.8];']
    for name, cols in tables.items():
        rows = [f'<TR><TD COLSPAN="2" ALIGN="LEFT" BGCOLOR="{C_HEADER}">'
                f'<FONT COLOR="white" POINT-SIZE="12"><B>{html.escape(name)}</B></FONT></TD></TR>']
        for col, col_type, is_pk in cols:
            is_derived = (name, col) in derived
            bg = f' BGCOLOR="{C_DERIVED}"' if is_derived else ""
            label = f"<B>{html.escape(col)}</B>" if is_pk else html.escape(col)
            tags = ""
            if is_pk:
                tags += f' <FONT POINT-SIZE="8" COLOR="{C_HEADER}">PK</FONT>'
            if (name, col) in fk_cols:
                tags += f' <FONT POINT-SIZE="8" COLOR="{C_HEADER}">FK</FONT>'
            if is_derived:
                tags += ' <FONT POINT-SIZE="8" COLOR="#777777"><I>derived</I></FONT>'
            rows.append(f'<TR><TD ALIGN="LEFT"{bg}>{label}{tags}&nbsp;&nbsp;</TD>'
                        f'<TD ALIGN="RIGHT"{bg}><FONT POINT-SIZE="9" COLOR="#777777">'
                        f'{html.escape(col_type)}</FONT></TD></TR>')
        out.append(f'  "{name}" [label=<<TABLE BORDER="1" COLOR="#d9d9d9" CELLBORDER="0" '
                   f'CELLSPACING="0" CELLPADDING="5" BGCOLOR="{C_ROW}">' + "".join(rows) + '</TABLE>>];')
    for child, _, parent, _ in refs:
        if child in tables and parent in tables:
            out.append(f'  "{parent}" -> "{child}";')
    has_parent = {child for child, _, parent, _ in refs if parent != child and parent in tables}
    roots = [name for name in tables if name not in has_parent]
    if roots:   # tables with no parents go on the top row (dot would otherwise sink them toward their children)
        out.append("  { rank=min; " + "; ".join(f'"{r}"' for r in roots) + "; }")
    out.append("}")
    return "\n".join(out)


def _link(target: Path, report_dir: Path) -> str:
    return quote(Path(os.path.relpath(target.resolve(), report_dir.resolve())).as_posix())


def sec_data_model(root: Path, rules: list, report_dir: Path) -> list:
    lines = ["## Data Model", ""]
    dbml = root / "docs" / "db.dbml"
    custom = next((root / "docs" / f"db_diagram{ext}" for ext in (".png", ".svg", ".jpg", ".jpeg")
                   if (root / "docs" / f"db_diagram{ext}").is_file()), None)
    derived_rules = [r for r in rules if r["derive"]]
    derived = set()
    for each in derived_rules:
        if "." in each["derive"]:
            cls, attr = each["derive"].split(".", 1)
            derived.add((cls, attr))

    if custom is not None:
        lines.append(f"![db diagram]({_link(custom, report_dir)})")
        lines.append("")
        lines.append(f"_Diagram supplied by you: `{_rel(custom, root)}`. Keep it in step with "
                     f"`docs/db.dbml`; schema changes are not reflected in it automatically._")
    elif dbml.is_file():
        tables, refs = parse_dbml(dbml)
        dot_text = build_dot(tables, refs, derived)
        dot_path = report_dir / "db_diagram.generated.dot"
        svg_path = report_dir / "db_diagram.generated.svg"
        dot_path.write_text(dot_text)
        if shutil.which("dot"):
            result = subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                lines.append(f"![db diagram]({_link(svg_path, report_dir)})")
                lines.append("")
                lines.append("_Generated from `docs/db.dbml` (parents above children; shaded rows are "
                             "derived by rules). To use your own layout, save it as `docs/db_diagram.png`._")
            else:
                lines.append(f"_Could not render the diagram: {_cell(result.stderr.strip()[:200])}_")
        else:
            lines.append("_Diagram not rendered: Graphviz `dot` is not installed (`brew install graphviz`). "
                         f"The graph source is in `{_rel(dot_path, root)}`._")
    else:
        lines.append("No `docs/db.dbml` found, and no `docs/db_diagram.png`. "
                     "Run `rebuild-from-database` to generate the dbml.")

    lines.append("")
    lines.append("### Derived columns")
    lines.append("")
    if not derived_rules:
        lines.append("None.")
        return lines
    lines.append("| Table | Column | Rule | Definition |")
    lines.append("|---|---|---|---|")
    for each in derived_rules:
        cls, _, attr = each["derive"].partition(".")
        lines.append(f"| {cls} | {attr} | {each['kind']} | {_code(each['text'])} |")
    return lines


# ======================================================================================
#  Security (RBAC)
# ======================================================================================

def _parse_security(root: Path):
    """ (defaults, grants) from security/declare_security.py, or None if absent/unparseable.
        defaults: [(role, read, insert, update, delete)]; grants: [(table, role, filter, req)] """
    path = root / "security" / "declare_security.py"
    if not path.is_file():
        return None
    src = _read(path)
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None

    roles = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Roles":
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Constant):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            roles[target.id] = stmt.value.value

    def role_of(node) -> str:
        text = _seg(src, node)
        if isinstance(node, ast.Attribute) and node.attr in roles:
            return roles[node.attr]
        return text.strip("\"'")

    defaults, grants = [], []
    src_lines = src.splitlines()
    for call in sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call)), key=lambda n: n.lineno):
        if not isinstance(call.func, ast.Name):
            continue
        kw = {k.arg: k.value for k in call.keywords if k.arg}
        if call.func.id == "DefaultRolePermission":
            def flag(name):
                node = kw.get(name)
                return isinstance(node, ast.Constant) and bool(node.value)
            defaults.append((role_of(kw.get("to_role")) if "to_role" in kw else "?",
                             flag("can_read"), flag("can_insert"), flag("can_update"), flag("can_delete")))
        elif call.func.id == "Grant":
            flt = kw.get("filter_debug")
            if isinstance(flt, ast.Constant):
                flt_text = str(flt.value)
            else:
                flt_text = _body(src, kw["filter"]) if "filter" in kw else ""
            before = "\n".join(src_lines[max(0, call.lineno - 9): call.lineno])
            req = re.findall(r'§\s*(\d+)', before)
            grants.append((_tidy(_seg(src, kw.get("on_entity"))) if "on_entity" in kw else "?",
                           role_of(kw.get("to_role")) if "to_role" in kw else "?",
                           flt_text, f"§{req[-1]}" if req else ""))
    return defaults, grants


def security_summary(root: Path) -> list:
    """ one line per Grant, for the requirement side-by-side """
    parsed = _parse_security(root)
    if not parsed:
        return []
    return [f"Grant on {table} to role {role}: {flt}" for table, role, flt, _ in parsed[1]]


def sec_security(root: Path) -> list:
    lines = ["## Security (RBAC)", ""]
    parsed = _parse_security(root)
    if parsed is None:
        lines.append("No (parseable) `security/declare_security.py`.")
        return lines
    defaults, grants = parsed
    env = _read(root / "config" / "default.env")
    m = re.search(r'^\s*SECURITY_ENABLED\s*=\s*(\w+)', env, re.M)
    enabled = (m.group(1).lower() in ("true", "yes", "1")) if m else False
    lines.append(f"**Security enabled: {'yes' if enabled else 'no'}** "
                 f"(`SECURITY_ENABLED` in `config/default.env`)."
                 + ("" if enabled else " The declarations below are not enforced until `genai-logic add-auth` is run."))
    lines.append("")
    lines.append("### Roles and CRUD (DefaultRolePermission)")
    lines.append("")
    if defaults:
        lines.append("| Role | Read | Insert | Update | Delete |")
        lines.append("|---|---|---|---|---|")
        mark = lambda v: "✅" if v else "—"
        for role, r, i, u, d in defaults:
            lines.append(f"| {_cell(role)} | {mark(r)} | {mark(i)} | {mark(u)} | {mark(d)} |")
    else:
        lines.append("None declared.")
    lines.append("")
    lines.append("### Row-level grants (Grant)")
    lines.append("")
    if grants:
        lines.append("| Table | Role | Filter | Requirement |")
        lines.append("|---|---|---|---|")
        for table, role, flt, req in grants:
            lines.append(f"| {_cell(table)} | {_cell(role)} | {_code(flt)} | {req} |")
    else:
        lines.append("None declared (`Grant`).")
    return lines


# ======================================================================================
#  Messages and APIs
# ======================================================================================

def _message_shape(root: Path, topic: str):
    for base in (root / "integration" / "kafka" / "message_formats",
                 *sorted((root / "docs" / "requirements").glob("*/message_formats"))):
        candidate = base / f"{topic}.json"
        if candidate.is_file():
            return candidate
    return None


def _is_model_ctor(call) -> str:
    """ 'models.Order(...)' / 'database.models.Order(...)' -> 'Order', else '' """
    func = call.func
    if isinstance(func, ast.Attribute) and func.attr[:1].isupper():
        owner = func.value
        if (isinstance(owner, ast.Name) and owner.id == "models") or \
                (isinstance(owner, ast.Attribute) and owner.attr == "models"):
            return func.attr
    return ""


def _import_map(tree) -> dict:
    """ imported name -> dotted module, from every 'from x import y' in the file (incl. inside functions) """
    names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for alias in node.names:
                names[alias.asname or alias.name] = node.module
    return names


PROJECT_PACKAGES = ("integration", "logic", "api")


def constructed_tables(root: Path, tree, fn, seen: set = None, depth: int = 4) -> set:
    """ tables whose rows a function constructs (models.X(...)), following calls to functions in the
        same file and in project modules it imports (integration/, logic/, api/). Unresolved calls
        add nothing: better a blank than a guess. """
    seen = seen if seen is not None else set()
    result = set()
    if fn is None or depth <= 0:
        return result
    functions = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    imports = _import_map(tree)
    for call in (n for n in ast.walk(fn) if isinstance(n, ast.Call)):
        table = _is_model_ctor(call)
        if table:
            result.add(table)
            continue
        if not isinstance(call.func, ast.Name):
            continue
        name = call.func.id
        if name in functions and functions[name] is not fn and (id(tree), name) not in seen:
            seen.add((id(tree), name))
            result |= constructed_tables(root, tree, functions[name], seen, depth - 1)
        elif name in imports and imports[name].split(".")[0] in PROJECT_PACKAGES:
            path = root / (imports[name].replace(".", "/") + ".py")
            if path.is_file():
                try:
                    other = ast.parse(_read(path))
                except SyntaxError:
                    continue
                target = next((n for n in ast.walk(other)
                               if isinstance(n, ast.FunctionDef) and n.name == name), None)
                if target is not None and (id(other), name) not in seen:
                    seen.add((id(other), name))
                    result |= constructed_tables(root, other, target, seen, depth - 1)
    return result


def collect_messages(root: Path, rules: list, report_dir: Path) -> list:
    """ Kafka topics (in/out) and HTTP endpoints, as dicts: direction, channel, name, handler, desc,
        tables, shape, file """
    rows = []

    sub_dir = root / "integration" / "kafka" / "kafka_subscribe_discovery"
    for each in sorted(sub_dir.glob("*.py")) if sub_dir.is_dir() else []:
        if each.name in SKIP_FILES:
            continue
        src = _read(each)
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        functions = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        for m in re.finditer(r'@bus\.handle\(\s*[\'"]([^\'"]+)[\'"]\s*\)\s*\n\s*def\s+(\w+)', src):
            topic, fn = m.group(1), m.group(2)
            shape = _message_shape(root, topic)
            rows.append({"direction": "in", "channel": "Kafka", "name": topic, "handler": f"{fn}()",
                         "desc": _doc1(functions.get(fn)) or "(no docstring)",
                         "tables": ", ".join(sorted(constructed_tables(root, tree, functions.get(fn)))),
                         "shape": shape, "file": _rel(each, root)})

    topic_patterns = (r'topic\s*=\s*[\'"]([^\'"]+)[\'"]', r'[\'"]topic[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]')
    for each in rules:
        if each["how"].startswith("event"):
            # only this event's own code: its function and its Rule.* call (never the rest of the file,
            # which may hold other events that publish elsewhere, or none)
            src = each.get("fn_src", "") + "\n" + each.get("call_src", "")
            m = next((x for x in (re.search(p, src) for p in topic_patterns) if x), None)
            if m:
                rows.append({"direction": "out", "channel": "Kafka", "name": m.group(1),
                             "handler": _tidy(each["text"]), "desc": each["desc"], "tables": "",
                             "shape": _message_shape(root, m.group(1)), "file": each["file"]})

    api_dir = root / "api" / "api_discovery"
    for each in sorted(api_dir.glob("*.py")) if api_dir.is_dir() else []:
        if each.name in API_STUB_FILES:
            continue
        src = _read(each)
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for fn in (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)):
            for dec in fn.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) \
                        and dec.func.attr == "route" and dec.args and isinstance(dec.args[0], ast.Constant):
                    methods = "GET"
                    for kw in dec.keywords:
                        if kw.arg == "methods":
                            methods = ",".join(_seg(src, kw.value).strip("[]\"' ").replace("'", "").split(","))
                    rows.append({"direction": "in", "channel": "HTTP", "name": f"{methods} {dec.args[0].value}",
                                 "handler": f"{fn.name}()", "desc": _doc1(fn) or "(no docstring)",
                                 "tables": "", "shape": None, "file": _rel(each, root)})
    return rows


def sec_messages(root: Path, rows: list, req_by_file: dict, report_dir: Path) -> list:
    lines = ["## Messages and APIs", ""]
    if not rows:
        lines.append("No Kafka topics or custom API endpoints found.")
        return lines
    lines.append("| Direction | Channel | Name | Handler | Tables created | Message shape | Requirement |")
    lines.append("|---|---|---|---|---|---|---|")
    for m in rows:
        shape = f"[{m['name']}.json]({_link(m['shape'], report_dir)})" if m["shape"] else ""
        handler = f"`{m['handler']}` - {m['desc']}" if m["direction"] == "in" else f"{m['handler']} - {m['desc']}"
        lines.append(f"| {'➡ in' if m['direction'] == 'in' else '⬅ out'} | {m['channel']} | `{_cell(m['name'])}` | "
                     f"{_cell(handler)} | {_cell(m['tables'])} | {shape} | "
                     f"{_cell('; '.join(req_by_file.get(m['file'], [])))} |")
    lines.append("")
    lines.append("_Topics and endpoints are read from the discovery folders. The condition that triggers "
                 "an outbound message lives in Python (see the rules under each requirement); here it is "
                 "described by the handler's docstring. \"Tables created\" lists rows the handler's code "
                 "constructs, following its calls within the project; blank means none were found, not "
                 "that none exist._")
    for topic in sorted({m["name"] for m in rows if m["channel"] == "Kafka" and m["shape"]}):
        shape = _message_shape(root, topic)
        lines.append("")
        lines.append("<details markdown>")
        lines.append(f"<summary>Message shape: {topic}</summary>")
        lines.append("")
        lines.append("```json")
        lines.append(_read(shape).rstrip())
        lines.append("```")
        lines.append("</details>")
    return lines


# ======================================================================================
#  Project summary (from readme, else from the creation prompt)
# ======================================================================================

SUMMARY_LINE_CAP = 15
SUMMARY_PLACEHOLDER_TEXT = ("PROJECT_SUMMARY_PLACEHOLDER", "have not been summarized yet")
INFERRED_PROMPT = re.compile(r'^\s*Create a project providing an admin app and JSON:API for database', re.I)
""" the one-liner `genai-logic create` writes when no real prompt exists - boilerplate, not a summary """


def _clean_markdown(lines: list) -> list:
    """ drop front matter, html comments, <style> blocks, images and &nbsp; spacers; collapse blanks """
    out = []
    in_comment = in_style = in_front = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0 and stripped == "---":
            in_front = True
            continue
        if in_front:
            if stripped == "---":
                in_front = False
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if stripped.startswith("<!--"):
            if "-->" not in line:
                in_comment = True
            continue
        if in_style:
            if "</style>" in line:
                in_style = False
            continue
        if stripped.startswith("<style"):
            if "</style>" not in line:
                in_style = True
            continue
        if re.match(r'^!\[.*\]\(.*\)\s*$', stripped) or stripped.startswith("<figure") \
                or stripped.startswith("<img") or stripped in ("&nbsp;", "&nbsp;&nbsp;"):
            continue
        if not stripped and out and not out[-1].strip():
            continue
        out.append(line.rstrip())
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def _cap(lines: list, cap: int = SUMMARY_LINE_CAP) -> tuple:
    """ first ~cap non-blank lines, cut at a paragraph boundary when that keeps most of them.
        returns (lines, was_cut) """
    count = 0
    for i, line in enumerate(lines):
        if line.strip():
            count += 1
        if count > cap:
            kept = lines[:i]
            last_blank = max((j for j, l in enumerate(kept) if not l.strip()), default=-1)
            if last_blank >= cap // 3:
                kept = kept[:last_blank]
            while kept and not kept[-1].strip():
                kept.pop()
            return kept, True
    return lines, False


def _readme_summary(path: Path) -> list:
    """ body of the first Summary/Overview heading (h1-h3) in a readme, or [] """
    lines = _clean_markdown(_read(path).splitlines())
    in_fence = False
    heads = []
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        m = re.match(r'^(#{1,3})\s+(.*?)\s*$', line)
        if m and not in_fence:
            heads.append((i, len(m.group(1)), m.group(2)))
    for n, (i, level, title) in enumerate(heads):
        if not re.search(r'summary|overview', title, re.I):
            continue
        end = len(lines)
        for j, lvl, _ in heads[n + 1:]:
            if lvl <= level:
                end = j
                break
        body = _clean_markdown(lines[i + 1:end])
        while body and (not body[-1].strip() or re.match(r'^\s*(-{3,}|\*{3,}|_{3,})\s*$', body[-1])):
            body.pop()   # a section-ending horizontal rule is not part of the summary
        text = "\n".join(body)
        if body and not any(p in text for p in SUMMARY_PLACEHOLDER_TEXT):
            return body
    return []


def _prompt_summary(path: Path) -> list:
    """ the creation prompt, minus // comments and the inferred one-liner, or [] """
    lines = [l.rstrip() for l in _read(path).splitlines() if not l.strip().startswith("//")]
    lines = _clean_markdown(lines)
    text = "\n".join(lines).strip()
    if not text or INFERRED_PROMPT.match(text):
        return []
    return lines


def project_summary(root: Path, report_dir: Path) -> list:
    """ markdown lines for an 'About this project' block, or [] if nothing usable.
        order: readme Summary/Overview section -> creation prompt """
    to_root = Path(os.path.relpath(root, report_dir)).as_posix()

    def fix_links(lines):
        pattern = re.compile(r'\]\((?!https?:|#|mailto:|/)([^)\s]+)\)')
        return [pattern.sub(lambda m: f"]({quote(to_root + '/' + m.group(1), safe='/#?=&:%')})", l) for l in lines]

    for name in ("readme.md", "readme_standard.md"):
        path = root / name
        if path.is_file():
            body = _readme_summary(path)
            if body:
                kept, cut = _cap(body)
                link = f"{to_root}/{name}"
                out = [f"**About this project** _(from [{name}]({quote(link)}))_", ""] + fix_links(kept)
                if cut:
                    out += ["", f"_… [more in {name}]({quote(link)})_"]
                return out
    prompt = root / "docs" / "requirements" / "project_creation_prompt.md"
    if prompt.is_file():
        body = _prompt_summary(prompt)
        if body:
            kept, cut = _cap(body)
            link = f"{to_root}/docs/requirements/project_creation_prompt.md"
            out = [f"**About this project** _(the prompt it was created from: "
                   f"[project_creation_prompt.md]({quote(link)}))_", ""]
            out += [("> " + l + "  ") if l.strip() else ">" for l in kept]
            if cut:
                out += ["", f"_… [more in project_creation_prompt.md]({quote(link)})_"]
            return out
    return []


# ======================================================================================
#  Assembly
# ======================================================================================

def _slug(title: str) -> str:
    """ github heading anchor """
    slug = re.sub(r'[^\w\- ]', '', title.lower())
    return slug.strip().replace(" ", "-")


def get_intro(prepend_wiki: str) -> list:
    """ user-owned intro text, up to the '# Behave Logic Report' heading """
    report_name = "Behave Logic Report"
    path = Path(prepend_wiki)
    if not path.is_file():
        return []
    result = []
    for each in path.read_text().splitlines():
        if '# ' + report_name in each:
            break
        result.append(each)
    return result


def add_spacing(lines: list) -> list:
    """ breathing room before headings: more before a section (##), less before a subsection (###) """
    out = []
    in_fence = False
    for line in lines:
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence:
            previous = next((l for l in reversed(out) if l.strip()), "")
            # a <details> block is an HTML block: it ends only at a blank line, so whatever follows
            # (a heading, a table) would be swallowed into it and shown as literal text
            if out and out[-1].strip() == "</details>" and line.strip():
                out.append("")
            if line.startswith("#") and out and out[-1].strip():
                out.append("")   # markdown headings need a blank line before them
            if line.startswith("## "):
                out += ["", "&nbsp;", "&nbsp;", ""]
            elif line.startswith("### ") and previous.strip() != "&nbsp;":
                out += ["", "&nbsp;", ""]
        out.append(line)
    return out


def tests_background() -> list:
    """ what these tests are, and what the logic log shows (the part worth explaining) """
    return [
        "These are Behave scenarios. Each one drives the running API the way any client would "
        "(create an order, change a quantity, ship it) and checks the result.",
        "",
        "**The logic log** is what makes them more than pass/fail. Business rules run inside the server "
        "on every commit, so the server records exactly what they did, and this report embeds that "
        "record for each scenario. Two things to look for:",
        "",
        "1. **It shows every rule that runs.** Each line is one rule execution, with the row's state, old "
        "and new values. You see not just that a test passed, but which rules ran and what each one changed.",
        "2. **The nesting shows multi-table chaining.** Indentation follows the cascade: a change to an Item "
        "adjusts its Order, which adjusts its Customer.",
        "",
        "<details markdown>",
        "<summary>How to read the logic log</summary>",
        "",
        "Open a scenario's \"Rules exercised and logic log\" block to see it. The log is shown in full, "
        "attribute values included, because those values are what you diagnose from when a rule produces "
        "an unexpected result.",
        "",
        "To read a log line:",
        "",
        "```",
        "....Order[16] {Update - Adjusting order: amount_total} id: 16, customer_id: 19, "
        "amount_total:  [0.0-->] 90.0",
        "```",
        "",
        "- The leading dots are the depth in the cascade: Item (2 dots), its Order (4), its Customer (6).",
        "- `Order[16]` is the row; `{...}` is the rule or action that ran; the rest is the row's "
        "attribute values at that step.",
        "- `[0.0-->] 90.0` marks a value the rules changed, with its old and new value.",
        "- The log is in phases: **ROW LOGIC** (derivations and constraints, as rows change), "
        "**COMMIT LOGIC** (checks that need the finished aggregates), and **AFTER_FLUSH LOGIC** "
        "(events that need database-assigned keys, such as the Kafka publish).",
        "",
        "More: [Logic Log](https://apilogicserver.github.io/Docs/Logic-Debug/#logic-log).",
        "",
        "</details>",
        "",
        "&nbsp;",
        "",
    ]


def tests_howto(root: Path, has_tests: bool) -> list:
    """ hide/show block: how to create tests (AI or by hand) and run them """
    names = []
    for each in parse_requirements(root):
        if each["num"] is None or each["features"]:
            names.extend(sorted(each["features"]) or [each["title"]])
    title = "How to add more tests, and run them" if has_tests else "How to create tests, and run them"
    named_prompt = []
    if names:
        named_prompt = [
            "Or, to have each requirement's tests linked in the Tests column above (it matches on "
            "`Feature:` name), say which names to use:",
            "",
            "```",
            "create tests from rules, one Feature per requirement, named exactly:",
            *[f"- {n}" for n in names],
            "```",
            "",
            "_Tests with other names still run and appear below; they just aren't linked to a requirement._",
            "",
        ]
    return [
        "<details markdown>",
        f"<summary>{title}</summary>",
        "",
        "**1. Have AI create them.** This project's context tells your AI assistant how "
        "(`.github/copilot-instructions.md`, `docs/training/testing.md`). Just say:",
        "",
        "```",
        "create tests from rules",
        "```",
        "",
        "The assistant reads `database/models.py`, the logic files and the custom APIs, then writes "
        "`.feature` files and step implementations under `test/api_logic_server_behave/features/`. "
        "It suggests how to run them; it does not run them for you.",
        "",
        *named_prompt,
        "**2. You can also define tests manually.** Add a `<name>.feature` file (Gherkin) under "
        "`test/api_logic_server_behave/features/` and its steps under `features/steps/`. "
        "The steps call the running API, so tests exercise the same rules as any client. "
        "See `docs/training/testing.md` for the patterns that keep tests repeatable.",
        "",
        "**Then run them** (server running, from `test/api_logic_server_behave`):",
        "",
        "```",
        "python behave_run.py --outfile=logs/behave.log",
        "python behave_logic_report.py run",
        "```",
        "",
        "</details>",
    ]


def main(behave_log: str, scenario_logs: str, wiki: str, prepend_wiki: str, project_dir: str = "../.."):
    """ main driver """
    root = Path(project_dir).resolve()
    wiki_path = Path(wiki).absolute()
    report_dir = wiki_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)

    rules = collect_rules(root)
    msg_rows = collect_messages(root, rules, report_dir)
    lines_requirements, req_by_file, features = sec_requirements(root, report_dir, rules, msg_rows,
                                                                 behave_log, scenario_logs)
    sections = [("Requirements Traceability To Rules", lines_requirements),
                ("Data Model", sec_data_model(root, rules, report_dir)),
                ("Security (RBAC)", sec_security(root)),
                ("Messages and APIs", sec_messages(root, msg_rows, req_by_file, report_dir))]

    # test evidence
    evidence = ["## Tests and Results", ""]
    log_path = Path(behave_log)
    n_scenarios = sum(features.values())
    if n_scenarios == 0:
        evidence.append("**No tests defined yet.** Everything above is generated from the project's rules, "
                        "data model, security declarations and integration files, so it is complete "
                        "without a test run. Add tests, then regenerate this report to see each scenario "
                        "with the rules it exercised.")
        evidence.append("")
        evidence.extend(tests_background())
        evidence.extend(tests_howto(root, has_tests=False))
    elif not log_path.is_file() or log_path.stat().st_size == 0:
        evidence.append(f"**{n_scenarios} scenario(s) defined, but no Behave run found** "
                        f"(`{behave_log}` is missing or empty). Run "
                        f"`python behave_run.py --outfile=logs/behave.log`, then regenerate this report.")
    else:
        outcome = scenario_results(behave_log) or {}
        passed = list(outcome.values()).count("passed")
        failed = list(outcome.values()).count("failed")
        evidence.append(f"**{'❌' if failed else '✅'} {n_scenarios} scenario(s): {passed} passed, "
                        f"{failed} failed** (from the last run, `{behave_log}`).")
        evidence.append("")
        evidence.extend(tests_background())
        evidence.extend(tests_howto(root, has_tests=True))
        evidence.extend(build_test_evidence(behave_log=behave_log, scenario_logs=scenario_logs))
    sections.append(("Tests and Results", evidence))

    # assemble
    out = list(get_intro(prepend_wiki))
    out.append("# Behave Logic Report")
    out.append("")
    outcome = scenario_results(behave_log) or {}
    n_failed = list(outcome.values()).count("failed")
    out.append(f"**Project:** {root.name} &nbsp;|&nbsp; **Generated:** "
               f"{datetime.datetime.now().strftime('%B %d, %Y %H:%M')} &nbsp;|&nbsp; "
               f"**Rules:** {len(rules)} &nbsp;|&nbsp; **Test scenarios:** {n_scenarios or 'none defined'}"
               f" &nbsp;|&nbsp; **Generator:** Behave Logic Report {__version__}")
    out.append("")
    if n_failed:
        failing_names = [f"{name}" for (_, name), status in outcome.items() if status == "failed"]
        out.append("")
        out.append(f"### ❌ {n_failed} of {len(outcome)} test scenarios FAILED")
        out.append("")
        out.extend(f"- ❌ {name}" for name in failing_names)
        out.append("")
        out.append("See [Tests and Results](#tests-and-results) for the failing step and the logic log.")
        out.append("")
    summary = project_summary(root, report_dir)
    if summary:
        out.extend(summary)
        out.append("")
    out.append("## Contents")
    out.append("")
    for title, _ in sections:
        out.append(f"- [{title}](#{_slug(title)})")
    out.append("")
    for _, section_lines in sections:
        out.extend(section_lines)
        out.append("")

    wiki_path.write_text("\n".join(add_spacing(out)))
    print(f'Wiki Output: {wiki_path}\n\n')


def ensure_working_directory():
    """ every default path (logs/, reports/, features/) and the project root (../..) is relative to
        test/api_logic_server_behave. Run from anywhere else, the report would silently describe the
        wrong folder (0 rules, no tests), so move to this file's own folder, as behave_run.py does. """
    if not Path("features").is_dir():
        here = Path(__file__).resolve().parent
        print(f"Not run from {here.name}: using {here} as the working directory")
        os.chdir(here)


def print_args(args, msg):
    print(msg)
    for each_arg in args:
        print(f'  {each_arg}')
    print(" ")


@click.group()
@click.pass_context
def cli(ctx):
    """
    Create the Behave Logic Report: requirements, rules, data model, security and
    messages (static), plus test evidence from behave.log and scenario_logic_logs.

    """
    pass


@cli.command("run")
@click.pass_context
@click.option('--behave_log',
              default=f'logs/behave.log',  # cwd set to test/api_logic_server_behave
              help="Log from the behave run")
@click.option('--scenario_logs',
              default=f'logs/scenario_logic_logs',
              help="Per-scenario logic logs")
@click.option('--wiki',
              default=f'reports/Behave Logic Report.md',
              help="Report to write")
@click.option('--prepend_wiki',
              default=f'reports/Behave Logic Report Intro micro.md',
              help="Your intro text, shown above the report")
@click.option('--project_dir',
              default=f'../..',
              help="Project root (default: two levels up from test/api_logic_server_behave)")
def run(ctx, behave_log: str, scenario_logs: str, wiki: str, prepend_wiki: str, project_dir: str):
    ensure_working_directory()
    main(behave_log=behave_log, scenario_logs=scenario_logs, wiki=wiki,
         prepend_wiki=prepend_wiki, project_dir=project_dir)


if __name__ == '__main__':  # debugger & python command line start here
    print(f'\nBehave Logic Report {__version__}, started at {os.getcwd()}')
    commands = sys.argv
    if len(sys.argv) > 1:
        print_args(commands, f'\n\nCommand Line Arguments:')
    cli()
