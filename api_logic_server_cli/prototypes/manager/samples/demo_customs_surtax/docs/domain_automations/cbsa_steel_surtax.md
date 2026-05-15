# CBSA Steel Derivative Goods Surtax

**Created:** 2026-05-10
**Tables:** CountryOrigin, Province, HsCodeRate, SysConfig (extended), CustomsEntry, SurtaxLineItem
**Rules:** 22 rules: 5 copy (entry header), 3 copy (line item), 1 formula (surtax_applicable), 2 formula (line amounts), 3 sum (entry aggregates), 3 formula (entry totals), 2 constraint

## Prompt

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

## Notes

- CountryOrigin.surtax_rate is a DECIMAL multiplier (0.0=exempt, 0.25=full surtax)
- Germany (CETA) and Japan (CPTPP) seeded with surtax_rate=0.0; US and China with 0.25
- Province uses single pre-combined tax_rate column: ON=0.13 (HST), BC=0.12 (GST+PST), AB=0.05, QC=0.1498
- SysConfig carries effective_date='2025-12-26', program_code='25267A', pc_number='2025-0917'; copied to CustomsEntry header
- surtax_applicable formula: ship_date >= effective_date (ISO string comparison works correctly)
- total_tax_due formula avoids sum-column prune: expressed as duty_paid_value - total_customs_value + sales_tax_amount
- Pre-surtax example (CBSA-2025-005, ship_date=2025-12-20): surtax_applicable=0, surtax_amount=0 on all lines
- HsCodeRate 7315.11 (roller chains) has base_duty_rate=5.5%; all steel structural codes are 0% MFN
