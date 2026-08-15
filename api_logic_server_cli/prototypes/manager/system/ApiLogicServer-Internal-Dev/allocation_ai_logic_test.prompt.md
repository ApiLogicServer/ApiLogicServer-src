# Allocation AI Logic Test — Prompt

Used by `Config.do_ai_generated_logic_test` (tests/build_and_test/build_load_and_test.py) —
NOT a user-facing sample prompt. Isolates the cascade-Allocate portion of
samples/prompts/allocation.prompt.md so the AI writes `charge_distribution.py` against a
known-good, already-created schema (project_id, constraints, and rollup rules already
exist in the project — write only the cascade allocation).

---

When a Charge is inserted against a Project:

Level 1 — allocate the Charge amount to each Department per that Department's
Project Funding Line percent → creates ChargeDeptAllocation rows.

Level 2 — allocate each ChargeDeptAllocation amount to that Department's
GL Accounts per their Dept Charge Definition Line percents → creates
ChargeGlAllocation rows.

Freeze the percent used at each level onto the allocation row at charge time
(not live-recalculated if the definition later changes).
