from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

import logging
logger = logging.getLogger('api_logic_server_app')


def _match_importer(row: models.Shipment, old_row, logic_row: LogicRow):
    """
    On Shipment insert: look up matching CcpCustomer by duty_bill_to_acct_nbr.
    If found, create a ShipmentParty row (type "I" = Importer) and attach it.
    """
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
        logger.warning(
            f"shipment_matching: no CcpCustomer for trprt_bill_to_acct_nbr={row.trprt_bill_to_acct_nbr}"
        )
        return

    party = models.ShipmentParty()
    party.shipment_party_type_cd = "I"
    party.company_nm = ccp.name
    party.city_nm = ccp.city
    party.state_cd = ccp.state
    party.country_cd = ccp.country
    party.postal_cd = ccp.postal
    party.broker_id_cd = ccp.broker_cd
    party.customer_acct_nbr = ccp.duty_bill_to_acct_nbr
    party.business_nbr = ccp.business_nbr

    row.ShipmentPartyList.append(party)
    logic_row.log(f"shipment_matching: matched CcpCustomer id={ccp.id} → ShipmentParty type=I")


def declare_logic():
    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
