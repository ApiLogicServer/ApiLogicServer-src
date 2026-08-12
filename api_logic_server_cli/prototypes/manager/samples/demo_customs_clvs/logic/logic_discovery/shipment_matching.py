"""
Logic discovery: Shipment matching (Phase 2).

Create `logic/logic_discovery/shipment_matching.py`.

On Shipment insert, look up the matching Customer using:
    Shipment.trprt_bill_to_acct_nbr == Customer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row, matching high confidence columns
from Customer to ShipmentParty.
Use Rule.row_event (not early_row_event) — fires before_flush so the new
ShipmentParty writes atomically with the parent Shipment.
"""
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _match_importer(row: models.Shipment, old_row, logic_row: LogicRow):
    """Shipment event: looks up Customer by trprt_bill_to_acct_nbr == duty_bill_to_acct_nbr
    and creates an importer ShipmentParty row (shipment_party_type_cd='I') when matched."""
    if not logic_row.is_inserted():
        return
    customer = logic_row.session.query(models.Customer).filter(
        models.Customer.duty_bill_to_acct_nbr == row.trprt_bill_to_acct_nbr).first()
    if customer is None:
        logic_row.log(f"shipment_matching: no Customer found for trprt_bill_to_acct_nbr={row.trprt_bill_to_acct_nbr}")
        return
    importer_party = models.ShipmentParty(
        shipment_party_type_cd="I",
        company_nm=customer.name,
        city_nm=customer.city,
        state_cd=customer.state,
        country_cd=customer.country,
        postal_cd=customer.postal,
        customer_acct_nbr=customer.duty_bill_to_acct_nbr,
        business_nbr=customer.business_nbr,
    )
    row.ShipmentPartyList.append(importer_party)
    logic_row.log(f"shipment_matching: matched Customer {customer.name} -> importer ShipmentParty")


def declare_logic():
    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
