"""
On Shipment insert, look up the matching Customer using:
    Shipment.trprt_bill_to_acct_nbr == Customer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row with shipment_party_type_cd="I" (importer).
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _match_importer(row: models.Shipment, old_row: models.Shipment, logic_row: LogicRow):
    if not logic_row.is_inserted():
        return
    # Extract to local variable before session.query to avoid LB scanner confusion
    trprt_acct = row.trprt_bill_to_acct_nbr
    if not trprt_acct:
        return
    session = logic_row.session
    customer = session.query(models.Customer).filter(
        models.Customer.duty_bill_to_acct_nbr == trprt_acct
    ).first()
    if customer is None:
        logic_row.log(f"shipment_matching: no customer for trprt_bill_to_acct_nbr={trprt_acct}")
        return
    party = models.ShipmentParty()
    party.shipment_party_type_cd = 'I'
    party.company_nm = customer.name
    party.country_cd = customer.country
    party.customer_acct_nbr = customer.customeroid
    party.business_nbr = customer.business_nbr
    row.ShipmentPartyList.append(party)
    logic_row.log(f"shipment_matching: created importer party for customer={customer.name}")


def declare_logic():
    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
