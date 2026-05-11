---
title: GenAI-Logic Project Governance Policy
version: 1.0 (May 2026)
audience: Project managers, team leads, consulting staff
related: docs/training/health_check.md — AI health check instructions
---

# GenAI-Logic Project Governance Policy

This document defines the governance thresholds, red flags, and acknowledgement
protocol for GenAI-Logic projects. It is the human-facing complement to
`health_check.md` (which instructs the AI how to compute scores).

Use this document to:
- Understand what scores mean and when to act
- Acknowledge known exceptions so they don't appear as unresolved flags
- Brief W-level reviewers on what to look for across a portfolio of projects

---

## Sample Project Governance Report Policy

The Manager workspace includes pre-built sample projects (under `samples/`) that
serve as reference implementations and demonstrations. Health check reports for
these samples follow a specific policy:

**Samples are authentic system outputs — findings are reported, not fixed.**

- `samples/portfolio_governance_report.md` — cross-project summary, run against all samples
- `samples/nw_sample/nw_sample_governance_report.md` — per-project report (with rules)
- `samples/nw_sample_nocust/nw_sample_nocust_governance_report.md` — per-project report (baseline)

These reports show what the health check finds on real generated projects, including
genuine findings. They are illustrative artifacts — the point is to demonstrate the
health check in action, not to show a perfect score.

**Do NOT fix sample logic files to improve their health check scores.** If the
health check finds a real issue in a sample (missing `__init__.py`, rules in
`declare_logic.py`, broken dependency tracking), that finding should appear in the
report. It is honest evidence of what the system generates and what the health check
catches. Fixing the issue silently undermines both the sample's authenticity and the
health check's credibility.

**To update a sample:** rebuild it from source (`genai-logic create` or
`rebuild-from-database`), verify it runs correctly, then store the rebuilt version.
The health check reports are then regenerated against the new version.

**The nw_sample reports live in prototype overlays** (`prototypes/nw/` and
`prototypes/nw_no_cust/`) so they survive BLT regeneration. Do not hand-edit them
in the BLT workspace — changes will be lost on next BLT run.

---

## 🚨 Red Flags

Red flags are binary alerts — not scores. They signal a project that may need
immediate attention: training, consulting, or architectural review.

### Red Flag 1: No Aggregation Rules on a Large Schema

**Condition:**  
> Project has **≥ 10 tables with incoming foreign keys** AND **zero `Rule.sum` + zero `Rule.count`** declarations anywhere in the project.

**Why it matters:**  
Sums and counts are the highest-value rule types — they replace multi-path
aggregate maintenance that is otherwise written procedurally and goes stale
on child changes. A project with 10+ tables and no aggregation rules has almost
certainly written those derivations procedurally (session.query, list comprehensions)
or not at all.

This is the primary governance signal. It does not mean the project is broken —
it means the team has not yet reached for the most powerful part of the engine.

**What to do:**  
- Schedule a 1-hour rules walkthrough with the team
- Show Rule.sum on the most obvious parent-child relationship
- Watch the logic report — the "aha moment" is immediate

**Manager view:** Appears in health check report as:
```
🚨 RED FLAG: 12 tables with child relationships, zero aggregation rules.
   Suggestion: schedule rules training or consulting engagement.
```

---

## Acknowledgement Protocol

When a red flag or demerit applies but is intentional or unavoidable, the
project can formally acknowledge it. This suppresses the flag in future health
checks while preserving the audit trail for governance review.

### Project-Level Acknowledgement

Place in the docstring of `logic/logic_discovery/use_case.py` (preferred)
or `logic/declare_logic.py`:

```python
"""
@health-check: red-flag-suppress
Reason: <required — explain why the flag does not apply>
Reviewer: <name>
Date: <YYYY-MM-DD>
"""
```

**`Reason:` is required.** Common valid reasons:
- "Schema locked — aggregations implemented in stored procedures outside ALS"
- "Read-only reporting project — no write paths, rules not applicable"
- "Legacy integration — child tables owned by external system, no local writes"
- "Proof-of-concept — rules to be added before production"

**Invalid reasons** (flag will not be suppressed):
- "Not needed" — not an explanation
- Omitting Reason entirely — annotation ignored, flag remains

### File-Level Demerit Suppression

For specific demerits (not red flags), place inline in the file docstring:

```python
"""
... requirement text ...

@health-check: reviewed 2026-05-10, approved
Pattern: ai-handler
Reviewer: val
"""
```

`Pattern:` must name a known hall-pass pattern from `health_check.md`:
`kafka-publish`, `eai-consumer-bridge`, `ai-handler`, `allocate-recipients`, `row-lookup`

### Line-Level Suppression

For a specific line:

```python
result = session.query(CcpCustomer).filter_by(...)  # @health-check: suppress — deliberate lookup
```

---

## Score Reference Ranges

### Coverage Score (weighted rules / domain tables)

| Score | Grade | Meaning | Action |
|---|---|---|---|
| ≥ 4.0 | ✅ Strong | Well-governed; meaningful rules on most objects | None |
| 2.0–3.9 | 🟡 Moderate | Some tables likely ungoverned | Review coverage gaps |
| 1.0–1.9 | 🟠 Thin | Mostly constraints; low rule density | Rules training recommended |
| < 1.0 | 🔴 Weak | Project largely procedural | Consulting engagement |

### Integrity Score (100 - demerits)

| Score | Grade | Meaning | Action |
|---|---|---|---|
| ≥ 95 | ✅ Good | Clean; minor advisories only | None |
| 85–94 | 🟡 Fair | Some findings to address | Developer remediation |
| 75–84 | 🟠 Poor | Likely bugs in production logic | Code review required |
| < 75 | 🔴 Critical | Significant integrity issues | Immediate remediation |

### Combined Profile

| Coverage | Integrity | Profile | Action |
|---|---|---|---|
| ≥ 4.0 | ≥ 95 | ✅ Production-ready | None |
| ≥ 4.0 | 85–94 | 🟡 Strong coverage, fix bugs | Developer remediation |
| 2.0–3.9 | ≥ 95 | 🟡 Clean but thin | Add rules to ungoverned tables |
| 2.0–3.9 | 85–94 | 🟠 Both need attention | Training + remediation |
| < 2.0 | any | 🔴 Under-governed | Training/consulting |
| any | < 75 | 🔴 Integrity critical | Immediate code review |

---

## Manager Roll-Up View

When reviewing a portfolio of projects, ask for:

```
"vital signs across all projects"
```

The AI will score each project and produce a summary table. Look for:

1. **🚨 Red flags first** — any project triggering the aggregation red flag
2. **Integrity < 85** — likely production bugs; escalate to code review
3. **Coverage trend** — is it going up or down between health checks?
4. **Unacknowledged findings > 30 days old** — stale issues signal a team not acting on feedback

### The Versata Baseline

At Versata, across tens to hundreds of thousands of lines of generated code:
- High-automation projects: **98%** declarative
- Low-automation projects: **94%** declarative
- The gap — 4 percentage points — represented thousands of lines of procedural
  code that bypassed the rules engine, with corresponding maintenance costs and
  production bugs

GenAI-Logic projects are smaller in absolute terms, but the principle holds:
the teams that fully adopt rules ship faster and have fewer logic bugs. The
governance metrics exist to make that adoption visible and measurable.

---

## Portfolio View — Rule Adoption Incentives

For organizations running multiple GenAI-Logic projects, the health check scores
provide a natural basis for tracking and incentivizing rule adoption across teams.

### The Leaderboard

Ask the AI to run `vital signs` across all projects in the workspace and produce
a ranked summary:

```
"vital signs across all projects — rank by coverage score"
```

Example output:

| Rank | Project | Team | Coverage | Integrity | Red Flag |
|---|---|---|---|---|---|
| 1 | customs_cbsa | Team A | 5.8 | 100 | — |
| 2 | allocate_demo | Team B | 2.5 | 97 | — |
| 3 | order_system | Team C | 1.7 | 94 | — |
| 4 | invoice_mgmt | Team D | 0.8 | 91 | — |
| 5 | legacy_port | Team E | 0.1 | 88 | 🚨 |

This is the modern equivalent of the Versata Automation Analyzer — visible,
objective, and comparable across teams without reading a single line of code.

### Why Gamification Works Here

**The score is actionable in an afternoon.** A team at Coverage 1.0 can add two
`Rule.sum` declarations and watch the score jump immediately. The feedback loop
is minutes, not sprint cycles. That immediacy makes improvement feel rewarding
rather than burdensome.

**The red flag is the entry point.** No team wants to be the only 🚨 on the
leaderboard. They fix it fast — and in fixing it, they discover the score is
still low compared to the top team. Curiosity takes over. You never had to
sell rules; the score sells them.

**The fix is always visible.** Coverage 1.0 → 2.0 means "add Rule.sum/count
to the tables that don't have them." The AI can identify exactly which tables
are ungoverned and suggest the rules. There is no ambiguity about what to do.

**Peer learning replaces mandates.** "How did Team A get to 5.8?" is a much
better conversation than "you must use more rules." The top team becomes the
model; the bottom team asks for help. Management facilitates rather than
enforces.

### The `@health-check` Accountability Layer

The suppress annotation cuts both ways. A team that suppresses a red flag
must put their name and reason on it — visible in the portfolio view:

```
| legacy_port | Team E | 0.1 | 88 | ✅ acknowledged 2026-05-10 by sarah |
|             |        |     |    | Reason: schema locked — stored procs |
```

Suppressing with a legitimate reason is fine. Suppressing to avoid being last
on the leaderboard is visible to W. The accountability trail is the governance.

### Trend Tracking

Run health checks periodically (after each significant feature release) and
track direction:

| Project | Mar | Apr | May | Trend |
|---|---|---|---|---|
| customs_cbsa | 4.2 | 5.1 | 5.8 | ✅ improving |
| order_system | 2.1 | 1.9 | 1.7 | ⚠️ regressing |
| legacy_port | 0.1 | 0.1 | 0.1 | 🔴 stalled |

A regressing score is the most actionable signal — it means new code is being
written procedurally. Caught after one sprint it's a conversation. Caught after
six months it's a rewrite.

### The Versata Baseline as a Target

At Versata, across Fortune 500 deployments with tens to hundreds of thousands
of lines of generated code, the measured range was **94–98% declarative**.
That is not a local preference — it is an industry-proven baseline from
thousands of production systems over 20+ years.

For GenAI-Logic, the equivalent target is **Coverage ≥ 3.0** for a mature
production project. Below 2.0 is worth a conversation. Below 1.0 is a
consulting engagement. The numbers give W something concrete to point to
that is not opinion.

---

## Demerit Quick Reference

| Demerit | Points | Category |
|---|---|---|
| `session.query()` inside formula (not event) | -3 | Bug |
| `len()`/`sum()` over child rows in formula | -3 | Bug |
| `as_expression=lambda row: my_func(row)` | -2 | Bug |
| Event assigns `row.attr =` with no I/O (should be Rule) | -2 | Bug |
| `calling=` hides all `row.attr` refs in helper | -2 | Bug |
| Side-effect `row.other =` inside formula | -2 | Bug |
| Rules in `declare_logic.py` instead of discovery files | -2 | Organization |
| `session.query()` iterating in row_event | -1 | Advisory |
| Docstring hygiene violation | -1 | Advisory |
| Missing `__init__.py` in logic subdirectory | -1 | Advisory |
| Wildcard import `from database.models import *` | -1 | Advisory |
