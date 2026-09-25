# Agentic Engineering — where GenAI-Logic fits

Source: Wynford Rees (FedEx), prepping a questionnaire for the Sept 29 2026 Town Hall on
Context Engineering adoption. He asked Gemini to explain the difference between VIBE
Development, Context Engineering, and Agentic Engineering — the transcript below is his,
verbatim, followed by where GenAI-Logic actually sits.

---

## TL;DR

Gemini's three-way split assumes each product picks one point on the autonomy axis.
GenAI-Logic uses AI at two different moments — they land in two different columns:

- **Authoring time — Context Engineering.** Curates how to build a governed system (which
  rule type fits, how to resolve schema ambiguity). Output: **declarative rules**.
- **Runtime — bounded Agentic Engineering.** An AI Rule makes a real LLM call *during* a
  transaction (e.g. picking the optimal supplier under disrupted shipping lanes) — genuine
  autonomy, not a lookup. But the deterministic rules around it still govern whatever the
  AI returns, with a full audit trail.

So it's Context Engineering *and* bounded Agentic Engineering, not one or the other. The
agentic part stays narrow on purpose — one judgment call inside a rule chain, not an
open-ended tool-calling loop — which is exactly the discipline Gemini's own "Over-Agenting"
warning calls for.

Wynford's questionnaire is good as written. One addition worth making: a Context
Engineering *product* should be evaluable by what it outputs — auditable rules, audit
logs, ad-libs — not just claimed as a methodology.

---

## Wynford's questionnaire draft (for Town Hall)

> FedEx currently support VIBE Development ("Vague Improvisational Behavioral Evaluation"
> with GitHub Copilot where you write a prompt, paste in some text, hit run and visually
> inspect the output, If it looks okay, you ship it). Context Engineering (like
> Retrieval-Augmented Generation/RAG) Development recognizes that the quality of the LLM's
> output is directly proportional to the quality and relevance of the context it is
> provided. Instead of asking the LLM to know everything, the architecture programmatically
> curate AI's working memory to achieve highly accurate, grounded, and safe results in a
> "single turn inference" by removing ambiguity from the prompt.
>
> Is Context Engineering Development currently supported or does FedEx have plans to
> support Context Engineering Development. Is there an evaluation process in place or a way
> to submit a request for evaluating a Context Engineering Development product that has
> Context Engineering as it's core methodology for application development purposes.

## Gemini's explainer (Wynford's prompt: "Can you explain the difference between Context
Engineering and Agentic Engineering? How are they different than VIBE development")

VIBE Development, Context Engineering, and Agentic Engineering — a progression from informal
experimentation to structured, programmatic system design.

| Feature | VIBE Development | Context Engineering | Agentic Engineering |
|---|---|---|---|
| Core Philosophy | "Let's write a prompt and see if it works." | "Let's feed the model the absolute best data to get a great first-shot response." | "Let's build a programmatic loop so the model can solve complex, multi-step tasks." |
| System Architecture | Single-prompt, manual input. | Prompt templates, RAG pipelines, vector search, metadata filtering. | State machines, tool-calling loops, planning modules, self-reflection. |
| Autonomy Level | None (user drives). | Low (deterministic code retrieves context; LLM generates once). | High (LLM decides which tools to call, evaluates outcomes, loops). |
| Evaluation Method | Ad-hoc manual checking. | Structured offline evals (RAGAS, LLM-as-a-judge, retrieval precision). | Trajectory evaluation, task success rate, regression testing on loops. |
| Best Used For | Prototyping, personal productivity, simple drafting. | Q&A bots, search engines, summarization, structured data extraction. | Complex workflows, autonomous research, coding assistants, workflow automation. |

**Common pitfalls Gemini flagged:** over-agenting (reaching for an agent loop when a
well-designed context pipeline would do — agents are slower, costlier, non-deterministic);
falling back to vibes even inside a Context/Agentic system when updating prompts, instead of
running against a golden test set.

---

## Where GenAI-Logic actually sits

Gemini's three-way split sorts by **how much autonomy the LLM has**, as if that were one
axis with one answer per product. GenAI-Logic doesn't fit that shape because it uses AI at
two distinct moments, governed differently, and both matter:

**1. Authoring time — Context Engineering, in Gemini's own sense.** When a developer asks
the AI to write a rule, Context Engineering is what steers it toward the right LogicBank
rule type (sum vs. count vs. Allocate vs. Request Pattern) and resolves ambiguity (copy vs.
live reference, FK vs. text code) instead of letting it default to procedural code. The
"context" being curated is the accumulated knowledge of how a governed system should be
built, not retrieved documents for a single Q&A turn — same mechanism Gemini describes,
aimed at code generation instead of an answer.

**2. Runtime — bounded Agentic Engineering, governed by deterministic rules, not replaced
by them.** This is the correction to get right: GenAI-Logic doesn't avoid agentic behavior
at runtime, it fences it. An **AI Rule** — see `samples/basic_demo_ai_rules-supplier` —
is a live LLM call made *during* a transaction: `__Use AI__ to Set Item field unit_price by
finding the optimal Product Supplier based on cost, lead time, and world conditions`. That
call happens on every commit, with real autonomy (the AI picks the supplier, with real
judgment, not a lookup). What makes it governable is that the **deterministic rules around
it still apply to whatever the AI returns** — the chosen `unit_price` flows into
`Item.amount` → `Order.amount_total` → `Customer.balance`, and the credit-limit constraint
still fires. The project's own architecture diagram calls this explicitly: *"AI and Rules
together, not AI vs. Rules"* — R1 (deterministic DSL) and R2 (LLM calls) execute in the
same commit, with R1 governing R2's result. Every AI request and response is logged to an
audit table (`SysSupplierReq`) for review.

So the honest answer to Wynford's question isn't "GenAI-Logic is Context Engineering, not
Agentic Engineering" — it's **both, at different moments, with the agentic part
deliberately kept narrow and auditable** rather than an open-ended tool-calling loop. That
lines up with Gemini's own "Over-Agenting" warning: an AI Rule is one bounded judgment call
inside a rule chain, not a multi-step autonomous agent deciding what to do next. RFI
(Requirements From Interview — the AI interviews to close gaps in a requirement before
writing any rules) is the same shape: a scoped, human-confirmed interaction, not an
autonomous loop.

**What makes this evaluable, not just claimed:** the output at both moments is a durable,
inspectable artifact — the rule itself (version-controlled Python), the audit trail of
every AI request/response, and `docs/requirements/ad-libs.md` (every assumption the AI
made beyond the spec, flagged for review). An evaluator doesn't have to trust the
methodology; they can read the rule, replay the audit log, and confirm the constraint held.

## For the Town Hall questionnaire specifically

Wynford's draft question is good and should go as written — it's the right question to ask
FedEx's AI CoE. One addition worth considering: naming what makes a Context Engineering
*product* (as opposed to a Context Engineering *pattern* like RAG) evaluable on its own
terms — the artifact it outputs is source code that a human reviews and version-controls,
not a black-box answer. That's the detail an evaluator will actually want to test against:
"show me the rule it wrote, show me that it can't be bypassed." GenAI-Logic's own
`docs/requirements/ad-libs.md` (every assumption the AI made, flagged for review) and the
generated Logic Report (execution trace per rule chain) are the concrete artifacts that make
that evaluable, not just claimed.
