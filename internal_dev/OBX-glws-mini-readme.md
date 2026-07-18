<!--
title: GLWS Quick Start (draft, mini) — PARKED, not active
Purpose: faster-start variant of README.md for business users — training first,
positioning compressed to 1-2 lines, dog-whistles the low-code-lock-in contrast
without naming/attacking low-code. See internal_dev/OBX.md for rationale.

STATUS (2026-07-17): Parked, not deleted. Decision: the full README.md is now the
single basis for GLWS going forward — both as the doc and as the shot list for the
planned GLWS announcement video (numbered "Example — Existing Database" sequence:
Declare it → Run it → Talk to your AI → Iterate → Why rules matter — maps directly
to video chapters via its <details> structure). Maintaining this mini variant
alongside the full README risked the same base-vs-basic_demo content drift already
seen elsewhere in this CE. The "impatient reader" need this file served is instead
met by the full README's own collapsible <details> sections — skim past what you
don't need yet, expand it later, no second document to keep in sync.

Originally lived at org_git/genai-logic-web-studio/readme-mini.md — moved here
next to OBX.md so it's found alongside the rationale, not out in the live repo
where it could be mistaken for current guidance.
-->

# GenAI-Logic Web Studio — Quick Start

No install — runs in your browser via GitHub Codespaces. (Use Chrome or Edge — Safari has known issues with VS Code in the browser.)

**How to think about this:** it's Python underneath — declared rules, not a proprietary scripting layer. If you ever need a developer to go further, they're working in a normal IDE with normal code, not reverse-engineering a black box.

&nbsp;

## Get Started

Say to your AI assistant:

```
Please load `.github/copilot-instructions.md`.
```

Then:

```
Create basic_demo from samples/dbs/basic_demo.sqlite (customers, orders, products).

On Placing Orders, Check Credit
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
```

Allow a few minutes. A browser tab may auto-open showing it running — safe to dismiss.

&nbsp;

## See It Work

Press F5 using "API Logic Server Run (run project from manager)", and open the Admin App.

Open an **unshipped** order for Alice, edit an item's quantity to something huge, and save.

It fails. That's the rule you just described in plain English — actually enforced, not a mockup.

&nbsp;

## This Is Real, Not a Demo

- The rule that just fired is plain Python, readable in `logic/logic_discovery/` — not a black box.
- Proof it's not just a toy: [declarative vs. procedural comparison](samples/basic_demo_sample/logic/procedural/declarative-vs-procedural-comparison.md) — same requirement, ~200 lines of hand-written code, 2 real bugs, vs. the 5 rules you just saw.

&nbsp;

## Built for the Enterprise

**The bottom line:** rules stay **readable** (5 lines, not 200), **trustworthy** (fire at every commit, from every caller — can't be forgotten or bypassed), and **maintainable** (add a rule anywhere, it finds its place automatically). You can read them, and trust they're enforced. Always.

**Security and integration aren't separate tools to learn:**
- RBAC — opt-in anytime: `genai-logic add-auth`.
- Messaging — describe it in plain English, same as any rule: *"When an Order's date_shipped is set, publish it to Kafka topic 'order_shipping'."* Partners subscribe the same way — see the [EAI example](samples/basic_demo_eai/readme.md).

**This scales past small demos.** A real logistics company's customs compliance system, built this way, caught an **8-figure compliance exposure** their prior hand-coded system had missed for months. A Canadian customs regulation (CBSA), cited directly, became a working duty-calculation system — no separate spec-to-code translation step. A multi-table cost allocation system across departments and GL accounts — cascading logic that defeats procedural code — had previously cost 4 Java developers 2 years without shipping; this version came from a single plain-English prompt. Once AI is unburdened from logic, it produces complete, governed, enterprise-class systems — not demos that become tech debt. [More examples →](README.md)

&nbsp;

## Ask Your AI

Once it's running, just ask — same AI, same context, nothing new to learn:

- "What else can you do?"
- "How does this work?"
- "Can I add a rule that customers with unpaid letters can't order?"

&nbsp;

## Go Deeper

Full walkthrough, governance reports, enterprise integration (EAI/MCP), and more examples: see [README.md](README.md).
