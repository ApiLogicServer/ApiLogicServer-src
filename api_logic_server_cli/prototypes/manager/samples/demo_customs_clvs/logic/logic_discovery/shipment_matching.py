"""
Shipment Importer Matching (Step 2):
On Shipment insert, match the importer Customer by duty_bill_to_acct_nbr
and create a ShipmentParty(type_cd='I') from the Customer record.
"""
import logging
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

app_logger = logging.getLogger("api_logic_server_app")


def _match_importer(row: models.Shipment, old_row: models.Shipment, logic_row: LogicRow):
    if not logic_row.is_inserted():
        return
    if not row.trprt_bill_to_acct_nbr:
        return

    session = logic_row.session
    customer = session.query(models.Customer).filter(
        models.Customer.duty_bill_to_acct_nbr == row.trprt_bill_to_acct_nbr
    ).first()

    if customer is None:
        logic_row.log(f"shipment_matching: no Customer match for trprt_bill_to_acct_nbr={row.trprt_bill_to_acct_nbr}")
        return

    logic_row.log(f"shipment_matching: matched Customer id={customer.id} name={customer.name}")

    party = models.ShipmentParty()
    party.local_shipment_oid_nbr = row.local_shipment_oid_nbr
    party.shipment_party_type_cd = 'I'  # Importer
    party.company_nm = customer.name
    party.city_nm = customer.city
    party.state_cd = customer.state
    party.country_cd = customer.country
    party.postal_cd = customer.postal
    party.customs_id_cd = customer.business_nbr
    party.customer_acct_nbr = customer.duty_bill_to_acct_nbr
    row.ShipmentPartyList.append(party)


def declare_logic():
    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
