# customs_cbsa — Provenance

**Prompt source:** `samples/prompts/customs_cbsa.prompt.md`  
**PC Number:** 2025-0917 (Steel Derivative Goods Surtax Order, 2025-12-11)  
**Program code:** 25267A  
**Effective date:** 2025-12-26  
**Created:** 2026-05-10 via Manager CE Method 4 (System Creation Services)

## Domain Summary

Implements CBSA Steel Derivative Goods Surtax Order under subsection 53(2) and
paragraph 79(a) of the Customs Tariff.  Transactions are `CustomsEntry` records
with one or more `SurtaxLineItem` rows (one per HS code).

### Tax calculation chain

| Step | Rule | Table |
|---|---|---|
| 1 | Copy `effective_date`, `program_code`, `pc_number` from `SysConfig` | `CustomsEntry` |
| 2 | Copy `country_surtax_rate` from `CountryOrigin` | `CustomsEntry` |
| 3 | Copy `province_tax_rate` from `Province` | `CustomsEntry` |
| 4 | `surtax_applicable = 1` when `ship_date >= effective_date` | `CustomsEntry` |
| 5 | Copy `base_duty_rate` from `HsCodeRate` | `SurtaxLineItem` |
| 6 | Copy `country_surtax_rate`, `surtax_applicable` from `CustomsEntry` | `SurtaxLineItem` |
| 7 | `base_duty_amount = customs_value × base_duty_rate` | `SurtaxLineItem` |
| 8 | `surtax_amount = customs_value × country_surtax_rate` (if applicable) | `SurtaxLineItem` |
| 9 | Sum `total_customs_value`, `total_duty_amount`, `total_surtax_amount` | `CustomsEntry` |
| 10 | `duty_paid_value = customs + duty + surtax` | `CustomsEntry` |
| 11 | `sales_tax_amount = duty_paid_value × province_tax_rate` | `CustomsEntry` |
| 12 | `total_tax_due = duty + surtax + sales_tax` | `CustomsEntry` |

### Example countries in seed data

| Country | Agreement | Surtax rate |
|---|---|---|
| Germany (DE) | CETA | 0% |
| United States (US) | CUSMA | 0% |
| Japan (JP) | CPTPP | 0% |
| China (CN) | — | 25% |
| United Kingdom (GB) | — | 25% |

## Files created

```
logic/logic_discovery/cbsa_surtax/
  __init__.py
  lookup_values.py    ← Rule.copy chains (SysConfig, CountryOrigin, Province, HsCodeRate → entry/line)
  line_amounts.py     ← surtax_applicable, base_duty_amount, surtax_amount
  entry_totals.py     ← Rule.sum aggregates + duty_paid_value, sales_tax_amount, total_tax_due
  validation.py       ← constraints (customs_value > 0, ship_date required)
database/test_data/alp_init.py   ← 5 example entries (DE, US, JP, CN, US-pre-effective)
```
