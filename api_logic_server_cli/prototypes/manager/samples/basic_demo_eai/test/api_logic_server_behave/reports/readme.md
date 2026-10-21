# reports/

The **Requirements Traceability Report** is written here by `../requirements_traceability_report.py`
(`behave_logic_report.py` is the old name and still works).

| File | What it is |
|---|---|
| `Requirements Traceability Report.md` | The report. Generated: don't edit it, regenerate it. |
| `Requirements Traceability Report Template.md` | The report's text, laid out in the report's own order. This is the file you edit. |
| `db_diagram.generated.*` | The data model diagram, drawn from `docs/db.dbml` (needs Graphviz). |
| `Behave Logic Report Sample.md` | An example of the older report format. |

## Make the report

Say to your AI assistant `run the requirements traceability report`, or, from `test/api_logic_server_behave`:

```
python behave_run.py --outfile=logs/behave.log        # optional: run the tests first (server running)
python requirements_traceability_report.py run
```

It works with no tests: the requirements, rules, data model, security and messages sections are read from the
project's files, and the test results and logic logs appear once the tests have run.

## Where the report's text comes from

The generator has the standard text built in. It uses, in this order:

1. the section or block in **this project's** `Requirements Traceability Report Template.md`, if it has one;
2. otherwise the built-in text.

This works section by section, so a template can hold just the parts you changed. Anything it leaves out keeps
the built-in text, and picks up improvements when the generator is upgraded. (An older `Behave Logic Report
Template.md` or `Behave Logic Report Intro.md`, if that is what the project has, is still read.)

The report's last section, **Provenance**, says which text the report used, with a hash.

### One template for every project in your organization

A new project starts with the standard template file. To give every project your organization's wording
(or your own legal, governance or branding text), put your version of that file in a template project and have
`genai-logic create` overlay it:

```
genai-logic create --project_name=my_project --db_url=... --from_git=<git url or directory>
```

You don't have to remember the flag: put the same value in the Manager's `system/config/default_from_git.txt`
(first non-comment line; a git URL, or a directory relative to the Manager) and every `create` uses it.
`--from_git=none` skips the template for one project. If the default can't be used, `create` stops and tells you,
and it never silently makes a project without your template. The template is copied when the project is created,
so changing it later does not change existing projects: copy the file into them.

## The template file

Read it top to bottom against the report: the headings and order are the report's.

- **Headings** (`#`, `##`, `###`, `####`) name the sections. The text under a heading is that section's introduction.
  The first heading (`#`) is the report's title; the text under it is the subtitle.
- **`<!-- text: name -->`** starts a named block of text, such as `coverage-note` or `tests-howto`.
  `<!-- text: intro -->` is the introduction of the section it appears in.
- **`> ⚙ generated: ...`** lines show where generated content (tables, counts, logs) goes. They are fixed.
  Only prose is customizable: the scorecard, tables, counts, dates and logs are always generated.
- **`<!-- title: New Name -->`** under a heading renames that section in the report (and in the Contents).
- **`{{name}}`** is filled in by the generator (for example the feature names in the "create tests" prompt).
- A block or section left out keeps the built-in text; one left empty shows nothing.
- A heading that is not one of the report's sections is ignored, and the generator prints a note listing the valid ones.

Text can use folds (`<details markdown>`). The report keeps a one-line cue next to each claim that needs one, with
the longer explanation in a fold. Folds do not print or export to PDF in some viewers: expand them first.

## Options

```
python requirements_traceability_report.py run --help
  --template   the template file     (default: reports/Requirements Traceability Report Template.md)
  --wiki       the report to write   (default: reports/Requirements Traceability Report.md)
  --behave_log the Behave run log    (default: logs/behave.log)
```
