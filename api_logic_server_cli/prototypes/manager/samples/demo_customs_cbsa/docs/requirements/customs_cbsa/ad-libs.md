# Ad-Libs Report — customs_cbsa

**Implementation review against `samples/prompts/customs_cbsa.prompt.md` (PC 2025-0917 / Program 25267A)**  
**Date:** 2026-05-10

**1 item needs your review. 4 FYIs — standard patterns, no action needed.**

---

## 🔴 Review Required

| Location | Issue | Fix |
|---|---|---|
| [alp_init.py](../../database/test_data/alp_init.py) | HS base duty rates guessed: structural steel codes (7301, 7302, 7304, 7306, 7308) seeded at 0%, roller chains (7315) at 5.5%. These are AI estimates, not verified MFN rates. | Look up actual MFN rates in the [Canada Customs Tariff](https://www.cbsa-asfc.gc.ca/trade-commerce/tariff-tarif/2025/html/tblmod-1-eng.html) and update `HsCodeRate` rows via the Admin UI or re-run seed. |

---

## 🟡 FYI

- **[lookup_values.py](../../logic/logic_discovery/cbsa_surtax/lookup_values.py)** — `Rule.copy` used for all parent-value rules (SysConfig→Entry, CountryOrigin→Entry, Province→Entry, HsCodeRate→Line, Entry→Line). Values frozen at transaction time — correct for regulatory audit purposes.

- **[entry_totals.py](../../logic/logic_discovery/cbsa_surtax/entry_totals.py)** — `total_tax_due` expressed as `duty_paid_value - total_customs_value + sales_tax_amount` rather than a direct sum of duty columns. This avoids a LogicBank sum-column prune ordering issue where `total_tax_due` would fire before `total_surtax_amount` was updated.

- **[models.py](../../database/models.py)** — `Province.tax_rate` uses a single pre-combined rate (e.g., Ontario 0.13 = HST, BC 0.12 = GST+PST). The prompt phrase "provincial sales tax or HST where applicable" describes rate variation — not an instruction to split into separate GST/PST columns. Standard approach per subsystem_creation.md.

- **[entry_totals.py](../../logic/logic_discovery/cbsa_surtax/entry_totals.py)** — `surtax_applicable` is a working value on `CustomsEntry` (not per line). Entry-level gate is correct when all line items share the same country of origin. If mixed-origin entries are ever needed, this flag would need to move to the line level.
