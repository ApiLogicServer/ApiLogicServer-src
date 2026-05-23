"""
Logic discovery: Shipment matching (Phase 2).

On Shipment insert, look up the matching Customer using:
    Shipment.trprt_bill_to_acct_nbr == Customer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row, matching high confidence columns
from Customer to ShipmentParty.
Use Rule.row_event (not early_row_event) — fires before_flush so the new
ShipmentParty writes atomically with the parent Shipment.
"""
import logging
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

app_logger = logging.getLogger("api_logic_server_app")


def _match_importer(row: models.Shipment, old_row: models.Shipment, logic_row: LogicRow):
    """On Shipment insert, look up matching Customer and create an Importer ShipmentParty."""
    if not logic_row.is_inserted():
        return
    if not row.trprt_bill_to_acct_nbr:
        return

    session = logic_row.session
    with session.no_autoflush:
        customer = (
            session.query(models.Customer)
            .filter(models.Customer.duty_bill_to_acct_nbr == row.trprt_bill_to_acct_nbr)
            .first()
        )
    if customer is None:
        app_logger.warning(
            f"shipment_matching: no Customer found for trprt_bill_to_acct_nbr={row.trprt_bill_to_acct_nbr}"
        )
        return

    importer = models.ShipmentParty()
    importer.shipment_party_type_cd = "I"
    importer.company_nm = customer.name
    importer.city_nm = customer.city
    importer.state_cd = customer.state
    importer.country_cd = customer.country
    importer.postal_cd = customer.postal
    importer.customs_id_cd = customer.business_nbr
    importer.broker_id_cd = customer.broker_cd
    importer.customer_acct_nbr = customer.duty_bill_to_acct_nbr

    row.ShipmentPartyList.append(importer)
    logic_row.log(f"shipment_matching: created Importer ShipmentParty for customer={customer.name}")


def declare_logic():
    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
