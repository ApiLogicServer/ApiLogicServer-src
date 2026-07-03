# Logic Flow — samples/demo_customs_surtax

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram.svg)

</td>
<td width="35%">

### Rules

1. `effective_date = copy(effective_date)`<br>
2. `program_code = copy(program_code)`<br>
3. `pc_number = copy(pc_number)`<br>
4. `country_surtax_rate = copy(surtax_rate)`<br>
5. `province_tax_rate = copy(tax_rate)`<br>
6. `base_duty_rate = copy(base_duty_rate)`<br>
7. `is_steel_derivative = copy(is_steel_derivative)`<br>
8. `surtax_applicable = 1 if (ship_date is not None<br>
                            and effective_date is not None<br>
                            and ship_date >= effective_date<br>
                            and (country_surtax_rate or 0) > 0)<br>
                      else 0`<br>
9. `duty_paid_value = (total_customs_value or 0)<br>
                      + (total_duty_amount or 0)<br>
                      + (total_surtax_amount or 0)`<br>
10. `sales_tax_amount = (duty_paid_value or 0) * (province_tax_rate or 0)`<br>
11. `total_tax_due = (total_duty_amount or 0)<br>
                      + (total_surtax_amount or 0)<br>
                      + (sales_tax_amount or 0)`<br>
12. `surtax_applicable = 1 if (customs_entry.surtax_applicable == 1<br>
                            and is_steel_derivative == 1)<br>
                      else 0`<br>
13. `base_duty_amount = (customs_value or 0) * (base_duty_rate or 0)`<br>
14. `surtax_amount = (customs_value or 0) * (customs_entry.country_surtax_rate or 0)<br>
                      if surtax_applicable == 1<br>
                      else 0`<br>
15. `total_customs_value = sum(customs_value)`<br>
16. `total_duty_amount = sum(base_duty_amount)`<br>
17. `total_surtax_amount = sum(surtax_amount)`<br>
C. constraint: `SurtaxLineItem`

</td>
</tr>
</table>

---
_Generated 2026-07-03 07:39_
