<!--
title: GLWS Announcement Video — Storyboard (Show / Say)
Status: draft script, not yet recorded
See internal_dev/OBX.md for the decision that README.md is the single basis for both
the doc and this video's shot list, and for the "Step 5 is a recap, not new claims"
principle this script applies to Beat 6.
-->

# GLWS Announcement Video — Storyboard

**Target length:** ~5 minutes (agreed after estimating honestly — 2-3 min was the
initial target, but the two "must run at real speed" beats — typing the prompt,
and the live trigger/save-fails moment — plus a proper setup+payoff for the
insert-vs-update aha don't fit in 2-3 min without cutting one of them, and both
earn their place. See "Timing Notes" at the end.)

**Narrator:** Val, first-person, talking to camera + screen capture. Confident,
unhurried, no hype-voice — same register as the README's hero line.

**Core rule for every beat:** no beat repeats a phrase from another beat. Say
each idea once, where it lands hardest, and move on. Never read the README
aloud — every line below is a compressed, spoken version of a README beat, not
a quotation of it.

---

## Beat 1 — Cold Open (0:00–0:20)

| SHOW | SAY |
|---|---|
| GLWS README hero section, or a plain title card. Cut fast — no lingering on logos/branding. | "This is GenAI-Logic Web Studio. What you're about to watch is a Business Analyst or Product Manager building a real, enterprise-class system, governed by rules you can read, trust, and maintain. No install. Runs in your browser. Let's build one, right now." |

---

## Beat 2 — Type the Prompt (0:20–1:00)

| SHOW | SAY |
|---|---|
| Codespaces, chat panel open, typing/pasting the prompt. Let the 5-line rule text actually sit on screen, readable, ~10-15 sec — this is real screen time, not choppable. | "Here's the whole spec. Five lines, plain English:" *(pause, let it read)* "That's it. That's the business policy. No developer wrote this — I did, in the language I already think in. Now I hit enter." |

**Prompt on screen:**
```
On Placing Orders, Check Credit
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
```

**Cut:** the 2-minute generation wait is edited out entirely — jump straight to a running system.

---

## Beat 3 — It's Already Running (1:00–1:20)

| SHOW | SAY |
|---|---|
| Admin App, already loaded — Swagger/API visible briefly. On-screen text overlay during the transition: "~2 min later". | "This is already running. Full REST API. Admin app. The five rules I just described are live, enforced, right now." |

**Why the cut:** the elapsed-time aside was verbal meta-commentary explaining
an edit — better handled as a small on-screen text card than spoken. Viewers
don't need cuts justified out loud; it also frees the narrator to open Beat 3
directly on the payoff (system's already running) instead of spending breath
on the edit itself.

---

## Beat 4 — The Trigger (1:20–1:55)

| SHOW | SAY |
|---|---|
| Real-time, unhurried, no speed-up: open Alice's unshipped order, find the Widget item, edit quantity to something absurd, hit save. No narration during the actual clicking/typing. Hold on the failure dialog 2-3 sec of silence after it appears. | "This is Alice's order — it hasn't shipped yet. I'm going to open this item, and change the quantity to something absurd." *(let the action play out, silent)* "And save." *(failure dialog appears)* "It fails." *(hold, silent)* |

**This beat must not be sped up or voiced over** — the credibility of the whole video depends on the viewer seeing this happen in real time, not as an edited trick.

---

## Beat 5 — Why This Matters (1:55–2:20)

| SHOW | SAY |
|---|---|
| Still on the failure dialog, or cut to narrator. | "That's not a form validator somebody bolted on. That's the exact policy I described a minute ago, in English — enforced, on every save, no matter where it comes from. The API. This admin app. An AI agent. A partner integration. Same rule. Same enforcement. Every time." |

---

## Beat 6 — Recap (2:20–2:45)

| SHOW | SAY |
|---|---|
| Brief pause — optionally the 5-rule prompt shown again, small, side-by-side with the fail dialog. | "Here's what you just watched. It has a name: Read, Trust, and Maintain. Five rules, not two hundred lines of code. A rule you can point to and know it runs. And when the requirements change — which they always do — you add a rule, you don't go untangle code to find where it belongs." |

**Why this beat exists, not cut:** Step 5 in the README ("Why rules are easy to
Read, Trust, and Maintain") is a recap, not new claims — the viewer already
*experienced* Readable, Trustworthy, and (partially) Maintainable in Beats 2
and 4. This beat's only job is to attach the memorable name to what they just
watched, once, out loud — not re-explain it. Cutting it entirely was
considered and rejected: the phrase needs to land as its own moment or it
never sticks.

---

## Beat 7 — The Insert-vs-Update Aha (2:45–3:40)

| SHOW | SAY |
|---|---|
| Back to chat panel briefly, then repeat the large-quantity-and-save trigger — but this time editing an existing order, framed explicitly as "editing, not placing." Let it fail again, real-time, but this run can move faster than Beat 4 since the viewer already knows the shape of it. | "Here's the part that actually surprised me the first time I saw it. That rule — 'On *Placing* Orders, Check Credit' — I only described what happens when you *place* an order. I said nothing about editing one. Watch what happens when I *edit* an existing order instead." *(trigger plays out)* "Same failure. I never wrote a rule for updates. The system didn't need one. Design it once, and it governs every path the change can arrive by — insert, update, delete, an AI agent, whatever comes next. That's what a rules engine gives you." |

**This is the single most differentiating moment in the video** — it's proof
the system generalizes to a case nobody explicitly coded for, not just a
scripted demo. Give it a real setup + payoff; don't rush it into a single line.

---

## Beat 8 — Close (3:40–4:15)

| SHOW | SAY |
|---|---|
| Back to narrator, or a simple end-card with the Codespaces link. Hold end card ~5 sec. | "This is a real, running system. Full API. Admin app. Governed logic, exactly as I described it — nothing hidden, nothing hand-tuned after the fact. And this isn't a five-table toy — the same rules engine you just watched holds up on enterprise-scale schemas, hundreds of tables, real production volume. It fits how your organization already works: standard tooling, no proprietary lock-in, hand it to your dev team whenever you're ready. Try it yourself — the link's below. It's the same five lines you just watched me type." |

**Note:** paraphrase here ("governed logic, exactly as I described it") —
do NOT restate "Read, Trust, and Maintain" again; that phrase is spent in Beat 6.

---

## Timing Notes

- Running total as scripted: ~4:15. Add ~30-45 sec of natural pacing (breaths
  between beats, the two "let it play out live" moments running a few seconds
  longer than estimated in a real take) → lands at **~5 minutes**.
- The two beats that must NOT be sped up or voiced-over while acting: Beat 4's
  trigger, and Beat 7's second trigger.
- Everything else (Beats 1, 3, 5, 6, 8) can be cut tight in editing — these are
  voiceover-over-b-roll, 10-25 sec each, no real-time constraint.
- Discipline is in trimming words per beat, not cutting beats — all 8 earn
  their place; the temptation to hit a shorter runtime should come from
  tighter language, not dropping Beat 6 or Beat 7.
