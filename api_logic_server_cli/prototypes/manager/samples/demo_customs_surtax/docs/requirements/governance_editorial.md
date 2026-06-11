---
generated: 2026-06-10
generated_by: claude-sonnet-4-6 (valjhuber@gmail.com)
context: editorial commentary on docs/requirements/governance_report.md, written
         after comparing demo_customs_surtax (this project, generated 2026-06-10)
         against ../samples/demo_customs_surtax (reference implementation)
---

# Editorial: demo_customs_surtax vs. reference implementation

Engineering notes, not marketing. The governance report says this project scores
well (7.2 coverage, 94 integrity). That's accurate but incomplete — the score
formula can't see everything that matters. This is the "what the score doesn't
tell you" writeup.

## Real advantages of this project (not just "it also works")

**1. `is_steel_derivative` per-line gating is a genuine correctness improvement.**
The reference implementation gates the surtax at the *entry* level only. This
project adds `is_steel_derivative` to `HsCodeRate`/`SurtaxLineItem` and checks it
per line item (`SurtaxLineItem.surtax_applicable` requires both
`customs_entry.surtax_applicable == 1` AND `is_steel_derivative == 1`). That
matches the actual CBSA order, which applies to specific HS codes, not to every
line on an entry from a subject country. If a customs entry from a "subject"
country contains a mix of steel-derivative and non-steel-derivative goods, the
reference implementation would over-tax the non-steel lines. This isn't a style
preference — it's a different (and more correct) answer for mixed-commodity
entries.

**2. Proper `Date` columns instead of `Text`.** `ship_date`, `effective_date`,
`order_date` are `Date` here vs. `Text`/`String` in the reference. This means
`row.ship_date >= row.effective_date` in `cbsa_steel_surtax.py:35` is a real date
comparison, not a string comparison that happens to work for ISO-formatted dates
(until someone enters `12/26/2025` instead of `2025-12-26`). Small thing, but
it's the kind of latent bug that survives every demo and bites in production.

**3. `SysConfig` carries its own audit trail.** `order_title`, `order_date`,
`legal_authority` columns mean the regulatory citation is *in the data*, not just
in a comment or doc. If someone's looking at a `CustomsEntry` row and asks "under
what authority was this surtax applied," the answer is one join away. The
reference implementation doesn't carry this.

**4. The `country_surtax_rate > 0` check in `surtax_applicable`.** Worth calling
out because it's subtle: a country can be in `country_origin` with
`surtax_rate = 0` (CETA/CUSMA/CPTPP partners, per the docstring) without being
"exempt" in some special-cased way — they just naturally produce `surtax_amount = 0`
downstream. But without the `> 0` check in the `surtax_applicable` formula
(line 36), those entries would still be flagged `surtax_applicable = 1`, which is
wrong for reporting/filtering purposes even though the dollar amounts would come
out right. This is the kind of condition that's easy to miss and easy to
under-test (it only shows up when you query "show me all surtax-applicable
entries" and a 0%-rate country shows up in the list).

## Real gaps (the governance report mostly caught these)

**1. Docstring hygiene (-1, flagged).** The `declare_logic()` docstring in
`cbsa_steel_surtax.py` is a paraphrase with an invented numbered eligibility list.
Per `logic_bank_api.md`, this is explicitly the wrong pattern — "anything you add
becomes a spec you then code to" on the next AI iteration. Easy fix: replace with
the verbatim CBSA order text (or a pointer to `requirements.md` if that's where
the verbatim text lives). Low cost, but worth doing before this file is used as a
template for the next use case — the paraphrase pattern is exactly what an AI
reading this file next time will copy.

**2. Missing copy-vs-formula TODO block (not scored, but real).** The reference
implementation's `lookup_values.py` has the standard TODO comment reminding a
reviewer to check each `Rule.copy` for snapshot-vs-live correctness. This file has
7 `Rule.copy` calls and no such comment. In this domain the snapshot choice is
almost certainly *right* (you don't want a rate correction next month to silently
re-price last month's filings — see the governance report notes), but "almost
certainly right" is exactly the kind of judgment call that should be visible and
reviewed, not silently defaulted. Five-minute fix.

**3. Five unindexed FK columns (new check, -5 total, flagged in the gov report).**
`customs_entry.country_origin_id`, `customs_entry.province_id`,
`customs_entry.sys_config_id`, `surtax_line_item.customs_entry_id`,
`surtax_line_item.hs_code_id` — none have a covering index. At today's seed-data
scale this is invisible. The one to actually care about is
`surtax_line_item.customs_entry_id`: every `Rule.sum` rollup onto `CustomsEntry`
(total_customs_value, total_duty_amount, total_surtax_amount) does a lookup
against this column on every line-item write. Cheap to fix now (`CREATE INDEX` x5
+ rebuild-from-database), and worth doing before this becomes "the project we
loaded with 50,000 customs entries and now everything's slow."

## The gap the governance report *can't* see

**4. `country_code` (CountryOrigin) and `hs_code` (HsCodeRate) lost their
`unique=True` constraint vs. the reference implementation.** This is the one from
our earlier discussion — and it's worth restating here because it's the clearest
example of the gov report's blind spot. The health check (even with the new v1.4
schema checks) inspects `logic/logic_discovery/**/*.py` for rule-quality issues
and now `database/models.py` + `db.sqlite` for PK/FK-index structure — but it
doesn't diff column-level constraints like `unique=True` against anything. There's
no "reference" for it to diff against in a freshly-generated project; uniqueness
is a domain judgment call (should two `CountryOrigin` rows be allowed to share a
`country_code`?), not a structural defect like a missing PK.

Practical effect: nothing stops a duplicate `country_code='US'` row from being
inserted into `country_origin`. If that happens, `Rule.copy(derive=
CustomsEntry.country_surtax_rate, from_parent=CountryOrigin.surtax_rate)` would
copy from *whichever* row the FK happens to point at — not ambiguous at the rule
level (the FK is concrete), but the lookup/seed logic that *sets* the FK
(`country_origin_id`) could pick the wrong duplicate if it matches by
`country_code` rather than `id`. Low-probability, high-confusion-when-it-happens.

Fix is a one-line model change (`unique=True` on `country_code` and `hs_code`) +
DDL `ALTER TABLE ... ADD CONSTRAINT` (or recreate-and-copy, since SQLite can't add
a unique constraint to an existing column directly) + rebuild-from-database. Worth
doing if these lookup tables are seeded/maintained by hand; less urgent if they're
only ever populated by a single controlled seed script that you already trust not
to duplicate codes.

## Bottom line

This project is the stronger baseline of the two — the `is_steel_derivative`
gating alone is a correctness difference, not a style difference. The gaps here
are all small and mechanical: one docstring rewrite, one TODO comment, five
`CREATE INDEX` statements, and a `unique=True` decision on two lookup tables. None
of them require rethinking the rule design. Worth fixing before this project (or
its `cbsa_steel_surtax.py`) gets used as a template for the next use case, since
templates propagate their flaws.
