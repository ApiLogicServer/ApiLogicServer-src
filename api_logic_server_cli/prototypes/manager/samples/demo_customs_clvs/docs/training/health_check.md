---
title: Project Health Check — Vital Signs
version: 1.3 (May 2026)
usage: AI reads this when user asks for vital signs / health check
overhead: zero until invoked — file is read on demand only
governance: see docs/training/governance.md — thresholds, red flags, score ranges, manager roll-up
---

# Project Health Check — Vital Signs

Inspired by the Versata Automation Analyzer. Produces two scores plus red flag detection:
1. **Coverage Score** — rules per object, weighted by rule power
2. **Integrity Score** — demerits for anti-patterns, credits for reviews
3. **Red Flag check** — binary alert for governance-level issues (see governance.md)

Report all three, all findings with file:line, and offer to fix each one.

**Governance policy, score reference ranges, and manager roll-up guidance:**  
→ `docs/training/governance.md`

---

## ACTIVATION TRIGGERS

- "vital signs"
- "health check"
- "how's my project doing"
- "doc, how am I doing"
- "check my logic"
- Any similar phrase requesting project health or quality assessment

---

## MANDATORY SEQUENCE

```
STEP 1: Read ALL files in logic/logic_discovery/**/*.py
STEP 1b: Read logic/declare_logic.py — check for rules declared outside discovery (demerit if found)
STEP 2: Read database/models.py — count mapped table classes and tables with incoming FKs
STEP 3: Scan for @health-check annotations (reviewed files / suppressed lines / red-flag-suppress)
STEP 4: Compute Coverage Score
STEP 5: Compute Integrity Score
STEP 6: Check Red Flag (see below) — read docs/training/governance.md for full policy
STEP 7: Present report (format below)
STEP 8: Offer to fix each unreviewed finding
```

---

## Coverage Score

**Purpose:** Are the tables in this project adequately governed by rules?
Normalizes for project size. A 3-table project with 3 rules is not healthier
than a 10-table project with 3 rules.

### Step 1 — Count weighted rules

| Rule type | Weight | Rationale |
|---|---|---|
| `Rule.sum` | 3 | Replaces multi-path aggregate + all downstream cascades |
| `Rule.count` | 3 | Same — existence checks, cardinality constraints |
| `Rule.formula` | 2 | Replaces derivation on every change path |
| `Rule.copy` | 2 | Replaces copy + cascade on parent change |
| `Rule.constraint` | 1 | Replaces one guard; trivial to write procedurally |
| `Rule.after_flush_row_event` | 0 | Hook, not a replacement for procedural code |

### Step 2 — Count mapped tables

Count SQLAlchemy model classes in `database/models.py` that are mapped to real
domain tables (exclude `SysConfig`, auth tables, and any class beginning with `Sys`).

**Exclude lookup tables:** tables with ≤ 2 non-PK columns are narrow reference or junction
tables (e.g. Region, Territory, Shipper, Union) that rarely have rules and would dilute
the score. Exclude them from the denominator and list them as `excluded (lookup)` in the
Coverage Detail section.

This threshold is intentionally conservative — a 3-column table (e.g. Department with
name + budget) may legitimately have rules and stays in the count.

### Step 3 — Compute

```
weighted_rules = (sum_count × 3) + (formula_copy × 2) + (constraint × 1)
coverage_score = weighted_rules / table_count
```

### Reference ranges

| Score | Grade | Meaning |
|---|---|---|
| ≥ 4.0 | ✅ Strong | Well-governed; meaningful rules on most objects |
| 2.0–3.9 | 🟡 Moderate | Some tables likely ungoverned; review coverage |
| 1.0–1.9 | 🟠 Thin | Mostly constraints only, or low rule density |
| < 1.0 | 🔴 Weak | Project is largely procedural; rules barely present |

`demo_customs_cbsa` reference: `(3×3 + 6×2 + 8×2 + 2×1) / 5 = 39/5 = 7.8` — Strong.

---

## Integrity Score

**Purpose:** Are there bugs, anti-patterns, or events that should have been rules?
Starts at 100. Demerits subtract; reviewed annotations restore credit.

### Demerits

#### -3: Raw query replacing a rule
`session.query()` **inside a formula function** to compute a derived value.
This silently goes stale when child rows change — exactly what `Rule.sum` / `Rule.count` exists to prevent.

Detection: `session.query(` inside a `def` function that is wired to a `Rule.formula` or `Rule.early_row_event` that assigns to a model attribute.

#### -3: Aggregate replacing a rule
`len(...)`, `sum(...)`, or any list comprehension over child rows inside a formula.
Same failure mode as raw query.

#### -2: Event that should be a rule
An event handler function whose body:
- Assigns a computed value to `row.attr` → should be `Rule.formula`
- Sums or counts child rows and assigns to `row.attr` → should be `Rule.sum` / `Rule.count`
- Copies a parent attribute to `row.attr` → should be `Rule.copy`
- Checks a condition and raises an exception → should be `Rule.constraint`

Detection heuristic: event body has `row.<attr> =` assignment AND no external I/O (no Kafka, no HTTP, no session.query for lookup).

#### -2: Broken dependency tracking
- `as_expression=lambda row: my_func(row)` — wraps a function; LB sees no `row.attr` refs
- `calling=` function body has no direct `row.attr` refs (all hidden in a helper)
- Side-effect assignment inside a formula: `row.other_col = ...` inside a `calling=` function

#### -1: Raw query in row_event (non-lookup)
`session.query()` inside a row_event that computes an aggregate or iterates over
multiple rows. A single `.filter_by()` returning one parent object is a lookup —
see Hall Passes below.

#### -1: Docstring hygiene violation
Docstring contains implementation notes, field mappings, or AI paraphrase beyond
the verbatim requirement text. (See Docstring Hygiene section.)

#### -1: Missing docstring on calling= function
A function wired via `calling=` has no docstring (or an empty one).
The first docstring line appears in logic flow diagrams and reports — without it,
the diagram shows only the function name with no indication of what it derives.

Detection: find all `Rule.formula(... calling=<func>)` and `Rule.early_row_event(... calling=<func>)`,
then check each `<func>` for a non-empty one-line docstring.

Fix: add `"""Derive <column>: <brief description>."""` as the first line of each function.

Example fix:
```python
# Before (flagged):
def _clvs_eligible(row, old_row, logic_row):
    if row.service_type_cd != CLVS_SERVICE_TYPE:
        return 0

# After (clean):
def _clvs_eligible(row, old_row, logic_row):
    """Derive clvs_eligible: 1 if shipment meets all CLVS criteria, else 0."""
    if row.service_type_cd != CLVS_SERVICE_TYPE:
        return 0
```

#### -2: Logic in `declare_logic.py` instead of discovery files
Rules declared directly in `logic/declare_logic.py` rather than in `logic/logic_discovery/` files.
Discovery files provide requirements traceability (use-case name → file → rules → logic report)
and are the current standard. `declare_logic.py` predates the discovery pattern — migrating is
the correct fix.

Detection: `Rule.` declarations present in `logic/declare_logic.py` (beyond the template stub).

#### -1: Missing `__init__.py` in logic subdirectory

### Hall Passes (no demerit)

These patterns are legitimately procedural. If the code fits the skeleton, exempt it.

| Pattern name | Detection |
|---|---|
| `kafka-publish` | Function body calls `kafka_producer.send_row_to_kafka` or `send_kafka_message` |
| `eai-consumer-bridge` | Function body checks `is_processed` guard then publishes to a topic |
| `ai-handler` | Function body imports/calls OpenAI, Anthropic, or similar LLM client |
| `allocate-recipients` | Function returns a list, wired as `recipients=` in an `Allocate()` call |
| `row-lookup` | Single `session.query(...).filter_by(...).first()` or `.one_or_none()` — no iteration, no aggregate |

If code is procedural but does **not** fit any pattern above → apply the appropriate demerit.

### @health-check Annotations (review sign-off)

#### File-level — in the file docstring:
```python
"""
... requirement text ...

@health-check: reviewed 2026-05-10, approved
Pattern: ai-handler
Reviewer: val
"""
```
- Suppresses **all** demerits for this file
- `Pattern:` must name a known hall-pass pattern (see above) — generic "approved" without a pattern name is logged but does not suppress demerits
- `Reviewer:` provides accountability trail
- Score: restore the demerits that would have applied (+3/+2/+1 as appropriate)
- Report as: `✅ reviewed 2026-05-10 by val (ai-handler)`

#### Line-level — inline comment:
```python
result = session.query(CcpCustomer).filter_by(...)  # @health-check: suppress — deliberate lookup
```
- Suppresses demerit for that specific line only
- Should include a brief reason
- Score: restore the demerit for that line only

#### Stale review detection:
If a file has `@health-check: reviewed <date>` but the file's logic functions were
modified after that date (check file modification time if available, otherwise note
as "unable to verify staleness"), flag as:
`🟡 Review may be stale — file modified after review date`

#### Escape hatch abuse detection:
If more than 30% of demerits in a project are suppressed by `@health-check` annotations
without a `Pattern:` name, flag as:
`🟡 High suppression rate without pattern names — review annotations`

### Integrity Score Calculation

```
raw_score = 100 - sum(all demerits) + sum(restored credits from @health-check)
integrity_score = max(0, raw_score)
```

---

## Docstring Hygiene

For each logic file, check whether the docstring contains **only** requirement text.

Flag (-1 each):
- Implementation notes ("Uses early_row_event", "on every insert")
- Field mappings with hardcoded values ("service_type_cd = '04'")
- Numbered eligibility conditions beyond what the requirement states
- AI paraphrase or restatement in own words

**Why it matters:** anything added becomes a spec the AI codes to on the next iteration.
Wrong additions drive wrong rules.

---

## Red Flag Check

After computing scores, check this binary condition:

**Condition:** `tables_with_incoming_fks >= 10 AND rule_sum_count == 0`

- Count tables that have at least one other table's FK pointing at them
- Count total `Rule.sum` + `Rule.count` declarations across ALL logic files
- If both conditions met AND no `@health-check: red-flag-suppress` annotation found → raise the flag

**Suppress:** Check `logic/logic_discovery/use_case.py` and `logic/declare_logic.py` docstrings for:
```
@health-check: red-flag-suppress
Reason: <text>
Reviewer: <name>
Date: <YYYY-MM-DD>
```
If found with a non-empty `Reason:` → suppress flag, report as `✅ acknowledged <date> by <reviewer>: <reason>`  
If found without `Reason:` → ignore annotation, flag remains

**Report as:**
```
🚨 RED FLAG: 12 tables with child relationships, zero aggregation rules.
   Suggestion: schedule rules training or consulting engagement.
   To acknowledge: add @health-check: red-flag-suppress to use_case.py docstring.
```
or if suppressed:
```
✅ Red flag acknowledged 2026-05-10 by val: schema locked — aggregations in stored procedures
```

See `docs/training/governance.md` for full policy, thresholds, and manager roll-up guidance.

---

## Report Format

```
## 🩺 Project Governance Report

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| <project_name> | 5 | 29 | **5.8** | **94** | — | 🟡 Strong coverage, 2 findings |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.  
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.  
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.  
> See `docs/training/governance.md` for full scoring guide.

**Coverage Score: 5.8**  (29 weighted rules / 5 tables)   ✅ Strong
**Integrity Score: 94**  (2 demerits, 0 reviewed)
**Red Flag: none**  (3 aggregation rules, 5 FK tables)

────────────────────────────────────────
COVERAGE DETAIL
  Tables: CustomsEntry (5), SurtaxLineItem (4), HsCodeRate (0), ...
  Rules:  3× sum, 8× formula, 6× copy, 2× constraint

INTEGRITY FINDINGS
  🔴 -3  logic/logic_discovery/clvs_eligibility.py:41
         broken dependency: calling=_clvs_eligible delegates all row.attr refs to helper
         → Fix: reference row.attr directly in _clvs_eligible body

  🟡 -1  logic/logic_discovery/validation.py:8
         docstring contains implementation note: "Uses early_row_event"
         → Fix: replace with verbatim requirement text only

  ✅  +0  logic/logic_discovery/shipment_matching.py
         @health-check reviewed 2026-05-10 by val (row-lookup)

────────────────────────────────────────
2 findings need attention. Want me to fix them?
```

---

## Fix Protocol

For each finding, when user says "fix it" or "fix them all":

| Finding | Fix |
|---|---|
| session.query() inside formula | Replace with `Rule.count` + `Rule.formula`; add column to models.py |
| Aggregate (len/sum) inside formula | Same as above |
| Event that should be a rule | Replace event body with appropriate Rule declaration |
| as_expression= wrapping function | Rewrite as `calling=` with direct `row.attr` refs in function body |
| Side-effect formula | Split into one `Rule.formula` per derived column |
| Missing __init__.py | Create empty file |
| Docstring with implementation notes | Replace with verbatim requirement text only |

Always show before/after and explain *why* the original was wrong.

---

## Appendix: Scoring Guide

### Why Two Scores?

**Coverage Score** answers: *Is this project well-governed by rules?*
It rewards the high-value rules (sum, count) that replace the most code and catch the most bugs.
A constraint is worth 1 point; a sum is worth 3 — because a sum rule replaces derivation,
propagation, and cascade on every write path. At Versata, projects with high rule density
had dramatically fewer production bugs and faster change velocity.

**Integrity Score** answers: *Is the rule code correct and well-maintained?*
It penalizes patterns that look like rules but silently don't work (broken dependency tracking),
code that should have been a rule but wasn't (events with row assignments), and hygiene issues
that cause AI to generate wrong rules on the next iteration.

### Why Hall Passes?

Not all procedural code is a failure to use rules. AI handlers, Kafka bridges, and Allocate
recipients functions are legitimately imperative — the rules engine cannot replace them.
Penalizing them would make projects with AI-powered logic look worse than simpler projects,
which is the wrong incentive.

The hall pass system makes the exemption explicit and auditable: the code is procedural
*by design*, not by oversight.

### Why @health-check Annotations?

At scale, the same procedural pattern appears repeatedly across teams. Without a review
sign-off mechanism, the health check would flag the same known-good pattern every run,
creating noise that causes developers to ignore the report entirely.

The annotation creates a *permanent record* that a human reviewed the code, understood why
it was procedural, and approved it. The `Pattern:` field prevents blanket suppression —
you must name the known pattern, not just wave it through.

The Reviewer field enables governance: a project manager can see not just the score, but
*who* approved each exemption and *when*. Stale reviews (file modified after review date)
surface automatically.

### Reference Scores

| Coverage | Integrity | Profile |
|---|---|---|
| ≥ 4.0 | ≥ 95 | ✅ Production-ready, well-governed |
| ≥ 4.0 | 80–94 | 🟡 Strong coverage, some bugs to fix |
| 2.0–3.9 | ≥ 95 | 🟡 Clean but thin — add rules to ungoverned tables |
| 2.0–3.9 | 80–94 | 🟠 Both dimensions need attention |
| < 2.0 | any | 🔴 Under-governed — significant rule adoption needed |
| any | < 80 | 🔴 Integrity issues — bugs likely in production |

### What the Scores Mean to a Project Manager

A **Coverage Score < 2.0** means the team is writing procedural code where rules belong.
This is the modern equivalent of the Versata anti-pattern: events instead of rules.
At Versata scale, low-coverage projects had 3–5× more production bugs in business logic
and took 2–3× longer to implement changes. The rules engine enforces correctness on all
change paths; procedural code does not.

An **Integrity Score < 80** means there are likely silent bugs — rules that appear to work
on insert but silently go stale when child rows change, or rules that never re-fire because
of broken dependency tracking. These are the hardest bugs to find in production because
they don't throw exceptions; they just return wrong answers.

**Trend matters more than absolute score.** A project at 85/3.5 trending up is healthier
than one at 90/4.0 trending down. Ask for health checks after each significant feature
addition, not just at release time.
