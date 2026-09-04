---
title: RFI Transcript Format
Description: Format spec for the `<name>-transcript.md` file STEP 1a/1b write during a
  Requirements-from-Interview session. Kept out of copilot-instructions.md so the format
  detail only loads on the (relatively rare) session where an interview actually runs,
  not on every Manager CE read.
Source: ApiLogicServer-src/prototypes/manager/.github/rfi_transcript_format.md
Propagation: BLT process → Manager workspace
Usage: AI assistants read this ONLY when STEP 1a or STEP 1b is about to write
  `<name>/docs/requirements/<name>-transcript.md`. Not read at Manager CE activation.
version: 1.0
changelog:
  - 1.0 (Sep 4 2026) - Extracted from copilot-instructions.md STEP 1a/1b's inline
    "verbatim, human/AI turns, not paraphrased" instruction, which in practice produced
    a transcript with `(batched — see below)` placeholders under several questions and
    a separate "full batched answers" list the reader had to cross-reference — a real
    live-build artifact (library_rfi) that a human reviewer found hard to follow. Fixed
    live, then generalized here: each question's real answer goes directly under it, in
    the exact structure `AskUserQuestion` itself renders (Question / Options / Answered),
    not a paraphrased "AI: ... / User: ..." dialogue. Moved to its own file rather than
    expanded inline, to avoid growing copilot-instructions.md — which loads on every
    Manager CE activation — for guidance that only matters on the STEP 1a/1b path.
---

# RFI Transcript Format

Applies to `<name>/docs/requirements/<name>-transcript.md`, written by STEP 1a (full
Socratic interview) and STEP 1b (scoped interview on one flagged clause).

## Structure

For each question actually answered, in the order asked:

```
**Question: <short label>**
Options: <opt1> · <opt2> · <opt3> · ...

**Answered:** <the option selected, or the free-text answer if no AskUserQuestion was used>
```

- Blank line between `Options:` and `**Answered:**` — without it, Markdown renders them
  as one run-on paragraph instead of two visually distinct lines.
- Omit the `Options:` line entirely for a question answered as free text (no multiple-choice
  tool call involved) — don't invent options that weren't offered.
- If an options list was long and only partially visible/captured, say so briefly
  (`*(list continued past what was captured)*`) rather than either fabricating the rest
  or silently dropping the fact that it was truncated.

**⛔ Do not write placeholder text like `(batched — see below)` under a question, with the
real answer parked in a separate list further down.** This was a real, confirmed failure
mode (see changelog above) — it forces the reader to cross-reference two locations to learn
what was actually answered. Every question's real answer goes directly beneath it, full
stop, regardless of what order the underlying tool calls happened in or whether several
questions were captured in one batched call.

**Failed/skipped tool attempts (validation errors, aborted calls, retries) are process
detail, not part of the Q&A.** Do not show a question as answered with a placeholder, and
do not interleave failure narration into the Q&A body. Record them tersely in a trailing
section instead:

```
## Tool notes (process, not requirements)

- <what failed, why, how it was recovered — one or two lines per incident>
```

## After the Q&A

```
**AI synthesis, read back to user:**

> <the synthesized requirements paragraph(s), as actually shown to the user>

**User:** "<their confirmation, verbatim>"
```

**If the synthesis states a specific number/value that was never itself an option in any
question** (e.g. the questions established *shape* — "capped" vs "uncapped" — but not the
exact cap amount), say so plainly rather than letting the transcript imply every figure was
menu-selected:

```
**Note on specific numbers:** <which figures were option-selected vs. proposed by the AI
during synthesis and accepted via the readback confirmation, not chosen from a menu>.
```

This matters because `ad-libs.md` and other provenance docs may describe the interview as
having "confirmed" values that were, more precisely, AI-proposed defaults the user accepted
as part of a batched synthesis — accurate under STEP 1a/1b's own "synthesize + read back"
design, but worth stating precisely rather than papering over the distinction.

## Example (from a real run — library_rfi)

```markdown
**Question: Loan period**
Options: 21 days, 1 renewal · 14 days, 2 renewals · No renewals · Other (I'll specify)

**Answered:** 21 days, 1 renewal

**Question: Fines**
Options: Flat rate/day, capped · Flat rate/day, no cap · Grace period then flat rate ·
No fines · *(list continued past what was captured)*

**Answered:** Flat rate/day, capped

**Note on specific numbers:** the options above establish policy shape, not literal dollar
figures. The $0.25/day rate came from a free-text answer (see Tool notes); the $10 cap and
$5 block threshold were proposed by the AI in the synthesis below and accepted via "looks
good - proceed," not selected from a menu.

**AI synthesis, read back to user:**

> - Overdue Loans accrue a fine of $0.25/day (configurable), capped at $10/book (configurable).
> - Once unpaid fines reach $5 (configurable), the member is blocked from checking out
>   additional books.

**User:** "looks good - proceed"

---

## Tool notes (process, not requirements)

- First `AskUserQuestion` batch failed `InputValidationError` — three "Other" catch-all
  options were missing the required `label` field. Fixed by adding explicit `"label": "Other"`.
- The corrected retry failed again with `AbortError`. The user answered the fine-rate
  question inline in plain text instead; the remaining questions were re-asked in a fresh,
  successful call.
```
