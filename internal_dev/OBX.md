# OBX — Out of Box Experience

No SEs/reps to set expectations — OBX *is* the sales process. Starts at a readme.

## Audience — two axes, not one list

- **Attitude:** Lovers (rare, shrinking — AI-code trust fell 40%→29% in a year, most-experienced devs most skeptical) vs. the real center, Skeptics+Neutrals (grants AI value at the margins, wants proof before trusting full systems, wants governance demonstrated not asserted — 55% of orgs now name governance as a buying criterion).
- **Role/stakes:** individual builder · veteran architect (wants proof fast, skip the convincing) · business stakeholder (BA/PM/tech mgr — wants speed + results) · diligence/acquirer (arrives via the Sierra pitch deck, verifies specific cited claims — not a 4th OBX persona, just needs those claims fast-findable).

Market check validates the site's proof-heavy approach (line counts, A/B bug count, never-doctored governance reports) as aimed at the right target — the gap is ordering/discoverability, not content.

## 3 Cases

1. **Local install** — `build_and_test/genai-logic/README.md`
2. **CS-MGR** — Codespaces. AI-lovers land here; confirmed post-pitch acquirer-verifiers also land here (genai-logic.com → Codespaces routes to CS-MGR). Content = same as #1.
3. **GLWS** (`org_git/genai-logic-web-studio`) — WebGenAI's replacement, now viable because frontier models don't need WebGenAI's old error-recovery machinery. Content ~identical to #1/#2 today. Its real differentiator is the friendlier UI + built-in IDE handoff, not readme text.

**Real differentiation today: install friction only.** Persona-tailored *content* across the three is mostly aspirational, not yet built.

## Findings

- Governance proof + customs examples are only 1 `<details>` deep — not buried, just 5th of 6 sections in reading order. Fix: a jump-point for readers who don't need the buildup (veteran architects, verifiers), not removal of the buildup itself.
- CE is never actually introduced — readme says "load CE" without saying what it is. Same gap that made `welcome.md` matter in the first place.

## AI Startup bug — known, deferred

`CLAUDE.md` now auto-loads (`@`-imports `copilot-instructions.md`) every session, unconditionally — breaks the "show brief `welcome.md` first" gate, which depends on Copilot never auto-reading the file. Confirmed live in this session.

**Decision:** keep the readme's "please load..." instruction as-is — low friction, not strictly required, preserves the two-step flow. **Not fixing** Claude's response to it right now — exposure is narrow (only local install + manually-added Claude; CS-MGR/GLWS are Copilot-only by design).

## Open question: speed vs. infrastructure framing

5-rules-vs-200-lines is framed as readability/maintainability, not speed — deliberately, to protect the "infrastructure, not code-gen" acquisition thesis. Presumption: readers infer the speed win themselves. **Untested.** Possible resolution: frame speed as a *consequence of governance* ("governed systems, in the time it takes to write requirements") rather than a competing headline.

## Low-code framing

Don't name or attack low-code. Dog-whistle the contrast via our own attributes ("plain Python, standard tooling, no proprietary DSL") and let low-code-burned readers connect the dots themselves. Partly already present (GLWS "Dev Friendly" bullet, "standard tooling" line) — just needs to land earlier.

## GLWS direction (business-user case)

**Superseded (2026-07-17) — see decision below.** Original direction (kept for history):
training ("here's how to use it") is priority; positioning/paradigm framing stays but
compressed to 1–2 lines up front — early, not deferred, not a section. Scoped to GLWS
only — CS-MGR/local readers (AI-lovers, veteran architects) want more depth up front.

### Decision (2026-07-17): drop the mini variant, README.md is the single basis

Context: GLWS gets an announcement video; the video should follow the readme's own
structure rather than a separate script. Val's read: a mini/fast-start variant and a
full README serve genuinely different formats (skim-a-doc vs. watch-a-video), and
maintaining both risked the same base-vs-basic_demo content drift already documented
elsewhere in this CE — the mini variant's content (see parked copy) was already
behind the full README on org-fit framing (see next section).

**Resolution:** `README.md` is now the single basis for both the doc and the video
shot list. Its existing numbered sequence under "Example — Existing Database"
(Declare it → Run it → Talk to your AI → Iterate → Why rules matter) already maps to
video chapters via the `<details>` structure — no separate script needed, curate from
what's there. The "impatient reader" need the mini variant existed to serve is met by
the README's own collapsed-by-default `<details>` sections: skim past what you don't
need yet, expand it later, same document, no drift risk.

**Open question, not yet resolved:** the README currently opens with AI-assistance/
model-picker mechanics (setup logistics) before "First Time Here?" / "The Vision"
(org-fit framing — see next section). For a BA/PM-aimed video, the org-fit hook is
probably the reason to keep watching past 30 seconds, not the model picker. Whether
to reorder the doc itself (not just the video) to lead with Vision — undecided.

`readme-mini.md` parked (not deleted) at `internal_dev/OBX-glws-mini-readme.md`,
next to this file rather than live in the GLWS repo where it could be mistaken for
current guidance.

### Org-fit content gap (found 2026-07-17, comparing README.md vs. mini)

Val's framing: a responsible BA/PM needs to know how this fits *within the org* —
not just "does the AI produce a correct system," but "does adopting this create a
new silo, a skills gap, or a governance blind spot." That's a different question
than the technical-credibility proof (CBSA catch, 40X line count, A/B bug count) —
those answer "is the tool good"; org-fit answers "can I defend this choice to my
CIO/compliance/risk team," which ties directly to the Audience Assumptions' "org
alignment (as opposed to shadow-IT wars)" line.

**Found only in README.md** ("The Vision" section, right after "First Time Here?"),
**absent from the (now-parked) mini variant entirely:**
- The actual "what is this" framing/intro paragraph.
- Four-bullet org-fit block — each bullet answers a specific handoff/ownership
  question:
  - **User Friendly** → BA/PM doesn't need to become a developer to drive it
  - **Dev Friendly** → existing dev team isn't sidelined or forced onto a
    proprietary tool — direct answer to "who maintains this, do we need specialists"
  - **DevOps Friendly** → no new infra spend or vendor lock-in on deployment —
    standard containers, existing cloud/on-prem process
  - **Enterprise Friendly** → security/integration aren't afterthoughts — already
    there when IT/compliance asks

This block is judged important enough that its absence from the mini variant was
itself one of the reasons to drop the mini variant rather than fix it in place —
the full README already had the content the business-user case needed; the mini
variant was behind, not ahead.
