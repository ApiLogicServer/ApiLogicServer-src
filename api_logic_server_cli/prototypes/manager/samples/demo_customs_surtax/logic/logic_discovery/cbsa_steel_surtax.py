from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """
    CBSA Steel Derivative Goods Surtax Order (PC Number 2025-0917, program code 25267A)

    A CustomsEntry (header) carries country of origin, province, and ship date.
    Each SurtaxLineItem (detail) carries an HS code and customs value.

    - Surtax (decimal multiplier, e.g. 0.25 = 25%) applies only when:
        * the entry's ship_date is on/after the order's effective_date, AND
        * the country of origin is "subject" (surtax_rate > 0 -- CETA/CUSMA/CPTPP
          partners are modelled with surtax_rate = 0.0), AND
        * the line item's HS code is in the steel-derivative schedule
    - Provincial sales tax (single pre-combined rate, e.g. 0.13 = 13% HST) applies
      to the duty-paid value (customs value + duty + surtax).
    """

    # --- CustomsEntry: copy regulatory constants from SysConfig (sys_config_id, server_default 1) ---
    Rule.copy(derive=models.CustomsEntry.effective_date, from_parent=models.SysConfig.effective_date)
    Rule.copy(derive=models.CustomsEntry.program_code, from_parent=models.SysConfig.program_code)
    Rule.copy(derive=models.CustomsEntry.pc_number, from_parent=models.SysConfig.pc_number)

    # --- CustomsEntry: copy rates from lookup tables (snapshot at entry time) ---
    Rule.copy(derive=models.CustomsEntry.country_surtax_rate, from_parent=models.CountryOrigin.surtax_rate)
    Rule.copy(derive=models.CustomsEntry.province_tax_rate, from_parent=models.Province.tax_rate)

    # --- CustomsEntry: is the order's surtax in effect for this entry? ---
    Rule.formula(derive=models.CustomsEntry.surtax_applicable,
                  as_expression=lambda row:
                      1 if (row.ship_date is not None
                            and row.effective_date is not None
                            and row.ship_date >= row.effective_date
                            and (row.country_surtax_rate or 0) > 0)
                      else 0)

    # --- CustomsEntry: rollups from SurtaxLineItem ---
    Rule.sum(derive=models.CustomsEntry.total_customs_value, as_sum_of=models.SurtaxLineItem.customs_value)
    Rule.sum(derive=models.CustomsEntry.total_duty_amount, as_sum_of=models.SurtaxLineItem.base_duty_amount)
    Rule.sum(derive=models.CustomsEntry.total_surtax_amount, as_sum_of=models.SurtaxLineItem.surtax_amount)

    # --- CustomsEntry: duty-paid value (base for provincial sales tax) ---
    # no_prune: depends on Rule.sum columns adjusted via child-insert delta,
    # which LogicBank's pruning would otherwise skip re-deriving from
    Rule.formula(derive=models.CustomsEntry.duty_paid_value,
                  as_expression=lambda row:
                      (row.total_customs_value or 0)
                      + (row.total_duty_amount or 0)
                      + (row.total_surtax_amount or 0),
                  no_prune=True)

    # --- CustomsEntry: provincial sales tax (single pre-combined GST/PST/HST rate) ---
    Rule.formula(derive=models.CustomsEntry.sales_tax_amount,
                  as_expression=lambda row: (row.duty_paid_value or 0) * (row.province_tax_rate or 0),
                  no_prune=True)

    # --- CustomsEntry: total amount owing ---
    Rule.formula(derive=models.CustomsEntry.total_tax_due,
                  as_expression=lambda row:
                      (row.total_duty_amount or 0)
                      + (row.total_surtax_amount or 0)
                      + (row.sales_tax_amount or 0),
                  no_prune=True)

    # --- SurtaxLineItem: copy HS code's tariff schedule attributes ---
    Rule.copy(derive=models.SurtaxLineItem.base_duty_rate, from_parent=models.HsCodeRate.base_duty_rate)
    Rule.copy(derive=models.SurtaxLineItem.is_steel_derivative, from_parent=models.HsCodeRate.is_steel_derivative)

    # --- SurtaxLineItem: surtax applies to this line only if the entry is
    #     surtax-applicable AND this HS code is in the steel-derivative schedule ---
    Rule.formula(derive=models.SurtaxLineItem.surtax_applicable,
                  as_expression=lambda row:
                      1 if (row.customs_entry.surtax_applicable == 1
                            and row.is_steel_derivative == 1)
                      else 0)

    # --- SurtaxLineItem: base (MFN) duty ---
    Rule.formula(derive=models.SurtaxLineItem.base_duty_amount,
                  as_expression=lambda row: (row.customs_value or 0) * (row.base_duty_rate or 0))

    # --- SurtaxLineItem: surtax (live reference to entry's country_surtax_rate) ---
    Rule.formula(derive=models.SurtaxLineItem.surtax_amount,
                  as_expression=lambda row:
                      (row.customs_value or 0) * (row.customs_entry.country_surtax_rate or 0)
                      if row.surtax_applicable == 1
                      else 0)

    # --- SurtaxLineItem: domain-standard guard against non-positive customs values ---
    Rule.constraint(validate=models.SurtaxLineItem,
                     as_condition=lambda row: row.customs_value > 0,
                     error_msg="Customs value ({row.customs_value}) must be greater than zero")
