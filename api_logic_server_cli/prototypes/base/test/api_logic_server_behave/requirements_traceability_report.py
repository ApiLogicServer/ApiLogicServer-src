from pathlib import Path
from collections import OrderedDict
from urllib.parse import quote
import datetime
import html
import os
import hashlib
import ast
import re
import shutil
import subprocess
import sys
import click

"""
Requirements Traceability Report (generator: behave_logic_report.py) - a governance exhibit, generated as one markdown file.

Sections, in the order an auditor reads them (each is an H2, so each shows in a TOC):

    1. Requirements Coverage            forward (requirement -> rules/handlers/grants -> tests) and
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
  2.12 - Messages and APIs now lists custom API methods (@jsonapi_rpc, served at /api/<Class>/<method>) and the EAI debug
        endpoints (register_consume_debug / register_queue_reset in the project's thin debug file); before, only
        @app.route functions were found, so a project whose API is a jsonapi_rpc class showed "0 HTTP endpoints". A use-case
        folder's requirements.md is no longer counted as another requirement when its Feature lines are already in a numbered
        section (demo_eai reported 8 requirements; there are 5). Found by the level 1 diagnostic (Oct 24 2026).
  2.11 - Run time. behave_run.py writes "Behave run time: N s" into the log and features/environment.py records each
        scenario's seconds (logs/scenario_times.json). The report shows the run's time in At a Glance, the Coverage
        summary and the Tests and Results line, and each scenario's time next to its result.
  2.10 - Skipped scenarios are reported as skipped (they were counted as passed): results are passed / failed /
        skipped, a requirement whose scenarios all skipped is flagged, and the verdict is a warning. Messages and
        APIs: a Kafka mode note above the table (simulated through /consume_debug, or live through a broker - read from the
        per-scenario record the steps write to logs/delivery_modes.json, else from KAFKA_SERVER), the "Tests mention it" column moved next to Name and marked "simulated" for Kafka channels in
        fallback mode, and a Kafka mode line in At a Glance.
  2.9 - Provenance section at the end: date, generator version, which text the report used (and its hash), when the
        tests last ran, source commit (if the project is in git), when the project was created, and the requirement files
        it read (with hashes).
  2.8 - At a Glance: a verdict line and scorecard right under the header (requirements, tests, last run, rules,
        security, messages), with a cue on what the status means. Template markers use a gear (> ⚙ generated:) so they
        are not mistaken for fold triangles.
  2.7 - Contents and the fixed ### / #### headings are in the template too, so every heading matches (and can be renamed
        with a title comment, or given an introduction).
  2.6 - The template mirrors the report from the top: title, subtitle, opening text, the Background fold written
        out, then each section. Generated parts show as visible '> ▶ generated:' lines. The opening text moved
        from above the title to under it.
  2.5 - The template is a skeleton of the report: same order, the report's own static text (including its folds) as
        <!-- text: name --> blocks, and <!-- generated: ... --> lines where generated content goes. Table notes
        are now a visible one-line cue plus a fold with the detail.
  2.4 - The script is requirements_traceability_report.py, writing docs/requirements/Requirements Traceability Report.md (was reports/; links are
        relative to the report's folder) and
        reading reports/Requirements Traceability Report Template.md. behave_logic_report.py remains as a
        shim that runs it, and the older Template / Intro file names are still read.
  2.3 - Renamed "Requirements Traceability Report" (first section: "Requirements Coverage"). The template file
        is now laid out like the report: '#' title with subtitle, '##' section headings as the markers, and
        <!-- title: New Name --> under a heading to rename a section.
  2.2 - Customizable text. reports/Behave Logic Report Template.md holds the introduction to each ##
        section (cover, background, requirements, data-model, security, messages, tests), marked
        <!-- section: name -->. A missing section uses the built-in text; an old-style
        "Behave Logic Report Intro.md" still works (as the cover). Only prose is customizable.
  2.1 - From a review of the 2.0 report.
        * Default intro file is reports/Behave Logic Report Intro.md (the identical "Intro micro.md" is gone).
        * Header states when the tests last ran, and warns if rules or tests changed after that run.
        * "Rules seen" counts against all rules; a rule the engine log cannot name is listed, not dropped.
        * Messages and APIs: "Tests mention it" column - no test naming a topic/endpoint means a passing
          scenario says nothing about that channel.
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

__version__ = "2.12"

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
                        doc_string = []
                        if step_code[comment_start].count('"""') >= 2:
                            # one-line docstring: """text""" - opening and closing on the same line
                            one_line = step_code[comment_start].strip().strip('"').strip()
                            doc_string.append(one_line + '\n')
                            doc_string_line = comment_start
                        else:
                            doc_string_line = comment_start+1
                            while doc_string_line < len(step_code):
                                if '"""' in step_code[doc_string_line]:
                                    break
                                doc_string.append(step_code[doc_string_line][indent:])
                                doc_string_line += 1
                        scenario_line = doc_string_line+1
                        if scenario_line >= len(step_code):
                            continue
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
    times = scenario_times(behave_log)
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
            mark = {"passed": " ✅", "failed": " ❌ FAILED", "skipped": " ⚠ SKIPPED"}.get(results.get((feature_name, name)), "")
            took = times.get(f"{feature_name} / {name}")
            if took is not None:
                mark += f" ({_secs(took)})"
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
    # A use-case folder's requirements.md is the verbatim excerpt that anchors its logic file; when its Feature lines are
    # all in a numbered section, it is the same requirement, not another one (it would be counted twice).
    numbered_features = set()
    for each in items.values():
        if each["num"] is not None:
            numbered_features |= each["features"]
    kept = [each for each in items.values()
            if not (each["num"] is None and each["features"] and each["features"] <= numbered_features)]
    return sorted(kept, key=lambda i: (i["num"] is None, i["num"] or 0, i["title"]))


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
    return fill(TEXT.get("diagrams-howto", []), diagram_title=title, project=project,
                manager_clause=(f" (`{manager.name}`)" if manager else "")) + [""]


def scenario_results(behave_log: str):
    """ {(feature, scenario): 'passed' | 'failed' | 'skipped'} read from behave.log, or None if there is no run.
        Behave writes 'Assertion Failed: ...' or a Traceback under a failing step; a scenario with
        neither passed, unless some of its steps never ran (listed with no location, e.g. after
        context.scenario.skip()): that scenario is skipped. (The scaffold's placeholder feature is left out.) """
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
        elif current and results[current] == "passed" \
                and re.match(r'^\s+(Given|When|Then|And|But)\s.*#\s*None\s*$', line):
            results[current] = "skipped"      # a step that never ran, and nothing failed
    return results or None


def _count(results, status: str):
    """ how many scenarios have this status (None when there is no test run) """
    return None if results is None else list(results.values()).count(status)


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
        ran = rec["passed"] + rec["failed"] + rec["skipped"]
        icon = "❌ " if rec["failed"] else ("⚠ " if rec["skipped"] else ("✅ " if ran >= rec["scenarios"] else ""))
        text = icon + text + f": {rec['passed']} passed" + (f", **{rec['failed']} FAILED**" if rec["failed"] else "")
        if rec["skipped"]:
            text += f", **{rec['skipped']} skipped**"
        if ran < rec["scenarios"]:
            text += f", {rec['scenarios'] - ran} not run"
    return text


def _gap_list(labels: list) -> str:
    return ", ".join(labels) if labels else "none"


def sec_requirements(root: Path, report_dir: Path, rules: list, msg_rows: list,
                     behave_log: str = "logs/behave.log", scenario_logs: str = "logs/scenario_logic_logs") -> tuple:
    """ requirements traceability: coverage summary, matrix, rule coverage by tests, detail per requirement.
        returns (lines, req_by_file, features) """
    lines = [f"## {title('requirements')}", ""]
    items = parse_requirements(root)
    files = implementation_files(root)
    features = parse_features(root)
    req_by_file = {}

    declarative = sum(1 for r in rules if r["how"].startswith("declarative"))
    python_fn = sum(1 for r in rules if r["how"] == "Python function")
    events = sum(1 for r in rules if r["how"].startswith("event"))
    n_files = len({r["file"] for r in rules})

    lines.extend(text("requirements"))

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
        rec["passed"], rec["failed"], rec["skipped"] = mine.count("passed"), mine.count("failed"), mine.count("skipped")
    lines += [f"### {title('coverage-summary')}", ""] + text("coverage-summary") + ["| Measure | Result |", "|---|---|"]
    n = len(records)
    lines.append(f"| Requirements | {n} |")
    lines.append(f"| Implemented (at least one file) | {n - len(no_impl)} of {n}"
                 + (f" - gap: {_gap_list(no_impl)}" if no_impl else "") + " |")
    lines.append(f"| Tested (at least one scenario) | {n - len(no_tests)} of {n}"
                 + (f" - gap: {_gap_list(no_tests)}" if no_tests else "") + " |")
    FACTS.clear()
    FACTS.update(n_req=n, no_impl=list(no_impl), no_tests=list(no_tests), n_rules=len(rules),
                 n_declarative=declarative, n_python=python_fn, n_events=events, seen=None,
                 passed=_count(results, "passed"), failed=_count(results, "failed"),
                 skipped=_count(results, "skipped") or 0,
                 skipped_reqs=[r["label"] for r in records if r["skipped"] and not r["passed"] and not r["failed"]])
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
        n_skipped = list(results.values()).count('skipped')
        lines.append(f"| Test results (last run) | {'❌' if n_failed else ('⚠' if n_skipped else '✅')} "
                     f"{list(results.values()).count('passed')} passed, {n_failed} failed"
                     + (f", {n_skipped} skipped" if n_skipped else "")
                     + (f"; took {_secs(run_seconds(behave_log))}" if run_seconds(behave_log) is not None else "")
                     + (f" - failing: {_cell(_gap_list(failing))}" if failing else "")
                     + (f" - skipped, not verified: {_cell(_gap_list(FACTS['skipped_reqs']))}" if FACTS["skipped_reqs"] else "")
                     + " |")
    if coverage is None:
        lines.append("| Rules seen in a scenario's log | no test run found |")
    else:
        lines.append(f"| Scenarios with a logic log | {cov[1]} of {cov[2]}"
                     + (" (plus the scaffold's shared log, which is included)" if cov[3] else "") + " |")
        matchable = [i for i, v in coverage.items() if v is not None]
        never = [rules[i] for i in matchable if not coverage[i]]
        unmatched = [rules[i] for i, v in coverage.items() if v is None]
        never_text = _gap_list([_code(r["text"]) for r in never])
        unmatched_text = _gap_list([_code(r["text"]) for r in unmatched])
        FACTS["seen"] = (len(matchable) - len(never), len(coverage))
        lines.append(f"| Rules seen in at least one scenario's log | {len(matchable) - len(never)} of {len(coverage)}"
                     + (f" - not seen: {never_text}" if never else "")
                     + (f" ({len(unmatched)} not counted: the engine's log does not name {unmatched_text}, "
                        f"so it cannot be matched)" if unmatched else "") + " |")
    lines.append("")
    lines.extend(text("coverage-note"))

    # ---- traceability matrix
    lines += ["", f"### {title('traceability-matrix')}", ""] + text("traceability-matrix")
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
    lines += ["", f"### {title('rule-coverage')}", ""] + text("rule-coverage")
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
        lines += [""] + text("rule-coverage-note")

    # ---- inventory line + per-requirement detail
    lines += ["", f"### {title('requirements-detail')}", ""] + text("requirements-detail")
    lines += [f"**{len(rules)} rules** in {n_files} files: {declarative} declarative (sum, count, copy, "
              f"formula and constraint expressions), {python_fn} backed by a Python function, "
              f"{events} events (Python).", ""]
    lines += text("inventory-note") + text("detail-intro")
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
        lines += ["", f"#### {title('not-traced')}", ""] + text("not-traced")
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
    lines = [f"## {title('data-model')}", ""] + text("data-model")
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
                lines.extend(text("data-model-note"))
            else:
                lines.append(f"_Could not render the diagram: {_cell(result.stderr.strip()[:200])}_")
        else:
            lines.append("_Diagram not rendered: Graphviz `dot` is not installed (`brew install graphviz`). "
                         f"The graph source is in `{_rel(dot_path, root)}`._")
    else:
        lines.append("No `docs/db.dbml` found, and no `docs/db_diagram.png`. "
                     "Run `rebuild-from-database` to generate the dbml.")

    lines.append("")
    lines.append(f"### {title('derived-columns')}")
    lines.append("")
    lines.extend(text("derived-columns"))
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


def _security_enabled(root: Path) -> bool:
    env = _read(root / "config" / "default.env")
    m = re.search(r'^\s*SECURITY_ENABLED\s*=\s*(\w+)', env, re.M)
    return (m.group(1).lower() in ("true", "yes", "1")) if m else False


def security_summary(root: Path) -> list:
    """ one line per Grant, for the requirement side-by-side """
    parsed = _parse_security(root)
    if not parsed:
        return []
    return [f"Grant on {table} to role {role}: {flt}" for table, role, flt, _ in parsed[1]]


def sec_security(root: Path) -> list:
    lines = [f"## {title('security')}", ""] + text("security")
    parsed = _parse_security(root)
    if parsed is None:
        lines.append("No (parseable) `security/declare_security.py`.")
        return lines
    defaults, grants = parsed
    enabled = _security_enabled(root)
    lines.append(f"**Security enabled: {'yes' if enabled else 'no'}** "
                 f"(`SECURITY_ENABLED` in `config/default.env`)."
                 + ("" if enabled else " The declarations below are not enforced until `genai-logic add-auth` is run."))
    lines.append("")
    lines.append(f"### {title('roles')}")
    lines.append("")
    lines.extend(text("roles"))
    if defaults:
        lines.append("| Role | Read | Insert | Update | Delete |")
        lines.append("|---|---|---|---|---|")
        mark = lambda v: "✅" if v else "—"
        for role, r, i, u, d in defaults:
            lines.append(f"| {_cell(role)} | {mark(r)} | {mark(i)} | {mark(u)} | {mark(d)} |")
    else:
        lines.append("None declared.")
    lines.append("")
    lines.append(f"### {title('grants')}")
    lines.append("")
    lines.extend(text("grants"))
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
        # custom API methods: @jsonapi_rpc on a safrs class method is served at /api/<Class>/<method>
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            for fn in (n for n in cls.body if isinstance(n, ast.FunctionDef)):
                for dec in fn.decorator_list:
                    target = dec.func if isinstance(dec, ast.Call) else dec
                    called = target.id if isinstance(target, ast.Name) else \
                        target.attr if isinstance(target, ast.Attribute) else ""
                    if called != "jsonapi_rpc":
                        continue
                    methods = "POST"
                    for kw in (dec.keywords if isinstance(dec, ast.Call) else []):
                        if kw.arg == "http_methods":
                            methods = ",".join(_seg(src, kw.value).strip("[]\"' ").replace("'", "").split(","))
                    rows.append({"direction": "in", "channel": "HTTP", "name": f"{methods} /api/{cls.name}/{fn.name}",
                                 "handler": f"{fn.name}()", "desc": _doc1(cls) or _doc1(fn) or "(no docstring)",
                                 "tables": "", "shape": None, "file": _rel(each, root)})
        # EAI debug endpoints: registered inside integration/system/EaiDebug.py, so the project file has no route decorator
        debug = {"register_consume_debug": ("topic", "GET /consume_debug/{key}",
                                            "EAI debug (development only, no authentication): sends the message in ?file= "
                                            "to the topic, live through Kafka or simulated"),
                 "register_queue_reset": ("name", "POST /consume_debug/{key}/reset",
                                          "EAI debug (development only, destructive): purges the messages in the "
                                          "pipeline's topics")}
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            called = call.func.id if isinstance(call.func, ast.Name) else \
                call.func.attr if isinstance(call.func, ast.Attribute) else ""
            if called not in debug:
                continue
            arg_name, route, desc = debug[called]
            given = {kw.arg: kw.value for kw in call.keywords}.get(arg_name)
            if given is None and len(call.args) > 1:
                given = call.args[1]            # register_*(app, <topic or name>, ...)
            if isinstance(given, ast.Constant) and isinstance(given.value, str):
                rows.append({"direction": "in", "channel": "HTTP", "name": route.format(key=given.value),
                             "handler": f"{called}()", "desc": desc,
                             "tables": "", "shape": None, "file": _rel(each, root)})
    return rows


def _test_text(root: Path) -> str:
    """ all feature and step text, to see which topics and endpoints the tests mention """
    base = root / "test" / "api_logic_server_behave" / "features"
    parts = [_read(p) for p in sorted(base.rglob("*")) if p.suffix in (".feature", ".py")] if base.is_dir() else []
    return "\n".join(parts)


def kafka_server(root: Path) -> str:
    """ the Kafka broker address in use (environment, else config/default.env), or "" when KAFKA_SERVER is not set:
        the platform then runs Kafka in fallback mode (no producer or consumer; /consume_debug is the test path) """
    value = os.environ.get("KAFKA_SERVER")
    if value is None:
        env = root / "config" / "default.env"
        for line in (_read(env).splitlines() if env.is_file() else []):
            m = re.match(r'^\s*KAFKA_SERVER\s*=\s*(.*?)\s*$', line)
            if m:
                value = m.group(1)
    value = (value or "").strip().strip('"\'')
    return "" if value in ("", "None") else value


def delivery_modes(root: Path) -> dict:
    """ how the last test run delivered Kafka messages: {'Feature / Scenario': {'mode': 'live'|'simulated',
        'broker': ...}}, written by the steps to test/api_logic_server_behave/logs/delivery_modes.json; {} if none """
    path = root / "test" / "api_logic_server_behave" / "logs" / "delivery_modes.json"
    if not path.is_file():
        return {}
    try:
        import json
        raw = json.loads(_read(path))
    except ValueError:
        return {}
    return {k: (v if isinstance(v, dict) else {"mode": v}) for k, v in raw.items()}


def kafka_delivery(root: Path, tests_text: str) -> tuple:
    """ ('live' | 'simulated' | 'mixed', broker): how the tests reached Kafka. From the run's own record when there is
        one; else tests that call /consume_debug are simulated; else KAFKA_SERVER decides """
    modes = delivery_modes(root)
    if modes:
        kinds = {v.get("mode") for v in modes.values()}
        broker = next((v.get("broker") for v in modes.values() if v.get("broker")), "") or kafka_server(root)
        return ("live" if kinds == {"live"} else "simulated" if kinds == {"simulated"} else "mixed"), broker
    if "consume_debug" in tests_text:
        return "simulated", ""
    server = kafka_server(root)
    return ("live", server) if server else ("simulated", "")


def _mentions(name: str, text: str) -> bool:
    key = name.split()[-1].rstrip("/").split("/")[-1]
    return bool(key and re.search(rf'(?<![\w]){re.escape(key)}(?![\w])', text))


def _tests_name(name: str, text: str, kafka: dict = None) -> str:
    """ does any test mention this topic or endpoint? (a mention is not proof of delivery, but no mention is).
        kafka: for a Kafka row, {'mode': 'live'|'simulated'|'mixed', 'publish': bool} """
    mentioned = _mentions(name, text)
    if kafka is None:
        return "✅" if mentioned else "⚠ no test mentions it"
    if kafka["publish"]:      # an outbound message the tests check in the server log, not on the topic
        return "⚠ message checked in the log, not on the topic" if mentioned else "⚠ no test mentions it"
    if kafka["mode"] == "live":
        return "✅ live"      # the live scenarios cannot pass unless the consumers ran
    if mentioned:
        return "⚠ simulated (no broker)" if kafka["mode"] == "simulated" else "⚠ mixed: live and simulated"
    return "⚠ no test mentions it"


def sec_messages(root: Path, rows: list, req_by_file: dict, report_dir: Path) -> list:
    lines = [f"## {title('messages')}", ""] + text("messages")
    if not rows:
        lines.append("No Kafka topics or custom API endpoints found.")
        return lines
    tests_text = _test_text(root)
    check = bool(tests_text.strip())
    kafka = any(m["channel"] == "Kafka" for m in rows)
    mode, server = kafka_delivery(root, tests_text) if kafka else ("simulated", "")
    if kafka:
        lines.extend(text("kafka-mode-live", server=server or "broker") if mode == "live" else
                     text("kafka-mode-mixed", server=server or "broker") if mode == "mixed" else text("kafka-mode-simulated"))
    # the status column is next to the name, so it is still visible when a wide table is cut off
    lines.append("| Direction | Channel | Name |" + (" Tests mention it |" if check else "")
                 + " Handler | Tables created | Message shape | Requirement |")
    lines.append("|---|---|---|" + ("---|" if check else "") + "---|---|---|---|")
    for m in rows:
        shape = f"[{m['name']}.json]({_link(m['shape'], report_dir)})" if m["shape"] else ""
        handler = f"`{m['handler']}` - {m['desc']}" if m["direction"] == "in" else f"{m['handler']} - {m['desc']}"
        kafka_row = {"mode": mode, "publish": m["direction"] == "out" and not m["name"].endswith("_processed")} \
            if m["channel"] == "Kafka" else None
        lines.append(f"| {'➡ in' if m['direction'] == 'in' else '⬅ out'} | {m['channel']} | `{_cell(m['name'])}` |"
                     + (f" {_tests_name(m['name'], tests_text, kafka_row)} |" if check else "")
                     + f" {_cell(handler)} | {_cell(m['tables'])} | {shape} | "
                     f"{_cell('; '.join(req_by_file.get(m['file'], [])))} |")
    lines.append("")
    if check:
        lines.extend(text("tests-mention-note"))
    lines.extend(text("messages-note"))
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


DEFAULT_TEMPLATE = '''<!-- Text for the report, laid out in the report's own order, so you can read it top to bottom against the report.
     The text under a heading, and each block introduced by a comment line  text: name, replaces the built-in text.
     Leave one out to keep the built-in text, or leave it empty to show nothing.
     Grey lines starting with  > ⚙ generated:  show where generated content (tables, counts, logs) appears; they are fixed.
     To rename a section, put a comment line  title: New Name  under its heading.
     The first heading (single #) is the report's title, with a subtitle under it. Double curly braces are filled in by the generator. -->

# Requirements Traceability Report

This report shows requirements, the rules created from them, and the tests created from those rules.

<!-- text: cover -->
This report is generated from the project's own files: its requirements, the rules and integrations built from them, and the tests that check them. Nothing in it is written by hand. Open **Background** (below the summary) for what the terms mean, how to read the report, and what it does and does not establish.

> ⚙ generated: project line (name, date, rule and test counts, generator version), last test run, and a banner if any scenario failed

## At a Glance

<!-- (no introduction by default; add one here) -->

> ⚙ generated: verdict and scorecard (status, requirements, tests, last run, rules, security, messages)

<!-- text: scorecard-note -->
_Status: ✅ every requirement is implemented and tested, all scenarios pass, and the results are current. ⚠ a requirement is untested or unimplemented, there is no test run, or files changed since the last run. ❌ a scenario failed. This reports what was traced and tested, not that the system is correct._

> ⚙ generated: About this project (from the project's readme)

<!-- text: background -->
<details markdown>
<summary>Background: what this report is, and how to read it</summary>

**What a requirement is**

A **requirement** is a statement of business behavior, written in plain language as a Gherkin feature (Given / When / Then). It lives in the project at `docs/requirements/<name>/requirements.md`. The system is built from these requirements, and this report is organized around them.

**How the system was built**

1. **Requirements** state what the system must do.
2. **Rules and integrations** implement them. A *rule* is a declaration about the data (for example, "a customer's balance is the sum of the unshipped order totals, and must not exceed the credit limit"). Rules are not called by code: the engine enforces them on every commit, whether the change came from the Admin App, the API, or a message. *Integrations* are the API endpoints and Kafka topics.
3. **Tests** (Behave scenarios) drive the running system the way any client would and check the outcome.
4. **This report** connects them: each requirement, to the rules and handlers that implement it, to the tests that exercise it, to the logic log that shows which rules ran.

**How to read it**

| If you are... | Start with | Look for |
|---|---|---|
| Business owner | *Requirements in detail* | The requirement text, then the **Tests** line under it: does a test exist, and did it pass? |
| Auditor | *Coverage summary*, *Rule coverage by tests*, *Messages and APIs* | Gaps (untested, untraced), the date of the last test run, and how each rule was shown to run |
| Developer | *Tests and Results* | Each scenario's logic log: every rule that ran, in order, with old and new values |

**What this report establishes, and what it does not**

**It establishes**
- Which files and rules implement each requirement, read from the project's source.
- Which scenarios ran at the last test run, and whether each passed.
- Which rules the engine reported running in each scenario's logic log.

**It does not establish**
- That a requirement is complete or correct. It traces what was written down.
- That a rule took effect because it appears in a log. An event runs on every commit of its class and decides for itself whether to act.
- That a constraint was exercised, unless a scenario made it reject a transaction. A constraint appears in the log only when it rejects.
- That a message reached a broker or an endpoint, unless a test step looks for it there. The *Messages and APIs* table flags channels no test mentions.
- That the results are current. They are as old as the last test run, shown in the header, and the header warns if files changed after it.
- Which version of a requirement the code was built against, or which clause of a requirement a given rule serves.

**Terms**

| Term | Meaning |
|---|---|
| Requirement | A Gherkin feature describing business behavior; the unit this report traces. |
| Rule | A declaration about data (sum, count, formula, copy, constraint) that the engine enforces at every commit. |
| Event | Python code the engine calls when a row of a given class changes (for example, to publish a message). |
| Handler | Code that serves an API endpoint or consumes a Kafka topic. |
| Scenario | One Behave test: a short Given / When / Then script run against the live API. |
| Logic log | The engine's record of every rule it ran in a transaction, nested to show cascades (an Item change adjusts its Order, which adjusts its Customer). |
| Phase | The step of a commit: ROW LOGIC (derivations, constraints), COMMIT LOGIC (checks that need finished totals), AFTER_FLUSH LOGIC (events that need database-assigned keys, such as publishing). |
| Seen | The engine reported running the rule in that scenario's log. |

</details>

## Contents

<!-- (no introduction by default; add one here) -->

> ⚙ generated: one link per section above

## Requirements Coverage

Traceability here is **forward** (requirement, to the rules, handlers and grants that implement it, to the tests that exercise it) and **backward** (implementation and tests, to the requirement they serve). Anything with no requirement is listed as untraced, and every requirement with no implementation or no test is listed as a gap. Links are made by the `Feature:` names and `§N` tags that requirements, code and tests carry.

### Coverage summary

> ⚙ generated: coverage summary table

<!-- text: coverage-note -->
_Test results are as current as the last run (see the header). A gap is any requirement with no implementation or no test._

<details markdown>
<summary>How to read this table</summary>

Test results are read from `logs/behave.log`, so they are only as current as that run. Not recorded here: which version of a requirement the code was built against, and which clause of a requirement a given rule serves.

</details>

### Traceability matrix

> ⚙ generated: matrix: requirement, implemented by, rules, tests

### Rule coverage by tests

> ⚙ generated: table: rule, requirement, scenarios where the engine's log shows it

<!-- text: rule-coverage-note -->
_"Seen" means the engine's log shows the rule ran, not proof that it took effect._

<details markdown>
<summary>How to read this table</summary>

"Seen" means the engine reported running the rule in that scenario's logic log. A scenario can only contribute if it has a log (see the coverage summary): a test that does not open one writes into whichever log was open last, and its rules are then credited to that scenario, or to the shared log. An event's function runs on every commit of its class, and its own condition decides whether it acts, so seen does not mean it took effect. A constraint appears in the log only when it rejects a transaction, so it is seen only in scenarios that make it reject. "Not seen" therefore means no log shows it, not that no test ran it.

</details>

### Requirements in detail

> ⚙ generated: rule counts for the project

<!-- text: inventory-note -->
_Declarative rules are read directly from their declarations; functions and events are Python, so the report shows each one's docstring, not an analysis of its code._

<!-- text: detail-intro -->
Each requirement is followed by the rules and handlers in the files that implement it. Logic diagrams are shown (click to expand) where they exist.

<!-- text: diagrams-howto -->
<details markdown>
<summary>{{diagram_title}}</summary>

Needs Graphviz (`brew install graphviz`). Tell your AI assistant:

```
create logic diagram for each requirement
```

or run this from the Manager root{{manager_clause}}:

```
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py {{project}} --each
```

Each diagram is saved under `docs/requirements/<name>/logic_diagrams/`. Then regenerate this report (`python requirements_traceability_report.py run`, from `test/api_logic_server_behave`).

</details>

&nbsp;

> ⚙ generated: one "#### §N requirement" block per requirement: its text, its rules and handlers, and a fold with its logic diagram

#### Rules not traced to a requirement

> ⚙ generated: table of rules that no requirement claims

## Data Model

<!-- (no introduction by default; add one here) -->

> ⚙ generated: database diagram

<!-- text: data-model-note -->
_Generated from `docs/db.dbml` (parents above children; shaded rows are derived by rules). To use your own layout, save it as `docs/db_diagram.png`._

### Derived columns

> ⚙ generated: table of derived columns and their rules

## Security (RBAC)

<!-- (no introduction by default; add one here) -->

> ⚙ generated: security status

### Roles and CRUD (DefaultRolePermission)

> ⚙ generated: table

### Row-level grants (Grant)

> ⚙ generated: table

## Messages and APIs

<!-- (no introduction by default; add one here) -->

<!-- text: kafka-mode-simulated -->
**Kafka mode: simulated (no broker).** `KAFKA_SERVER` is not set, so no Kafka consumer or producer runs. The tests deliver inbound messages by calling `/consume_debug`, which runs the same parse-and-save function the live consumer uses, so lookups, rules and the saved message are exercised, but Kafka delivery itself is not. Outbound messages are built and logged, not sent. To test with a real broker, set `KAFKA_SERVER` and `KAFKA_CONSUMER_GROUP` (see `integration/kafka/kafka_readme.md`).

<!-- text: kafka-mode-live -->
**Kafka mode: live ({{server}}).** The tests sent inbound messages through a real broker: `/consume_debug` published them to topic `order_b2b`, the server's consumers processed them, and the tests then checked the results. Outbound `order_shipping` messages are checked in the server log, not read back from the topic.

<!-- text: kafka-mode-mixed -->
**Kafka mode: mixed.** Some scenarios sent messages through a live broker ({{server}}) and some were simulated through `/consume_debug`. The Scenario names and the table below say which.

> ⚙ generated: messages and APIs table

<!-- text: tests-mention-note -->
_"Tests mention it" checks the test sources, not delivery._

<details markdown>
<summary>How to read this column</summary>

A passing scenario proves a message reached a topic or an endpoint only if its steps look for it there. A handler that ran (see the logic log) is weaker evidence than a step that consumes the message. Channels no test mentions are flagged.

</details>

<!-- text: messages-note -->
<details markdown>
<summary>How to read this table</summary>

Topics and endpoints are read from the discovery folders. The condition that triggers an outbound message lives in Python (see the rules under each requirement); here it is described by the handler's docstring. "Tables created" lists rows the handler's code constructs, following its calls within the project; blank means none were found, not that none exist.

</details>

> ⚙ generated: message shapes (one fold per topic)

## Tests and Results

> ⚙ generated: pass/fail status line

<!-- text: intro -->
These are Behave scenarios. Each one drives the running API the way any client would (create an order, change a quantity, ship it) and checks the result.

**The logic log** is what makes them more than pass/fail. Business rules run inside the server on every commit, so the server records exactly what they did, and this report embeds that record for each scenario. Two things to look for:

1. **It shows every rule that runs.** Each line is one rule execution, with the row's state, old and new values. You see not just that a test passed, but which rules ran and what each one changed.
2. **The nesting shows multi-table chaining.** Indentation follows the cascade: a change to an Item adjusts its Order, which adjusts its Customer.

<details markdown>
<summary>How to read the logic log</summary>

Open a scenario's "Rules exercised and logic log" block to see it. The log is shown in full, attribute values included, because those values are what you diagnose from when a rule produces an unexpected result.

To read a log line:

```
....Order[16] {Update - Adjusting order: amount_total} id: 16, customer_id: 19, amount_total:  [0.0-->] 90.0
```

- The leading dots are the depth in the cascade: Item (2 dots), its Order (4), its Customer (6).
- `Order[16]` is the row; `{...}` is the rule or action that ran; the rest is the row's attribute values at that step.
- `[0.0-->] 90.0` marks a value the rules changed, with its old and new value.
- The log is in phases: **ROW LOGIC** (derivations and constraints, as rows change), **COMMIT LOGIC** (checks that need the finished aggregates), and **AFTER_FLUSH LOGIC** (events that need database-assigned keys, such as the Kafka publish).

More: [Logic Log](https://apilogicserver.github.io/Docs/Logic-Debug/#logic-log).

</details>

&nbsp;

<!-- text: tests-howto -->
<details markdown>
<summary>{{howto_title}}</summary>

**1. Have AI create them.** This project's context tells your AI assistant how (`.github/copilot-instructions.md`, `docs/training/testing.md`). Just say:

```
create tests from rules
```

The assistant reads `database/models.py`, the logic files and the custom APIs, then writes `.feature` files and step implementations under `test/api_logic_server_behave/features/`. Then say `run the tests` and `run the requirements traceability report` and the assistant does both.

{{feature_prompt}}
**2. You can also define tests manually.** Add a `<name>.feature` file (Gherkin) under `test/api_logic_server_behave/features/` and its steps under `features/steps/`. The steps call the running API, so tests exercise the same rules as any client. See `docs/training/testing.md` for the patterns that keep tests repeatable.

**Or run them yourself** (server running, from `test/api_logic_server_behave`):

```
python behave_run.py --outfile=logs/behave.log
python requirements_traceability_report.py run
```

</details>

> ⚙ generated: used inside the fold above, where {{feature_prompt}} is (only when the project has requirements)

<!-- text: feature-prompt -->
Or, to have each requirement's tests linked in the Tests column above (it matches on `Feature:` name), say which names to use:

```
create tests from rules, one Feature per requirement, named exactly:
{{feature_names}}
```

_Tests with other names still run and appear below; they just aren't linked to a requirement._

> ⚙ generated: for each feature a "### Feature: <name>" heading; for each scenario a "#### Scenario: <name>" block with a fold for its rules and logic log

## Provenance

<!-- (no introduction by default; add one here) -->

> ⚙ generated: how this report was produced (date, generator and version, text source, last test run, project, requirement files)

<!-- text: provenance-note -->
_The report is derived from the project's files and the last test run; nothing in it is stored anywhere else, so regenerating it always reflects the project as it is now._
'''
""" the built-in text for each customizable section; the same text ships as reports/Requirements Traceability Report Template.md """


DEFAULT_TITLES = {"report": "Requirements Traceability Report", "cover": "Cover", "background": "Background",
                  "requirements": "Requirements Coverage", "data-model": "Data Model",
                  "security": "Security (RBAC)", "messages": "Messages and APIs", "tests": "Tests and Results"}
""" the heading that names each section in the template file (and shows in the report, unless renamed) """
DEFAULT_TITLES["contents"] = "Contents"
DEFAULT_TITLES["glance"] = "At a Glance"
DEFAULT_TITLES["provenance"] = "Provenance"
SUB_TITLES = {"coverage-summary": "Coverage summary", "traceability-matrix": "Traceability matrix",
              "rule-coverage": "Rule coverage by tests", "requirements-detail": "Requirements in detail",
              "not-traced": "Rules not traced to a requirement", "derived-columns": "Derived columns",
              "roles": "Roles and CRUD (DefaultRolePermission)", "grants": "Row-level grants (Grant)"}
""" the ### and #### headings that are the same in every report """
SECTION_KEYS = tuple(DEFAULT_TITLES)
_ALIASES = {"requirements traceability to rules": "requirements"}
""" older names for a section, still accepted as its heading """
_TEXT_MARK = re.compile(r'^\s*<!--\s*text:\s*([\w-]+)\s*-->\s*$')
_GENERATED_MARK = re.compile(r'^\s*(<!--\s*generated:.*-->|>\s*[▶⚙].*)\s*$')
_TITLE_OVERRIDE = re.compile(r'^\s*<!--\s*title:\s*(.+?)\s*-->\s*$')
_COMMENT_LINE = re.compile(r'^\s*<!--.*-->\s*$')
TEMPLATE_SOURCE = {"where": "built-in text", "sha": ""}
""" which text the report was written with: the built-in text, or a template file (and its hash) """
FACTS = {}
""" numbers sec_requirements works out, for the At a Glance scorecard """
TEXT = {}
""" the text in use, by section: the built-in DEFAULT_TEMPLATE, overridden section by section """
TITLES = {}
""" the title in use, by section """


def _section_key(heading: str):
    name = heading.strip().lower()
    if name in _ALIASES:
        return _ALIASES[name]
    return next((k for k, v in {**DEFAULT_TITLES, **SUB_TITLES}.items() if v.lower() == name and k != "report"), None)


def parse_template(text: str) -> tuple:
    """ ({name: [lines]}, {section: title}) from a template. '# Title' (with its subtitle) and '## Section'
        headings start sections; the text under a heading is that section's introduction. '<!-- text: name -->'
        starts a named block (text: intro = the section's introduction); '<!-- generated: ... -->' marks where
        generated content goes (ignored); '<!-- title: X -->' renames the section; other comments are dropped """
    out, titles, section, bucket, fence, unknown = {}, {}, None, None, False, []
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
        if not fence and re.match(r'^# \S', line):
            section = bucket = "report"
            out[bucket] = []
            titles[section] = line[2:].strip()
            continue
        if not fence and re.match(r'^#{2,4} \S', line):
            section = _section_key(line.lstrip('#'))
            bucket = section
            if section is None:
                unknown.append(line.lstrip('#').strip())
            else:
                out[bucket] = []
            continue
        if section is None:
            continue
        m = _TEXT_MARK.match(line)
        if m:
            bucket = section if m.group(1) == "intro" else m.group(1)
            out.setdefault(bucket, [])
            continue
        if _GENERATED_MARK.match(line):
            bucket = None
            continue
        m = _TITLE_OVERRIDE.match(line)
        if m:
            titles[section] = m.group(1)
        elif bucket is not None and not _COMMENT_LINE.match(line):
            out[bucket].append(line)
    for lines in out.values():
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
    if unknown:
        print(f"Note: heading(s) not recognised as sections, and ignored: {', '.join(unknown)} "
              f"(known: {', '.join(list(v for k, v in DEFAULT_TITLES.items() if k != 'report') + list(SUB_TITLES.values()))})")
    return out, titles


def load_template(template_path: str) -> None:
    """ built-in text, then the project's template file on top of it (section by section).
        An old-style Intro file (no section headings) supplies the cover only. """
    result, titles = parse_template(DEFAULT_TEMPLATE)
    titles = {k: v for k, v in titles.items()}
    path = Path(template_path)
    older = [path.with_name("Behave Logic Report Template.md"), path.with_name("Behave Logic Report Intro.md")]
    chosen = path if path.is_file() else next((p for p in older if p.is_file()), None)
    if chosen:
        src = chosen.read_text()
        if re.search(r'^## \S', src, re.M) or re.search(r'^# (?!Behave Logic Report|Requirements Traceability Report)\S', src, re.M):
            mine, mine_titles = parse_template(src)
            result.update(mine)
            titles.update(mine_titles)
        else:
            cover = []
            for each in src.splitlines():
                if '# Behave Logic Report' in each or '# Requirements Traceability Report' in each:
                    break
                cover.append(each)
            while cover and cover[-1].strip() in ("", "---"):
                cover.pop()
            result["cover"] = cover
    TEMPLATE_SOURCE["where"] = "built-in text"
    TEMPLATE_SOURCE["sha"] = ""
    if chosen:
        TEMPLATE_SOURCE["where"] = chosen.as_posix()
        TEMPLATE_SOURCE["sha"] = hashlib.sha256(chosen.read_bytes()).hexdigest()[:12]
    TEXT.clear()
    TEXT.update(result)
    TITLES.clear()
    TITLES.update(titles)


def title(key: str) -> str:
    """ the heading to show for a section """
    return TITLES.get(key) or DEFAULT_TITLES.get(key) or SUB_TITLES[key]


def fill(lines: list, **values) -> list:
    """ replace {{name}} in text lines; a line that is only {{name}} may be replaced by several lines (or none) """
    out = []
    for line in lines:
        m = re.fullmatch(r'\s*\{\{(\w+)\}\}\s*', line)
        if m and m.group(1) in values and isinstance(values[m.group(1)], list):
            out.extend(values[m.group(1)])
            continue
        for k, v in values.items():
            line = line.replace("{{" + k + "}}", str(v))
        out.append(line)
    return out


def text(key: str, **values) -> list:
    """ a section's introduction, followed by a blank line, or nothing if it is blank """
    lines = fill(TEXT.get(key, []), **values) if values else TEXT.get(key, [])
    return list(lines) + [""] if lines else []


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


def tests_howto(root: Path, has_tests: bool) -> list:
    """ hide/show block: how to create tests (AI or by hand) and run them """
    names = []
    for each in parse_requirements(root):
        if each["num"] is None or each["features"]:
            names.extend(sorted(each["features"]) or [each["title"]])
    title = "How to add more tests, and run them" if has_tests else "How to create tests, and run them"
    prompt = text("feature-prompt", feature_names=[f"- {n}" for n in names]) if names else []
    return fill(TEXT.get("tests-howto", []), howto_title=title, feature_prompt=prompt)


def _secs(seconds) -> str:
    """ 0.29 -> '0.29 s', 2.481 -> '2.5 s', 75 -> '1m 15s' """
    if seconds is None:
        return ""
    if seconds < 1:
        return f"{seconds:.2f} s"
    if seconds < 60:
        return f"{seconds:.1f} s"
    return f"{int(seconds // 60)}m {int(round(seconds % 60)):02d}s"


def run_seconds(behave_log: str):
    """ how long the last run took, from the 'Behave run time: N s' line behave_run.py writes into the log; None if absent """
    log = Path(behave_log)
    if not log.is_file():
        return None
    m = re.findall(r'Behave run time:\s*([\d.]+)\s*s', _read(log))
    return float(m[-1]) if m else None


def scenario_times(behave_log: str) -> dict:
    """ {'Feature / Scenario': seconds} from logs/scenario_times.json (written by features/environment.py), or {} """
    path = Path(behave_log).parent / "scenario_times.json"
    if not path.is_file():
        return {}
    try:
        import json
        return json.loads(_read(path))
    except ValueError:
        return {}


def _run_info(root: Path, behave_log: str):
    """ (when the tests last ran, how long ago as text, files changed since), or None if there is no run """
    log = Path(behave_log)
    if not log.is_file() or log.stat().st_size == 0:
        return None
    ran = datetime.datetime.fromtimestamp(log.stat().st_mtime)
    minutes = int((datetime.datetime.now() - ran).total_seconds() // 60)
    ago = f"{minutes // 60}h {minutes % 60}m" if minutes >= 60 else f"{minutes}m"
    watched = []
    for sub, pattern in (("logic", "*.py"), ("test/api_logic_server_behave/features", "*"),
                         ("integration", "*.py"), ("api", "*.py"), ("security", "*.py")):
        folder = root / sub
        if folder.is_dir():
            watched += [p for p in folder.rglob(pattern) if p.is_file() and "__pycache__" not in p.parts]
    newer = sorted({_rel(p, root) for p in watched if p.stat().st_mtime > log.stat().st_mtime})
    return ran, ago, newer


def _run_stamp(root: Path, behave_log: str) -> list:
    """ when the tests last ran, how far that is from this report, and whether the rules or tests
        changed after it (the evidence below is only as current as that run) """
    info = _run_info(root, behave_log)
    if info is None:
        return []
    ran, ago, newer = info
    took = run_seconds(behave_log)
    text = (f"**Last test run:** {ran.strftime('%B %d, %Y %H:%M')}" + (f", took {_secs(took)}" if took is not None else "")
            + f" ({ago} before this report; test results and logic logs below are from that run)")
    if newer:
        text += (f"  \n⚠ **{len(newer)} file(s) changed after that run** (e.g. `{newer[0]}`): "
                 f"re-run the tests before relying on the results.")
    return [text, ""]


def provenance(root: Path, behave_log: str) -> list:
    """ how this report was produced, so a reader can tell what it was built from and when """
    rows = [("Generated", datetime.datetime.now().strftime("%B %d, %Y %H:%M")),
            ("Generator", f"`requirements_traceability_report.py` {__version__}")]
    where = TEMPLATE_SOURCE["where"]
    rows.append(("Report text from", where + (f" (sha256 {TEMPLATE_SOURCE['sha']})" if TEMPLATE_SOURCE["sha"] else "")))
    info = _run_info(root, behave_log)
    rows.append(("Tests last ran", info[0].strftime("%B %d, %Y %H:%M") + (f"; {len(info[2])} file(s) changed since" if info[2] else "")
                 if info else "no test run found"))
    rows.append(("Project", root.name))
    try:
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5)
        if commit.returncode == 0:
            dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, timeout=5)
            rows.append(("Source commit", commit.stdout.strip() + (" (uncommitted changes)" if dirty.stdout.strip() else "")))
    except (OSError, subprocess.SubprocessError):
        pass
    created = re.search(r'\*\*Created:\*\*\s*(.+)', _read(root / "docs" / "requirements" / "project_creation_report.md"))
    if created:
        rows.append(("Project created", created.group(1).strip()))
    reqs = sorted((root / "docs" / "requirements").glob("*/requirements.md")) if (root / "docs" / "requirements").is_dir() else []
    if reqs:
        rows.append(("Requirement files read", "<br>".join(f"`{_rel(p, root)}` (sha256 {hashlib.sha256(p.read_bytes()).hexdigest()[:8]})" for p in reqs)))
    rows.append(("Regenerate", "`python requirements_traceability_report.py run`, from `test/api_logic_server_behave`"))
    return ["| | |", "|---|---|"] + [f"| {k} | {_cell(v) if k != 'Requirement files read' else v} |" for k, v in rows] + [""]


def scorecard(root: Path, msg_rows: list, behave_log: str) -> list:
    """ the verdict and a short table, from facts the report already worked out (nothing is judged here
        beyond coverage: this says what was traced and tested, not that the system is correct) """
    f = FACTS
    if not f:
        return []
    info = _run_info(root, behave_log)
    newer = info[2] if info else []
    n_tested = f["n_req"] - len(f["no_tests"])
    if f["failed"]:
        icon = "❌"
    elif f["n_req"] == 0 or f["passed"] is None or f["no_impl"] or f["no_tests"] or f["skipped"] or newer:
        icon = "⚠"
    else:
        icon = "✅"
    parts = [f"{f['n_req']} requirement(s)" + (", all implemented" if not f["no_impl"] and f["n_req"]
                                                else (f", {len(f['no_impl'])} not implemented" if f["no_impl"] else ""))]
    if f["n_req"]:
        parts.append(f"{n_tested} tested" + (f" (gap: {_gap_list(f['no_tests'])})" if f["no_tests"] else ""))
    if f["passed"] is None:
        parts.append("no test run found")
    else:
        parts.append(f"{f['passed']} of {f['passed'] + f['failed'] + f['skipped']} scenarios passed"
                     + (f", {f['failed']} FAILED" if f["failed"] else "")
                     + (f", {f['skipped']} skipped" + (f" (not verified: {_gap_list(f['skipped_reqs'])})" if f["skipped_reqs"] else "")
                        if f["skipped"] else ""))
        if info:
            parts.append(f"last run {info[1]} ago" + (", files changed since" if newer else ""))
    lines = [f"**{icon} {'; '.join(parts)}.**", "", "| | |", "|---|---|"]
    lines.append(f"| Requirements | {f['n_req']}" + (f" ({f['n_req'] - len(f['no_impl'])} implemented)" if f["n_req"] else "") + " |")
    if f["n_req"]:
        lines.append(f"| Tested | {n_tested} of {f['n_req']}" + (f" - gap: {_gap_list(f['no_tests'])}" if f["no_tests"] else "") + " |")
    if f["passed"] is None:
        lines.append("| Last test run | none found |")
    else:
        lines.append(f"| Last test run | {'❌' if f['failed'] else ('⚠' if f['skipped'] else '✅')} {f['passed']} passed, {f['failed']} failed"
                     + (f", {f['skipped']} skipped" if f["skipped"] else "")
                     + (f" ({info[0].strftime('%B %d, %Y %H:%M')}, {info[1]} ago)" if info else "")
                     + (f"; took {_secs(run_seconds(behave_log))}" if run_seconds(behave_log) is not None else "") + " |")
    lines.append(f"| Rules | {f['n_rules']} ({f['n_declarative']} declarative, {f['n_python']} Python functions, {f['n_events']} Python events) |")
    if f["seen"]:
        lines.append(f"| Rules shown running in a test log | {f['seen'][0]} of {f['seen'][1]} |")
    parsed = _parse_security(root)
    if parsed:
        lines.append(f"| Security | {'enabled' if _security_enabled(root) else 'not enabled'}; "
                     f"{len(parsed[0])} role(s), {len(parsed[1])} row-level grant(s) |")
    kafka_in = sum(1 for m in msg_rows if m["channel"] == "Kafka" and m["direction"] == "in")
    kafka_out = sum(1 for m in msg_rows if m["channel"] == "Kafka" and m["direction"] == "out")
    http = sum(1 for m in msg_rows if m["channel"] == "HTTP")
    if msg_rows:
        lines.append(f"| Messages and APIs | {kafka_in} Kafka topic(s) in, {kafka_out} out; {http} HTTP endpoint(s) |")
    if kafka_in or kafka_out:
        mode, server = kafka_delivery(root, _test_text(root))
        lines.append("| Kafka | " + (f"live ({server}): subscribe tested through the broker; outbound messages checked in the log"
                                      if mode == "live" else
                                      "mixed: some scenarios live, some simulated" if mode == "mixed" else
                                      "simulated, no broker: messages are tested through /consume_debug; live delivery not verified")
                     + " |")
    return lines + [""]


def main(behave_log: str, scenario_logs: str, wiki: str, prepend_wiki: str, project_dir: str = "../.."):
    """ main driver """
    root = Path(project_dir).resolve()
    wiki_path = Path(wiki).absolute()
    report_dir = wiki_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)

    load_template(prepend_wiki)
    rules = collect_rules(root)
    msg_rows = collect_messages(root, rules, report_dir)
    lines_requirements, req_by_file, features = sec_requirements(root, report_dir, rules, msg_rows,
                                                                 behave_log, scenario_logs)
    sections = [(title("requirements"), lines_requirements),
                (title("data-model"), sec_data_model(root, rules, report_dir)),
                (title("security"), sec_security(root)),
                (title("messages"), sec_messages(root, msg_rows, req_by_file, report_dir))]

    # test evidence
    evidence = [f"## {title('tests')}", ""]
    log_path = Path(behave_log)
    n_scenarios = sum(features.values())
    if n_scenarios == 0:
        evidence.append("**No tests defined yet.** Everything above is generated from the project's rules, "
                        "data model, security declarations and integration files, so it is complete "
                        "without a test run. Add tests, then regenerate this report to see each scenario "
                        "with the rules it exercised.")
        evidence.append("")
        evidence.extend(text("tests"))
        evidence.extend(tests_howto(root, has_tests=False))
    elif not log_path.is_file() or log_path.stat().st_size == 0:
        evidence.append(f"**{n_scenarios} scenario(s) defined, but no Behave run found** "
                        f"(`{behave_log}` is missing or empty). Run "
                        f"`python behave_run.py --outfile=logs/behave.log`, then regenerate this report.")
    else:
        outcome = scenario_results(behave_log) or {}
        passed = list(outcome.values()).count("passed")
        failed = list(outcome.values()).count("failed")
        skipped = list(outcome.values()).count("skipped")
        evidence.append(f"**{'❌' if failed else ('⚠' if skipped else '✅')} {n_scenarios} scenario(s): {passed} passed, "
                        f"{failed} failed" + (f", {skipped} skipped (not verified)" if skipped else "")
                        + (f"; took {_secs(run_seconds(behave_log))}" if run_seconds(behave_log) is not None else "")
                        + f"** (from the last run, `{behave_log}`).")
        evidence.append("")
        evidence.extend(text("tests"))
        evidence.extend(tests_howto(root, has_tests=True))
        evidence.extend(build_test_evidence(behave_log=behave_log, scenario_logs=scenario_logs))
    sections.append((title("tests"), evidence))
    sections.append((title("provenance"), [f"## {title('provenance')}", ""] + text("provenance")
                     + provenance(root, behave_log) + text("provenance-note")))

    # assemble
    out = [f"# {title('report')}", ""]
    if TEXT.get("report"):
        out += TEXT["report"] + [""]
    if TEXT.get("cover"):
        out += TEXT["cover"] + [""]
    out.append("")
    outcome = scenario_results(behave_log) or {}
    n_failed = list(outcome.values()).count("failed")
    out.append(f"**Project:** {root.name} &nbsp;|&nbsp; **Generated:** "
               f"{datetime.datetime.now().strftime('%B %d, %Y %H:%M')} &nbsp;|&nbsp; "
               f"**Rules:** {len(rules)} &nbsp;|&nbsp; **Test scenarios:** {n_scenarios or 'none defined'}"
               f" &nbsp;|&nbsp; **Generator:** requirements_traceability_report.py {__version__}")
    out.append("")
    out.extend(_run_stamp(root, behave_log))
    if n_failed:
        failing_names = [f"{name}" for (_, name), status in outcome.items() if status == "failed"]
        out.append("")
        out.append(f"### ❌ {n_failed} of {len(outcome)} test scenarios FAILED")
        out.append("")
        out.extend(f"- ❌ {name}" for name in failing_names)
        out.append("")
        out.append(f"See [{title('tests')}](#{_slug(title('tests'))}) for the failing step and the logic log.")
        out.append("")
    out.append(f"## {title('glance')}")
    out.append("")
    out.extend(text("glance"))
    out.extend(scorecard(root, msg_rows, behave_log))
    out.extend(text("scorecard-note"))
    summary = project_summary(root, report_dir)
    if summary:
        out.extend(summary)
        out.append("")
    background = TEXT.get("background")
    if background:
        if not any("<details" in line for line in background):   # text without its own fold: wrap it in one
            background = (["<details markdown>", f"<summary>{title('background')}: what this report is, and how to read it</summary>", ""]
                          + background + ["", "</details>"])
        out += background + [""]
    out.append(f"## {title('contents')}")
    out.append("")
    out.extend(text("contents"))
    for section_title, _ in sections:
        out.append(f"- [{section_title}](#{_slug(section_title)})")
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
    Create the Requirements Traceability Report: requirements, rules, data model, security and
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
              default=f'../../docs/requirements/Requirements Traceability Report.md',  # all links are computed relative to this folder
              help="Report to write")
@click.option('--template', '--prepend_wiki', 'prepend_wiki',
              default=f'reports/Requirements Traceability Report Template.md',
              help="Your text for the report's introductions (sections marked <!-- section: name -->)")
@click.option('--project_dir',
              default=f'../..',
              help="Project root (default: two levels up from test/api_logic_server_behave)")
def run(ctx, behave_log: str, scenario_logs: str, wiki: str, prepend_wiki: str, project_dir: str):
    ensure_working_directory()
    main(behave_log=behave_log, scenario_logs=scenario_logs, wiki=wiki,
         prepend_wiki=prepend_wiki, project_dir=project_dir)


if __name__ == '__main__':  # debugger & python command line start here
    print(f'\nRequirements Traceability Report {__version__}, started at {os.getcwd()}')
    commands = sys.argv
    if len(sys.argv) > 1:
        print_args(commands, f'\n\nCommand Line Arguments:')
    cli()
