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

import logging

from logic_bank.logic_bank import Rule
from database import models

app_logger = logging.getLogger("api_logic_server_app")


def declare_logic():

    def _match_importer(row: models.Shipment, old_row: models.Shipment, logic_row):
        """On Shipment insert, find matching Customer and create ShipmentParty type 'I'."""
        if old_row is not None:
            return  # inserts only

        if not row.trprt_bill_to_acct_nbr:
            return

        customer = logic_row.session.query(models.Customer).filter_by(
            duty_bill_to_acct_nbr=row.trprt_bill_to_acct_nbr
        ).first()

        if customer is None:
            app_logger.warning(
                f'shipment_matching: no Customer found for '
                f'trprt_bill_to_acct_nbr={row.trprt_bill_to_acct_nbr}'
            )
            return

        importer = models.ShipmentParty(
            shipment_party_type_cd='I',
            company_nm=customer.name,
            city_nm=customer.city,
            country_cd=customer.country,
            state_cd=customer.state,
            postal_cd=customer.postal,
            business_nbr=str(customer.business_nbr)[:15] if customer.business_nbr else None,
            customer_acct_nbr=customer.id,
        )
        row.ShipmentPartyList.append(importer)
        logic_row.log(f'shipment_matching: created importer party for customer {customer.name}')

    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
