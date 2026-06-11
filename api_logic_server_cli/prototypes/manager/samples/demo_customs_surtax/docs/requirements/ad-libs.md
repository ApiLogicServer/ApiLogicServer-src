# Ad-Libs Report — cbsa_steel_surtax

**Implementation review against `samples/prompts/customs_cbsa.prompt.md` (PC 2025-0917 / Program 25267A)**
**Date:** 2026-06-10

**1 item needs your review. 6 FYIs — standard patterns, no action needed.**

---

## 🔴 Review Required

| Location | Issue | Fix |
|---|---|---|
| [alp_init.py](../../database/test_data/alp_init.py) / `HsCodeRate` seed rows | HS `base_duty_rate` guessed at 0% for all six steel-derivative codes (7208.10, 7213.10, 7216.10, 7228.30, 7301.10, 7306.30). The prompt does not specify MFN duty rates for these codes. | Look up actual MFN rates in the [Canada Customs Tariff](https://www.cbsa-asfc.gc.ca/trade-commerce/tariff-tarif/2025/html/tblmod-1-eng.html) and update `HsCodeRate.base_duty_rate` via the Admin UI or re-run seed. |

---

## 🟡 FYI

- **[alp_init.py](../../database/test_data/alp_init.py) / `Province` seed rows** — Seeded 5 representative provinces (ON 13%, AB 5%, BC 12%, NS 15%, MB 12%) with single pre-combined GST/PST/HST rates. The prompt says "provincial sales tax or HST where applicable" — interpreted as rate variation by province, not a request to enumerate all 13 provinces/territories or split into separate GST/PST columns. Add more `Province` rows via the Admin UI as needed.

- **[models.py](../../database/models.py) / `SysConfig`** — Added descriptive audit columns (`order_title`, `order_date`, `legal_authority`, `pc_number`, `program_code`) beyond the bare `effective_date`/rate columns strictly needed by the formulas, so the regulatory citation (PC 2025-0917, program 25267A, subsection 53(2)/paragraph 79(a)) is visible in the Admin UI and copyable onto each `CustomsEntry`.

- **[cbsa_steel_surtax.py](../../logic/logic_discovery/cbsa_steel_surtax.py)** — `Rule.copy` used for all parent-value rules (`SysConfig`→Entry, `CountryOrigin`→Entry, `Province`→Entry, `HsCodeRate`→Line). Values are frozen at transaction time — correct for regulatory audit (a later change to a country's surtax rate or a province's tax rate does not retroactively alter past entries).

- **[cbsa_steel_surtax.py](../../logic/logic_discovery/cbsa_steel_surtax.py)** — `surtax_applicable` is computed once at the `CustomsEntry` (header) level, then copied down as a gating condition for each `SurtaxLineItem`. This is correct because `CustomsEntry` has a single `country_origin_id` and `ship_date` — all line items on one entry share the same country of origin and ship date, so the entry-level gate applies uniformly.

- **[cbsa_steel_surtax.py](../../logic/logic_discovery/cbsa_steel_surtax.py)** — `duty_paid_value`, `sales_tax_amount`, and `total_tax_due` use `no_prune=True`. These three formulas depend on `Rule.sum`-derived columns (`total_customs_value`, `total_duty_amount`, `total_surtax_amount`) that are updated via LogicBank's deferred child-insert delta adjustment; without `no_prune=True` the re-derivation could be skipped after such an adjustment-only update.

- **[alp_init.py](../../database/test_data/alp_init.py)** — All 4 seed `ship_date` values (2026-01-10 through 2026-02-01) are on/after `effective_date` (2025-12-26), so the date-gating condition in `surtax_applicable` is always "in effect" for seed data; only each entry's `country_surtax_rate` (0% vs 25%) determines whether surtax actually applies. A pre-effective-date example was not included since the prompt's four named examples (Germany, US, Japan, China) don't call for one.

- **[alp_init.py](../../database/test_data/alp_init.py)** — `os.environ['OPT_LOCKING'] = 'ignored'` is set at the top of the seed script (before `config.config` import) because the seed script flushes each `CustomsEntry` header before appending its line items (so the header's `surtax_applicable` formula resolves before child rows reference it), and the subsequent `Rule.sum` adjustment to that same header row would otherwise be flagged as a concurrent-edit conflict by `opt_lock_patch()`. This setting only affects the seed script's own session, not the running API/Admin UI.
