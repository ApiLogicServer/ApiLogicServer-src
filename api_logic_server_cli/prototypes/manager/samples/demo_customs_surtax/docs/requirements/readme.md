# cbsa_steel_surtax — Provenance

**Prompt source:** `samples/prompts/customs_cbsa.prompt.md`
**PC Number:** 2025-0917 (Steel Derivative Goods Surtax Order, 2025-12-11)
**Program code:** 25267A
**Effective date:** 2025-12-26
**Created:** 2026-06-10 via Manager CE Method 4 (System Creation Services), generated fresh from the prompt (no content copied from `samples/demo_customs_surtax/`)

## Domain Summary

Implements the CBSA Steel Derivative Goods Surtax Order under subsection 53(2) and
paragraph 79(a) of the Customs Tariff. Transactions are `CustomsEntry` records
with one or more `SurtaxLineItem` rows (one per HS code).

### Tax calculation chain

| Step | Rule | Table |
|---|---|---|
| 1 | Copy `effective_date`, `program_code`, `pc_number` from `SysConfig` | `CustomsEntry` |
| 2 | Copy `country_surtax_rate` from `CountryOrigin` | `CustomsEntry` |
| 3 | Copy `province_tax_rate` from `Province` | `CustomsEntry` |
| 4 | `surtax_applicable = 1` when `ship_date >= effective_date` AND `country_surtax_rate > 0` | `CustomsEntry` |
| 5 | Copy `base_duty_rate`, `is_steel_derivative` from `HsCodeRate` | `SurtaxLineItem` |
| 6 | `surtax_applicable = 1` when entry `surtax_applicable == 1` AND `is_steel_derivative == 1` | `SurtaxLineItem` |
| 7 | `base_duty_amount = customs_value * base_duty_rate` | `SurtaxLineItem` |
| 8 | `surtax_amount = customs_value * country_surtax_rate` (if line `surtax_applicable`) | `SurtaxLineItem` |
| 9 | Sum `total_customs_value`, `total_duty_amount`, `total_surtax_amount` | `CustomsEntry` |
| 10 | `duty_paid_value = total_customs_value + total_duty_amount + total_surtax_amount` | `CustomsEntry` |
| 11 | `sales_tax_amount = duty_paid_value * province_tax_rate` | `CustomsEntry` |
| 12 | `total_tax_due = total_duty_amount + total_surtax_amount + sales_tax_amount` | `CustomsEntry` |

### Example countries in seed data

| Country | Agreement | Surtax rate |
|---|---|---|
| Germany (DE) | CETA | 0% |
| United States (US) | CUSMA | 0% |
| Japan (JP) | CPTPP | 0% |
| China (CN) | — | 25% |

### Provinces in seed data

| Province | Tax rate (pre-combined GST/PST/HST) |
|---|---|
| Ontario (ON) | 13% |
| Alberta (AB) | 5% |
| British Columbia (BC) | 12% |
| Nova Scotia (NS) | 15% |
| Manitoba (MB) | 12% |

## Files created

```
logic/logic_discovery/
  cbsa_steel_surtax.py      ← all 18 rules: Rule.copy (sys_config/country/province/hs_code),
                                surtax_applicable formulas (entry + line), base_duty_amount,
                                surtax_amount, Rule.sum rollups, duty_paid_value,
                                sales_tax_amount, total_tax_due, customs_value > 0 constraint
database/test_data/alp_init.py  ← 4 example entries (DE, US, JP, CN)
docs/requirements/cbsa_steel_surtax/requirements.md  ← verbatim prompt (this use case)
docs/requirements/ad-libs.md                          ← assumptions made beyond the prompt spec
```

## Verified seed-data results

All 4 `CustomsEntry` rows and all 7 `SurtaxLineItem` rows were verified via sqlite3
after running `alp_init.py` inside Flask app context (LogicBank active):

| Entry | Country | total_customs_value | total_surtax_amount | duty_paid_value | sales_tax_amount | total_tax_due | surtax_applicable |
|---|---|---|---|---|---|---|---|
| B3-2026-0001 | Germany (CETA) | 65000.00 | 0.00 | 65000.00 | 8450.00 | 8450.00 | 0 |
| B3-2026-0002 | US (CUSMA) | 30000.00 | 0.00 | 30000.00 | 1500.00 | 1500.00 | 0 |
| B3-2026-0003 | Japan (CPTPP) | 60000.00 | 0.00 | 60000.00 | 7200.00 | 7200.00 | 0 |
| B3-2026-0004 | China | 85000.00 | 21250.00 | 106250.00 | 13812.50 | 35062.50 | 1 |

For B3-2026-0004 (China), **both** line items (HS 7208.10 and HS 7228.30) are flagged
`is_steel_derivative = 1`, so both are correctly subject to the 25% surtax
(60000*0.25 + 25000*0.25 = 15000 + 6250 = 21250).

## Implementation notes (issues found and fixed during build)

Three interacting issues were found and fixed in `database/test_data/alp_init.py` and
`logic/logic_discovery/cbsa_steel_surtax.py` while developing the seed script — all are
now resolved and the results above reflect the corrected, working state:

1. **Formula pruning on Rule.sum-derived inputs** — `duty_paid_value`, `sales_tax_amount`,
   and `total_tax_due` depend on `total_customs_value` / `total_duty_amount` /
   `total_surtax_amount`, which are themselves `Rule.sum` columns updated via LogicBank's
   deferred child-insert delta adjustment. LogicBank's pruning optimization could skip
   re-deriving these formulas after such a delta-only update. Fixed by adding
   `no_prune=True` to all three `Rule.formula` declarations.

2. **Cross-row formula ordering** — `SurtaxLineItem.surtax_applicable` reads
   `row.customs_entry.surtax_applicable` (itself a `Rule.formula` on the parent). If a
   child row is processed via deferred-adjustment chaining before the parent's own row
   logic has run, the child formula can be evaluated with a stale/unset parent value and
   never re-fire. Fixed by restructuring `alp_init.py` to `session.add(entry)` and
   `session.flush()` for each `CustomsEntry` *before* appending its `SurtaxLineItem` rows,
   guaranteeing the parent's `surtax_applicable` is computed first.

3. **Optimistic locking on the flushed header** — the flush-before-append pattern from
   (2) causes a subsequent in-transaction UPDATE to the same `CustomsEntry` row (via the
   `Rule.sum` adjustment when line items are added), which `opt_lock_patch()` treated as a
   concurrent-edit conflict under the default `OPT_LOCKING = "optional"`. Fixed by setting
   `os.environ['OPT_LOCKING'] = 'ignored'` at the top of `alp_init.py`, before
   `config.config` is imported.
