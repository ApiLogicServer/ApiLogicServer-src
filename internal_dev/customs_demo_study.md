# CE Revision — Executive Summary
**Date:** 2026-02-27  
**Context:** Context Engineering (CE) fixes identified during `customs_demo_plus` post-mortem

---

## Origin: What Launched This Study

**Phase 1 — `customs_app` (seemed solid):**  
Built a hand-crafted CBSA surtax reference implementation (`customs_app`). The underlying database had been seeded from a `basic_demo`-derived schema that still contained `Customer → Order → Item`, `Product.unit_price`, etc. Results were excellent — 16 declarative rules, correct schema, clean architecture. CE was judged adequate.

**Phase 2 — `customs_demo_plus` (the mess):**  
Attempted to reproduce the result from clean `starter.sqlite` — a blank-slate database with no `basic_demo` artifacts. The AI produced a dramatically worse result: wrong schema, no `Rule.copy`, procedural fallbacks, Request Pattern misapplication. The CE that "worked" for `customs_app` was not actually adequate — it had been riding the `basic_demo` schema as invisible few-shot examples.

**Phase 3 — this study:**  
Systematic iteration to identify root causes, fix CE, and validate with the methodology below until a clean `starter.sqlite` project matched `customs_app`'s 16-rule result.

---

## Key Takeaways

1. **Bad prompt from a discarded path needed removal.** `subsystem_creation.md` had been written from a failed iteration and documented wrong patterns as `✅ CORRECT` — the `SysCustomsReq` wrapper, `early_row_event + session.query()` rate lookup, 3-column province model. Any AI reading it faithfully would reproduce those failures. CE can actively mislead. *(In fairness: this was a joint human+AI authoring mistake — we're only partly human.)*

2. **The ghost of `basic_demo` had unexpected depth.** AI will infer patterns from anything in scope — not just explicit instructions, but schema artifacts in the working database. `basic_demo`'s `Order → Item → Product.unit_price` structure silently guided the AI toward header/detail design, flat reference tables, and `Rule.copy`. When that ghost was removed, the CE's real coverage became visible. **AI is an aggressive pattern-matcher: it will use every signal it can find, intended or not.**

3. **Generalize `basic_demo` principles explicitly into CE.** The solution was not to restore the ghost — it was to make the implicit explicit: header/detail schema hint in the prompt, flat reference table principle in `subsystem_creation.md`, `Rule.copy` as default in `logic_bank_api.md`. What `basic_demo` had been providing for free is now provided by deliberate CE.

4. **Significant discovery — treat the prompt as a floor, not a ceiling.** When a prompt provides an explicit column/table spec, AI switches from architect mode (apply domain knowledge) to builder mode (implement exactly what's described). This suppresses domain-standard fields and constraints the prompt author assumed were obvious. The fix — the `spec = floor` principle added to `subsystem_creation.md` — reframes the spec as a minimum anchor and restores autonomous domain reasoning. This is the most generalizable finding: it applies to any domain, not just customs.

5. **The validation methodology compounds.** The gen → compare-against-reference → analyze → fix-CE → repeat loop with a fixed reference implementation as ground truth is what made all of this tractable. Without `customs_app` as a yardstick, iteration would have been guesswork.

6. **Ghost context is not limited to database schemas — it includes existing code and documentation.** The `customs_demo` readme explicitly described "16 declarative rules" with a breakdown by type and named `duty` (implying `base_duty_rate`). When Copilot generated the logic file, that readme was in context — making it impossible to know whether the AI inferred correctly from the prompt+CE, or simply transcribed from the readme. **Be mindful of everything lying around in the project**: readmes, existing logic files, prior-iteration code. Any of it can act as an implicit few-shot example, for better or worse.

---

## What Went Wrong

The `customs_demo_plus` project (CBSA Steel Surtax, created from `starter.sqlite`) produced significantly worse results than `customs_app` — which had been created from a database seeded with `basic_demo` schema artifacts.

Investigation revealed three root causes.

### Methodology

This was a very interesting joint AI/human design; the approach:

1. Gen customs_app
2. Ask genned app to compare itself to the reference implementation
3. Analyze the comparison in a long-running manager session in mgr Copilot with full CE (mgr, project, internals)
4. Ask Copilot to Revise CE (in src and venv), and update this document
5. Repeat

---

## Root Cause 1 — `basic_demo` schema artifacts as hidden implicit few-shot examples (MAJOR)

`customs_app` worked because it was built from a database that still contained `basic_demo` schema objects — `Customer → Order → Item`, `Product.unit_price`. These acted as **silent few-shot examples** that guided the AI toward:

- Header/detail schema structure (`CustomsEntry → SurtaxLineItem`, like `Order → Item`)
- Flat single-column reference data (`HSCodeRate.surtax_rate`, like `Product.unit_price`)
- `Rule.copy` from parent (`Item.unit_price ← Product.unit_price`)
- Plain domain insert — no Request Pattern wrapper

When `customs_demo_plus` was created from clean `starter.sqlite`, all four implicit constraints vanished. The CE had never made them explicit — the system had been correct for the wrong reasons.

**This is the diagnostic root cause.** It exposed everything else. Without `basic_demo` pollution, the weaknesses in CE Roots 2 and 3 became visible failures.

The fix: the schema hint sentence ("transactions are placed as a CustomsEntry with multiple SurtaxLineItems, one per HS code") and the CE additions below make these constraints explicit and durable — independent of what's in the source database.

---

## Root Cause 2 — CE encoded a failed implementation as correct guidance

`subsystem_creation.md` was written from a `customs_demo_plus` iteration that itself had gone wrong. The bad patterns were documented as `✅ CORRECT`:

| What the CE taught (wrong) | What should have been there |
|---|---|
| `SysCustomsReq` table wrapping a `CustomsEntry` insert | Direct domain insert — rules derive everything automatically |
| `early_row_event + session.query()` to look up a surtax rate | `Rule.copy(derive=SurtaxLineItem.surtax_rate, from_parent=HSCodeRate.surtax_rate)` |
| `Province.gst_rate / hst_rate / pst_rate` (3-column conditional) | `Province.tax_rate` single pre-combined column |

Any AI reading the old CE faithfully would reproduce exactly those failures. The CE was not missing guidance — it had *inverted* guidance.

---

## Root Cause 3 — Missing CE: flat reference table as default

No CE file stated the principle:

> **Reference/lookup tables store their rate as a flat column on the parent row — the same way `Product.unit_price` is modeled. Copy it with `Rule.copy`. Introduce a versioned child table only if the prompt explicitly mentions `effective_date`, rate history, or versioning.**

Without this, AI "modeled it properly" → created a separate `SurtaxRate` child table → `Rule.copy` impossible → forced `early_row_event + session.query()` → caused nested-flush errors → triggered the (incorrect) Request Pattern workaround.

One schema decision cascaded into three downstream failures.

---

## How They Connected

Root 1 (`basic_demo` pollution) meant the system had been working silently on borrowed context — not because the CE was adequate.  
Root 3 (missing flat-reference-table principle) caused the original `customs_demo_plus` schema failure once that borrowed context was gone.  
Root 2 (inverted CE guidance) occurred when that failure was *documented* without recognizing it was wrong — locking the bad patterns into the CE for future runs.

The fix required rewriting against the **reference implementation** (`customs_app`) rather than the failed one, and making all four `basic_demo` implicit constraints explicit in the CE.

---

## Files Changed

| File | Change | Propagated |
|---|---|---|
| `docs/training/logic_bank_api.md` | Added copy-vs-formula section: `Rule.copy` as default, TODO convention, anti-pattern warning | org_git ✅, venv ✅ |
| `docs/training/subsystem_creation.md` | Added reference table design principle; fixed province model; flipped lookup anti-pattern; replaced `SysCustomsReq` Part 3 with direct insert; fixed Mistake #3 and Quick Ref. Added **"Lookup References: Use FK Integers, Not String Codes"** section. Added **Part 5: Seed Data** — `alp_init.py` path fix, ranked patterns table, 4 common failure/fix pairs, never-heredoc rule. Updated Quick Reference (5 items). Added **"Governing Principle: Prompt Spec = Floor, Not Ceiling"** section (first after intro) — explicit specs are minimum anchors; flesh out with domain-standard fields, constraints, sums; domain expert omissions = expected not excluded. Added as Quick Reference item 0. | org_git ✅, venv ✅ |
| `docs/training/RequestObjectPattern.md` | Removed `DutyCalculation` example; added `SysEmail`+`SysSupplierReq` as canonical examples; added domain-data-entry negative gate | org_git ✅, venv ✅ |
| `.github/.copilot-instructions.md` | Tightened Request Pattern trigger — explicit ✅/❌ examples; customs domain insert named as ❌. Added: **"create runnable UI"** = seed data + Admin App — never custom HTML/Flask template. Fixed venv path: `source venv/bin/activate` → `source ../venv/bin/activate` (shared manager venv). | `basic_demo_16_02_00x` ✅, org_git `prototypes/base` ✅, venv `prototypes/base` ✅ |

---

## Key Principles Now in the CE

1. **Schema hint required for subsystem prompts:** "Transactions are placed as a `CustomsEntry` with multiple `SurtaxLineItems`, one per imported product HS code." — names header/detail entities explicitly so AI doesn't need `basic_demo` as an implicit guide.
2. **Reference table default:** flat column + `Rule.copy`. Versioned child table only on explicit prompt signal.
3. **`Rule.copy` is the default** for parent-value access (snapshot, safe). `Rule.formula` is the escalation (live propagation).
4. **Request Pattern scope:** integration side-effects only — email, Kafka, AI calls. NOT for domain data entry where rules derive computed columns.
5. **Domain insert is the pattern** for transactional domain objects. Direct insert → LogicBank rules fire automatically. No `Sys*` wrapper needed.
6. **"Create runnable UI"** = seed example data + Admin App at `http://localhost:5656`. Never a custom HTML page, Flask template, or calculator endpoint.
7. **Lookup references use FK integers:** when the prompt supplies codes/names for a known entity (country, province, HS code, product, customer), the transactional table stores `country_origin_id FK → CountryOrigin.id` — not `country_of_origin = "DE"`. Gate: apply to lookup entities; free text (notes, address) stays as String. FK is what makes `Rule.copy` traversable; text code = no relationship = no `Rule.copy`.
8. **Seed data canonical pattern:** use `alp_init.py` with `sys.path.insert(0, str(Path(__file__).parent.parent.parent))` at top — Flask + LogicBank active → all rules fire → correct computed values on first load. Never shell heredocs (garbled by terminal tool). `APILOGICPROJECT_NO_FLASK=1` suppresses LogicBank → zero computed fields.
9. **Spec = floor, not ceiling — never suppress domain knowledge:** when a prompt provides an explicit column list or table spec, interpret it as the *minimum anchor* (the fields the author needed to control), not as a *complete design*. Apply domain knowledge to flesh out the rest: standard rate/amount/date fields for the domain, `Rule.constraint` on quantity and price columns, audit fields, etc. The prompt author is a domain expert who omitted "obvious-to-them" fields — treat omissions as "expected" not "excluded." **This is the governing principle:** explicit specs buy FK correctness; domain knowledge buys completeness. Both must be active simultaneously.

---

## Validation Test — `customs_demo_ce_fix`

Created from `starter.sqlite`. Results are **mixed — catastrophic failures eliminated, nuanced failures remain.**

### Fixed ✅
| Issue | Old behavior | New behavior |
|---|---|---|
| Request Pattern misapplication | `SysCustomsReq` wrapper table | Direct domain insert |
| Custom HTML UI | Calculator page generated | No custom HTML |
| Header/detail structure | Flat or wrong | `CustomsEntry → SurtaxLineItem` present |
| Rule count | 6 flat rules | 10 rules (closer to reference 16) |
| Nested flush errors | Yes | No |

### Still Failing ❌
| Issue | Root cause | Fix needed |
|---|---|---|
| `early_row_event + session.query()` still used (0 `Rule.copy`) | AI stores `country_of_origin = "DE"` (text) instead of FK → `Rule.copy` structurally impossible | ✅ CE fix added (FK integers section in `subsystem_creation.md`) — needs re-test |
| Province 3-column design returned (`federal_rate`, `provincial_rate`, `hst_rate`, `uses_hst`) | Prompt phrase "provincial sales tax or HST where applicable" → conditional logic → multi-column | Province prompt phrase must be narrowed: "Province has a single combined `tax_rate` column" |
| 0 constraints | Were implicit in `basic_demo` logic examples; not in CE | Add constraint examples to CE or prompt explicitly |

### Key Metric Comparison
| Metric | `customs_demo_ce_fix` | `customs_app` (reference) |
|---|---|---|
| Total rules | 10 | 16 |
| `Rule.early_row_event` | 1 | 0 |
| `Rule.copy` | 0 | 2 |
| `Rule.constraint` | 0 | 3 |
| `Rule.sum` | 4 | 5 |

**Root of remaining failures:** The CE fixes are correct, but the customs prompt's phrasing still triggers wrong schema decisions — text-code storage and multi-column province design — which make `Rule.copy` impossible regardless of CE content. The next fixes are **prompt-level**, not CE-level.

---

## Prompt Analysis

### Current Prompt (verbatim)

```
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917 
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order 
 under subsection 53(2) and paragraph 79(a) of the 
 Customs Tariff program code 25267A to calculate duties and taxes 
 including provincial sales tax or HST where applicable when 
 hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26' 
 and create runnable ui with examples from Germany, US, Japan and China
 Transactions are received as a CustomsEntry with multiple 
 SurtaxLineItems, one per imported product HS code.
```

### Phrase-Level Failure Analysis

| Phrase | What AI does | Why it fails |
|---|---|---|
| `"provincial sales tax or HST where applicable"` | Creates `Province` with `federal_rate`, `provincial_rate`, `hst_rate`, `uses_hst` columns + conditional branching logic | "where applicable" = conditional → multi-column. Makes `Rule.copy` awkward; breaks flat-reference-table principle |
| `"country of origin"` | Stores as text column `country_of_origin = "DE"` | Sounds like a free-text field, not a FK. No parent table → `Rule.copy` impossible → forces `early_row_event + session.query()` |
| `"province code"` | Stores as text column `province_code = "ON"` | Same problem — "code" implies string identifier, not FK. Text storage = no parent relationship = no `Rule.copy` |
| `"hs codes"` (plural, lowercase) | Sometimes stored as text array or multi-value column | Ambiguous cardinality; should be `hs_code_id FK → HSCodeRate` |

### Root of All Three: ambiguous reference semantics

The prompt says "when hs codes, country of origin, customs value, and province code" — all three lookup values are described as **codes** (strings), not as FK references to a parent table. The AI therefore stores them as text columns. Once stored as text, `Rule.copy` from a parent is structurally impossible — there is no parent relationship to traverse. This forces `early_row_event + session.query()` which then hits the nested-flush constraint.

### Proposed Fixed Prompt

Two targeted changes: (1) province → single flat rate, (2) country/province/hs_code → FK references.

```
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917 
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order 
 under subsection 53(2) and paragraph 79(a) of the 
 Customs Tariff program code 25267A to calculate duties and taxes.
 Lookup tables: HSCodeRate (hs_code PK, surtax_rate), 
 CountryRate (country_code PK, surtax_rate), 
 Province (province_code PK, tax_rate — a single pre-combined rate whether HST or GST+PST).
 SurtaxLineItem references these by FK: hs_code_id, country_id, province_id.
 ship date >= '2025-12-26'.
 Create runnable ui with examples from Germany, US, Japan and China.
 Transactions are received as a CustomsEntry with multiple 
 SurtaxLineItems, one per imported product HS code.
```

**Key changes:**
- `"provincial sales tax or HST where applicable"` → `"Province (province_code PK, tax_rate — a single pre-combined rate whether HST or GST+PST)"`  eliminates the conditional/multi-column trigger
- `"country of origin"` + `"province code"` + `"hs codes"` → explicit `Lookup tables: ... SurtaxLineItem references these by FK` — forces FK relationships, enables `Rule.copy`
- Constraints (`ship_date >= entry_date`, `quantity > 0`, `unit_price > 0`) still need to be added explicitly or via CE

---

## Validation Test — `customs_demo_v2`

Created from `starter.sqlite` with the fixed prompt (explicit FK schema, single province `tax_rate`). Results are **significantly improved — FK and province fixes confirmed working.**

### Fixed vs `customs_demo_ce_fix` ✅
| Issue | `customs_demo_ce_fix` | `customs_demo_v2` |
|---|---|---|
| `Rule.copy` count | 0 | **3** — `hs_surtax_rate`, `country_surtax_rate`, `province_tax_rate` all via FK |
| `Rule.early_row_event + session.query()` | 1 | **0** — no longer needed |
| Province design | 4 columns (`federal_rate`, `provincial_rate`, `hst_rate`, `uses_hst`) | **1 column** (`tax_rate`) |
| Seed data with LogicBank | Not verified | **✅ Flask context — all totals auto-calculated at load time** |
| Country/province/hs FKs | Text codes (`"DE"`, `"ON"`) | **Integer FKs** (`country_id`, `province_id`, `hs_code_id`) |
| Admin App URL | Wrong (guessed) | `.copilot-instructions.md` has `http://localhost:5656/` — correct |

### Key Metric Comparison (all three)
| Metric | `customs_demo_ce_fix` | `customs_demo_v2` | `customs_app` (reference) |
|---|---|---|---|
| Total rules | 10 | **13** | 17 |
| `Rule.copy` | 0 | **3** | 2 |
| `Rule.early_row_event` | 1 | **0** | 0 |
| `Rule.formula` | 5 | 6 | 7 |
| `Rule.sum` | 4 | 3 | 5 |
| `Rule.constraint` | 0 | **1** | 3 |

### Structural difference: country/province placement

`customs_demo_v2` places `country_id` and `province_id` FKs **on each line item** (Form B3 accurate for multi-origin entries). `customs_app` places them on the order header. Both are valid designs; v2 is more faithful to CBSA Form B3.

Consequence: v2 gets a direct `Rule.copy` for `province_tax_rate` (line→Province FK). `customs_app` requires a `calling=` function because the path is `line → order → province` (two hops, no direct FK).

### Still Missing in `customs_demo_v2` ❌
| Issue | Root cause | Fix |
|---|---|---|
| `Rule.constraint` = 1 vs 3 | `qty > 0` and `unit_price > 0` not in prompt | Add to prompt explicitly |
| `base_duty_rate` absent from `HSCodeRate` | Not specified in prompt | Add `HSCodeRate (hs_code PK, base_duty_rate, surtax_rate)` to prompt |
| `total_duty` sum absent from `CustomsEntry` | No `duty_amount` on line (no `base_duty_rate`) | Follows from above |
| `surtax_applicable` flag not modeled | Constraint blocks pre-cutoff entries entirely; no historical data path | Add `surtax_applicable` formula + flag pattern to prompt if pre-cutoff support needed |
| `Rule.sum` = 3 vs 5 | Missing `total_duty` (no base duty) + one extra in `customs_app` for `duty_amount` | Follows from base_duty_rate gap |

### Root Cause: "Spec as Ceiling" — the explicit-spec suppression effect

Both the missing `Rule.constraint` and the missing `base_duty_rate` (+ `duty_amount`, `total_duty`) share the same disease, manifesting at two levels:

| Level | Missing in v2 | Present in customs_app | Why |
|---|---|---|---|
| Schema | `base_duty_rate`, `duty_amount` | ✅ Present | `customs_app` prompt had no column spec — Claude applied domain knowledge. V2 spec said `HSCodeRate (hs_code PK, surtax_rate)` — Claude implemented exactly that, stopping at the ceiling. |
| Rules | `qty > 0`, `unit_price > 0` constraints | ✅ Present | `customs_app` minimal prompt → "design a good system" mode. V2 explicit spec → "implement exactly what's described" mode. |

**The disease:** When Claude receives an explicit column/table spec, it interprets it as a *complete* definition, not a *minimum anchor*. It switches from **architect mode** (apply domain knowledge, flesh out the design) to **builder mode** (implement the spec faithfully, don't deviate). The prompt author wrote the spec to fix the FK problem — they specified only what they needed to control; they expected Claude to complete the rest. But Claude read "here is the schema" as "here is the *full* schema."

This is **fixing the symptom, not the disease** if we respond by adding `base_duty_rate` to the prompt or adding constraint examples to CE. Those patch individual omissions but don't address the mode-switching. Next time there will be different omissions.

### The Real Fix: teach Claude that spec = floor, not ceiling

The CE needs a principle that explicitly reframes how to read a prompt spec:

> *A column list in a prompt is a **minimum anchor** — the fields the prompt author needed to specify to ensure correct structure. It is **not a complete design**. Apply domain knowledge to flesh out the table beyond the spec: standard rate/amount/date fields for the domain, `Rule.constraint` on quantity and price columns, audit columns where appropriate. The prompt author omitted "obvious" fields — obvious to a domain expert. Treat omissions as "expected by the author" not as "not required."*

This preserves the FK precision (the spec anchor) while restoring the autonomous domain-knowledge layer. Both modes active simultaneously: **follow the spec AND architect the rest.**

### Implication for CE

The fix belongs in `subsystem_creation.md` as a new principle, not in the prompt. It should cover:
1. Column lists = minimum anchor, not ceiling — flesh out with domain-standard fields
2. `Rule.constraint` on quantity/price columns is always expected (not "only if specified")
3. The prompt author is a domain expert who wrote the minimum they needed to control — infer the rest

### Overall Assessment

**The FK integers CE fix is validated — 0 → 3 `Rule.copy` is the headline win.** The remaining gaps (`base_duty_rate`, constraints) are both instances of the same "spec as ceiling" suppression effect — a single CE principle fixes both. Next: add "spec = floor not ceiling" principle to `subsystem_creation.md`.

---

## Validation Test — `customs_demo_v3`

Created from `starter.sqlite` with the **same prompt as v2** — only variable is the new "spec = floor, not ceiling" CE principle added to `subsystem_creation.md`. Tests whether the principle alone restores `base_duty_rate` and qty/price constraints.

### Key Metric Comparison (all four)
| Metric | `ce_fix` | `v2` | `v3` | `customs_app` (reference) |
|---|---|---|---|---|
| Total rules | 10 | 13 | **11** | 17 |
| `Rule.copy` | 0 | 3 | **3** ✅ | 2 |
| `Rule.early_row_event` | 1 | 0 | **0** ✅ | 0 |
| `Rule.formula` | 5 | 6 | **4** | 7 |
| `Rule.sum` | 4 | 3 | **3** | 5 |
| `Rule.constraint` | 0 | 1 | **1** | 3 |

### What the spec=floor principle restored ✅
The principle worked for **generic domain elaboration**:
- Added `importer_name`, `entry_date`, `notes` to `CustomsEntry` — domain-standard audit fields
- Added `effective_surtax_rate` column (combined HS + country rate) — makes the combined rate visible in UI
- Added `entry_date` to header — audit trail field not in prompt

### What the spec=floor principle did NOT restore ❌
| Missing | Why principle wasn't enough |
|---|---|
| `base_duty_rate` on `HsCodeRate` | CBSA-specific domain knowledge — not a general convention Claude knows. The principle restores *generic* elaboration; it cannot supply *domain-specific* field knowledge the AI doesn't inherently have. |
| `quantity × unit_price` model | V3 **regressed** from v2: chose `declared_value` (a scalar) over `quantity + unit_price`. This is a different (plausible) valuation model, but loses the formula rule *and* makes qty/price constraints irrelevant. |
| Constraints = 1 vs 3 | Partly a consequence of the `declared_value` regression (no `quantity` or `unit_price` columns to constrain). The principle's "always add `quantity > 0` and `unit_price > 0`" bullet didn't fire because those columns don't exist in v3. |

### Root cause of `declared_value` regression

The prompt says "customs value" — Claude correctly identified this as the taxable value basis, but v3 modeled it as a single `declared_value` input rather than a derived `customs_value = quantity × unit_price`. The prompt never mentions "quantity" or "unit_price" as field names — Claude inferred the simpler model. V2 happened to get it right by chance; v3 went the other way. Both are valid responses to the same ambiguous prompt.

**This is ambiguity, not a CE failure.** Fix: add `quantity`, `unit_of_measure`, `unit_price` explicitly to the prompt spec.

### Revised conclusion on spec=floor principle

The principle has two distinct operating ranges:

| Field type | spec=floor effective? | Reason |
|---|---|---|
| Generic domain conventions (`entry_date`, `notes`, audit columns) | ✅ Yes | Claude has broad cross-domain knowledge — "transactions have entry dates" is universal |
| Domain-specific standard fields (`base_duty_rate` for tariff tables) | ❌ No | See Root Cause 1 — this field came from `Product.unit_price` as an implicit template, not from Claude's tariff domain knowledge |
| Ambiguous prompt terms (`customs_value` → qty×price vs scalar) | ❌ No | Ambiguity resolution is non-deterministic; principle can't help |

**The principle is doing its intended job** for the generic case. For the domain-specific gaps, the diagnosis is Root Cause 1 again — not a Claude knowledge gap.

### `base_duty_rate` is another Root Cause 1 artifact

`customs_app` got `base_duty_rate` because the database still contained `Product.unit_price` — a reference table with a primary rate field. Claude used `Product` as a silent template: "a tariff reference table should have a base rate (`base_duty_rate` = MFN tariff) AND an additional rate (`surtax_rate` = PC 2025-0917 levy)" — exactly the same way `Product.unit_price` has a single value.

Without `Product` in the `starter.sqlite` schema, v2 and v3 had no template to anchor that inference. The mapping:

| `basic_demo` implicit template | CBSA inference in `customs_app` |
|---|---|
| `Order → Item` header/detail | `CustomsEntry → SurtaxLineItem` |
| `Product.unit_price` flat reference column | `HSCodeRate.base_duty_rate` flat base rate |
| `Item.unit_price ← Product.unit_price` copy | `SurtaxLineItem.duty_rate ← HSCodeRate.base_duty_rate` copy |

This means there is **no CE fix** for `base_duty_rate` — the implicit template that produced it in `customs_app` no longer exists in the clean `starter.sqlite` workflow. The only fix is the prompt. And there is no risk of the spec=floor principle ever restoring it — it's not a general convention, it's a `basic_demo` ghost.

### Updated conclusion on remaining gaps

| Gap | Root cause | Fix |
|---|---|---|
| `base_duty_rate` absent | Root Cause 1 — `Product.unit_price` implicit template gone | Add `HSCodeRate (hs_code PK, base_duty_rate, surtax_rate)` to prompt — no CE equivalent |
| `quantity × unit_price` model | Prompt ambiguity — "customs value" resolved as scalar | Add `SurtaxLineItem: quantity, unit_of_measure, unit_price; customs_value = quantity × unit_price` to prompt |
| Constraints = 1 vs 3 | Follows from qty/price prompt fix | Once `quantity` and `unit_price` are explicit, CE spec=floor principle fires correctly |

---

## Validation Test — New Release (`customs_demo`)

Created from `starter.sqlite` using the v3.8 release with all CE fixes applied. The v4 prompt (including `base_duty_rate`, explicit `quantity/unit_of_measure/unit_price`, and `customs_value = quantity × unit_price`) was used.

### Key Metric Comparison (all iterations)

| Metric | `ce_fix` | `v2` | `v3` | **new release** | `customs_app` (reference) |
|---|---|---|---|---|---|
| Total rules | 10 | 13 | 11 | **16** ✅ | 16 |
| `Rule.copy` | 0 | 3 | 3 | **1** (+1 formula-copy) | 2 |
| `Rule.formula` | 5 | 6 | 4 | **7** ✅ | 7 |
| `Rule.sum` | 4 | 3 | 3 | **5** ✅ | 5 |
| `Rule.constraint` | 0 | 1 | 1 | **3** ✅ | 3 |
| `Rule.early_row_event` | 1 | 0 | 0 | **0** ✅ | 0 |
| `base_duty_rate` present | ❌ | ❌ | ❌ | **✅** | ✅ |
| `quantity × unit_price` model | N/A | ✅ | ❌ (scalar) | **✅** | ✅ |

### Result: Functionally at par with the reference ✅

16 rules — identical total to `customs_app`. All three constraints firing. All five sums present. `base_duty_rate` present. `qty × unit_price` model correct. Zero `early_row_event + session.query()` anti-pattern.

The CE study paid off: every root cause fix validated across the iteration chain produces a result equivalent to the hand-crafted reference.

### Differences from reference (refinements, not correctness failures)

| Priority | Difference | Impact |
|---|---|---|
| **High** | `Float` vs `DECIMAL` for monetary/rate columns | Floating-point drift in production |
| **High** | `surtax_applicable` on line item (N formulas) vs order header (1 formula) | Efficiency + single-responsibility |
| **Medium** | No `to_date()` helper / session fallback in `surtax_applicable` formula | Brittle if `ship_date` stored as `Date` object |
| **Medium** | `entry_date` absent from `SurtaxOrder` | Loses per-entry ship-date consistency check |
| **Low** | Relationship names use class-name casing (`.SurtaxOrder`) vs snake_case | Convention only |

### Seed data conflict identified

`copilot-instructions.md` v3.8 step 6 said: *"create `database/test_data/<name>_seed.py` using plain `DeclarativeBase` models (not SAFRS models — seed scripts run outside Flask context)"* — directly contradicting the CE canonical of `alp_init.py` with Flask context active. Running outside Flask context suppresses LogicBank → all computed fields are zero. **Fixed in `copilot-instructions.md` (customs_demo + org_git/prototypes/base + venv/prototypes/base).**

---

## Validation Test — `customs_demo_v1a` (clean context, no readme ghost)

Created from `starter.sqlite` with **Prompt B only** (the readme prompt). The `customs_demo` readme was **not** in the Copilot context — deliberate clean-room test to determine whether `customs_demo`'s 16-rule result came from the CE or from the readme acting as a ghost.

### Session Issues Encountered

Three process failures occurred before any logic was written — all confirming known CE gaps:

| # | Issue | Root cause | Impact |
|---|---|---|---|
| 1 | Venv error — AI tried to create a new venv | `../venv/bin/activate` search didn't find the shared manager venv at grandparent level | ~3 min delay |
| 2 | Heredoc terminal corruption | `sqlite3 ... << 'SQL'` here-doc garbled by terminal tool | Schema creation failed; switched to Python script |
| 3 | `alp_init.py` file-exists error | `create_file` rejected because template already exists; then first `replace_string_in_file` had wrong `sys.path` setup | Two extra edit rounds |

Issues 1 and 2 are recurring CE failures — the venv search depth and the heredoc ban are both documented in `subsystem_creation.md` but not yet reliably followed.

### Key Metric Comparison

| Metric | `v1a` (no readme) | `customs_demo` (with readme) | `customs_app` (reference) |
|---|---|---|---|
| Total rules | 21 | 16 | 16 |
| `Rule.copy` | 1 (duty rate only) | 1 (+1 formula-copy) | 2 |
| `Rule.constraint` | **0** | 3 ✅ | 3 |
| Province design | **3 columns** (`gst_rate`, `pst_rate`, `hst_rate`) | 1 column ✅ | 1 column |
| `CountryOrigin` FK table | **❌** (embedded in HS code rule) | ✅ | ✅ |
| `quantity × unit_price` model | **❌** (`customs_value` is input) | ✅ | ✅ |
| Duty rate field on HS table | ✅ `mfn_duty_rate` present | ✅ `base_duty_rate` present | ✅ |
| `alp_init.py` Flask context seed | ✅ | ✅ | ❌ (outside Flask) |

### Verdict: the readme WAS a ghost for the structural wins in `customs_demo`

Without the readme in context, v1a regresses to near-v3 quality on schema and constraints. The CE alone (Prompt B + v3.8 CE) does NOT produce: single-column province, `CountryOrigin` FK table, `quantity × unit_price` model, or constraints.

What the CE alone **does** reliably produce:
- Header/detail structure (`CustomsEntry → SurtaxLineItem`) ✅ — schema hint works
- Flat rate field on HS code table (`mfn_duty_rate`) ✅ — flat reference table principle works
- `Rule.copy` for duty rate ✅ — `logic_bank_api.md` default works
- `alp_init.py` Flask context for seed data ✅ — seed data CE fix works

**Conclusion:** `customs_demo`'s 16-rule result was powered by the readme's explicit description ("16 declarative rules", "duty", breakdown by type) acting as a ghost — not by the CE alone. The study's v3 conclusion that "there is no CE fix for `base_duty_rate`" was correct. The readme was the confounding variable.

### Bonus finding: domain accuracy correction

v1a identified a factual error in `customs_app` (reference): the reference marks Germany, Japan, and China as `surtax_applicable=True`. PC 2025-0917 is a targeted US retaliatory surtax — only US-origin goods attract the 25% levy. v1a correctly modeled this by embedding country-of-origin into the HS code rules. An interesting case of the AI catching a domain error in the "gold standard" reference.

---

## Validation Test — `customs_demo_v1` (clean context, anti-ghost readme, Mar 1 2026)

Created from `starter.sqlite`. Readme updated with OBX-pattern body blockquote (`> 🤖 AI GENERATION NOTE: ...`) directing AI to CE files. **Copilot confirmed it did not use the readme** — first fully clean-context run using the revised CE (FK integers section, spec=floor, seed data fix).

### Key Metric Comparison

| Metric | `v1` (anti-ghost) | `v1a` (no readme) | `customs_app` (reference) |
|---|---|---|---|
| Total rules | **16** | 21 | 16–17 |
| `Rule.copy` | 2 ✅ | 1 | 2 |
| `Rule.constraint` | 3 ✅ | 0 | 3 |
| `early_row_event + session.query()` | **0** ✅ | — | 0 |
| Province design | **3 columns** (`gst_rate`, `pst_rate`, `hst_rate`) ❌ | 3 columns ❌ | 1 column |
| `CountryOrigin` FK table | ✅ | ❌ | ✅ |
| `to_date()` datetime safety | ❌ | ❌ | ✅ |
| `surtax_applicable` on header | ❌ (per line item) | — | ✅ |
| `entry_date` on header | ❌ | ❌ | ✅ |
| B2B `SubmitEntry` endpoint | ✅ (beyond reference) | ❌ | ❌ |
| Admin UI configured for CBSA tables | ✅ | — | ❌ |
| CETA/CPTPP exemptions correct | ✅ | ✅ | ❌ |
| Seed data uses Flask context | ✅ | ✅ | ❌ |

### What the FK integers CE fix achieved

No `early_row_event + session.query()` anywhere — the primary failure mode of every prior clean-context run is gone. `CountryOrigin` and `ProvinceTaxRate` are proper FK-linked parent tables. `Rule.copy` traverses the FK relationship correctly (2 copies match reference). Rule count (16) matches reference for the first time in a clean-context run.

### What spec=floor achieved

Three clear examples of autonomous domain reasoning beyond the prompt:
- `surtax_rate_override` nullable column on `CountryOrigin` — per-country rate deviation not in the prompt
- CETA/CPTPP exemptions in seed data (Germany=exempt, Japan=exempt) — reference gets this *wrong* (all countries = 25%)
- B2B `SubmitEntry` endpoint + `CustomsEntryMapper` — entirely beyond prompt scope

### Still failing (prompt-level, as study predicted)

**Province 3-column design persists** — `gst_rate`, `pst_rate`, `hst_rate` columns returned again. The phrase "provincial sales tax or HST where applicable" continues to trigger conditional/multi-column design. CE cannot fix this — it requires a prompt-level phrase: `"Province has a single pre-combined tax_rate column (e.g., Ontario=0.13, BC=0.12)"`.

**`country_id` per line item, not on header** — the normalization issue. Province is correctly on the header; country splits per line. Root cause: "country of origin" appears in the same prompt list as "hs codes" (which are correctly per-line), so the AI colocalizes them. Fix: prompt must explicitly assign country to the header — e.g., `"Each CustomsEntry has a single country_origin_id FK on the header"`.

**`to_date()` missing** — persists across every clean run. This is a CE gap, not a prompt issue: prompt authors won't think to specify it. Must be added to `logic_bank_api.md` or `subsystem_creation.md` as a standing rule for date-comparison formulas.

### New finding: anti-ghost readme blockquote works

The OBX-pattern body blockquote (`> 🤖 AI GENERATION NOTE`) successfully prevented readme pollution. Copilot confirmed it did not use the readme — the first clean confirmation that the blockquote technique works. Front matter alone (`Do NOT use`) had failed; the visible body instruction succeeds, consistent with OBX pattern theory (positive instruction in a scanned position > negative instruction in metadata).

### Bonus finding: AI correctly caught reference domain error (confirmed again)

v1a finding confirmed: reference has all countries `surtax_applicable=True` including Germany and Japan. v1 again correctly modeled CETA/CPTPP exemptions. The "gold standard" reference is wrong on this point; the AI is reasoning correctly from domain knowledge with spec=floor active.

---

## Open Items

| Item | Status |
|---|---|
| Validation test — `customs_demo_ce_fix` | ✅ Complete |
| Prompt fix: province phrase + FK schema | ✅ Validated in `customs_demo_v2` |
| Validation test — `customs_demo_v2` | ✅ Complete |
| Add CE principle: "spec = floor not ceiling" | ✅ Added to `subsystem_creation.md` — propagated to org_git, venv, customs_demo_v2/v3 |
| Validation test — `customs_demo_v3` | ✅ Complete — spec=floor works for generic elaboration; domain-specific gaps need prompt fixes |
| Add `base_duty_rate` + `quantity/unit_of_measure/unit_price` to prompt | ✅ Validated in new release (`customs_demo`) — readme was the ghost |
| Validation test — new release (`customs_demo`) | ✅ Complete — 16 rules (readme-assisted); v1a confirms CE alone = ~v3 quality |
| Validation test — `customs_demo_v1a` (clean context) | ✅ Complete — confirms readme was ghost; CE produces header/detail + flat ref table + `Rule.copy` + `alp_init.py`; NOT province/FK/qty×price/constraints |
| Fix seed data instruction in `copilot-instructions.md` | ✅ Fixed — propagated to org_git, venv, customs_demo |
| Anti-ghost readme blockquote (OBX pattern) | ✅ Implemented and confirmed working in `customs_demo_v1` — front matter alone failed; body blockquote succeeds |
| Validation test — `customs_demo_v1` (anti-ghost, Mar 1 2026) | ✅ Complete — FK integers fix eliminates `early_row_event`; spec=floor produces beyond-prompt domain reasoning; 16 rules matches reference; province 3-column + `to_date()` + country-on-header remain |
| Venv search depth — grandparent shared venv not found reliably | ⏳ CE fix needed in `copilot-instructions.md` |
| `Float` → `Numeric`/`DECIMAL` for financial columns (CE or prompt default) | ✅ Added to `subsystem_creation.md` — `Numeric(15,2)` for amounts, `Numeric(8,6)`/`Numeric(7,4)` for rates; propagated to org_git, venv, customs_demo_v1 |
| `to_date()` datetime safety — missing in all clean runs | ⏳ CE fix needed in `logic_bank_api.md` or `subsystem_creation.md`: "normalize date columns before comparison" |
| Province prompt fix: single `tax_rate` phrase | ⏳ v2 prompt — add: `"Province has a single pre-combined tax_rate column"` |
| Country-on-header prompt fix: `country_origin_id` on `CustomsEntry` | ⏳ v2 prompt — add: `"Each CustomsEntry has a single country_origin_id FK on the header"` |
| `surtax_applicable` placement: line item → order header | ⏳ Follows from country-on-header fix; 3NF issue resolves when country is on header |
| `basic_demo_ai_rules-supplier` in org_git — old `logic_bank_api.md` | ⏳ Low priority; auto-corrects on next BLT |
| Ghost of `basic_demo` — make patterns explicit | ✅ Created `docs/training/sample_app.md` — explicit few-shot reference for all 5 rule patterns with canonical Customer/Order/Item/Product examples + domain translation table; propagated to org_git, venv |
