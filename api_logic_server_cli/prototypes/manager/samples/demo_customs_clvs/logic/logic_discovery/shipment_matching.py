"""
Feature: Importer matching

Logic discovery: Shipment matching (Phase 2).

Create `logic/logic_discovery/shipment_matching.py`.

On Shipment insert, look up the matching Customer using:
    Shipment.trprt_bill_to_acct_nbr == Customer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row, matching high confidence columns
from Customer to ShipmentParty.
Use Rule.row_event (not early_row_event) — fires before_flush so the new
ShipmentParty writes atomically with the parent Shipment.

version: 1.0
created: 2026-11-01
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
"""
from logic_bank.logic_bank import Rule
from database import models


def _match_importer(row: models.Shipment, old_row, logic_row):
    """Shipment event: on insert, finds the Customer whose duty_bill_to_acct_nbr equals the shipment's
    trprt_bill_to_acct_nbr and adds an importer ShipmentParty (type I) copied from it; logs a warning if none matches."""
    if not logic_row.is_inserted():
        return
    account = row.trprt_bill_to_acct_nbr
    customer = None
    if account is not None:
        customer = (logic_row.session.query(models.Customer)
                    .filter(models.Customer.duty_bill_to_acct_nbr == account).first())
    if customer is None:
        logic_row.log(f"_match_importer: WARNING no Customer with duty_bill_to_acct_nbr = {account}")
        return
    importer = models.ShipmentParty(shipment_party_type_cd="I", company_nm=customer.name, city_nm=customer.city,
                                    state_cd=customer.state, postal_cd=customer.postal, country_cd=customer.country,
                                    customer_acct_nbr=customer.duty_bill_to_acct_nbr,
                                    contact_phone_nbr=customer.phone_nbr, business_nbr=customer.business_nbr,
                                    broker_id_cd=customer.broker_cd)
    row.ShipmentPartyList.append(importer)


def declare_logic():
    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
