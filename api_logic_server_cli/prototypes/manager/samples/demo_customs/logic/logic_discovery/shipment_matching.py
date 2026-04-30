"""
Logic discovery: Shipment matching (Phase 2).

On Shipment insert, look up the matching CcpCustomer using:
    Shipment.trprt_bill_to_acct_nbr == CcpCustomer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row, matching high confidence columns
from CcpCustomer to ShipmentParty.
Use Rule.row_event (not early_row_event) — fires before_flush so the new
ShipmentParty writes atomically with the parent Shipment.
"""

import logging

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

app_logger = logging.getLogger("api_logic_server_app")


def _match_importer(row: models.Shipment, old_row, logic_row: LogicRow):
    if not logic_row.is_inserted():
        return
    if not row.trprt_bill_to_acct_nbr:
        return

    session = logic_row.session
    ccp = (
        session.query(models.CcpCustomer)
        .filter(models.CcpCustomer.duty_bill_to_acct_nbr == row.trprt_bill_to_acct_nbr)
        .first()
    )
    if ccp is None:
        app_logger.warning(
            f"shipment_matching: no CcpCustomer match for trprt_bill_to_acct_nbr={row.trprt_bill_to_acct_nbr}"
        )
        return

    party = models.ShipmentParty()
    party.shipment_party_type_cd = "I"   # Importer
    party.company_nm             = ccp.name
    party.city_nm                = ccp.city
    party.state_cd               = ccp.state
    party.country_cd             = ccp.country
    party.postal_cd              = ccp.postal
    party.contact_phone_nbr      = ccp.phone_nbr
    party.customs_id_cd          = ccp.business_nbr
    party.customer_acct_nbr      = ccp.duty_bill_to_acct_nbr
    party.broker_id_cd           = ccp.broker_cd

    row.ShipmentPartyList.append(party)
    logic_row.log(f"shipment_matching: matched CcpCustomer id={ccp.id} → ShipmentParty type=I")


def declare_logic():
    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
