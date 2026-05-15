"""
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order
 under subsection 53(2) and paragraph 79(a) of the
 Customs Tariff program code 25267A to calculate duties and taxes
 including provincial sales tax or HST where applicable when
 hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26'
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    # TODO: Review parent-value rules below.
    #   Rule.copy  = snapshot (value frozen at transaction time, no cascade on parent change) ← default
    #   Rule.formula referencing row.parent.attr = live (re-derives if parent changes)
    #   Change Rule.copy → Rule.formula where live propagation is required.

    # SysConfig constants → CustomsEntry header
    Rule.copy(derive=models.CustomsEntry.effective_date, from_parent=models.SysConfig.effective_date)
    Rule.copy(derive=models.CustomsEntry.program_code,   from_parent=models.SysConfig.program_code)
    Rule.copy(derive=models.CustomsEntry.pc_number,      from_parent=models.SysConfig.pc_number)

    # CountryOrigin rate → CustomsEntry
    Rule.copy(derive=models.CustomsEntry.country_surtax_rate, from_parent=models.CountryOrigin.surtax_rate)

    # Province combined tax rate → CustomsEntry
    Rule.copy(derive=models.CustomsEntry.province_tax_rate, from_parent=models.Province.tax_rate)

    # HsCodeRate base duty rate → SurtaxLineItem
    Rule.copy(derive=models.SurtaxLineItem.base_duty_rate, from_parent=models.HsCodeRate.base_duty_rate)

    # CustomsEntry surtax context → SurtaxLineItem (frozen at line creation)
    Rule.copy(derive=models.SurtaxLineItem.country_surtax_rate, from_parent=models.CustomsEntry.country_surtax_rate)
    Rule.copy(derive=models.SurtaxLineItem.surtax_applicable,   from_parent=models.CustomsEntry.surtax_applicable)
