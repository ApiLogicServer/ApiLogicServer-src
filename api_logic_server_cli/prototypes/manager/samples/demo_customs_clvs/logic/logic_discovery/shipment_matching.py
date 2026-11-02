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
import logging
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

app_logger = logging.getLogger(__name__)


def _match_importer(row: models.Shipment, old_row, logic_row: LogicRow):
    """Shipment event: on insert, finds the Customer whose duty_bill_to_acct_nbr equals the shipment's
    trprt_bill_to_acct_nbr and, if found, inserts an importer ShipmentParty (type I) copied from that Customer."""
    if not logic_row.is_inserted():
        return
    customer = None
    if row.trprt_bill_to_acct_nbr is not None:
        customer = logic_row.session.query(models.Customer).filter(
            models.Customer.duty_bill_to_acct_nbr == row.trprt_bill_to_acct_nbr).first()
    if customer is None:
        app_logger.warning(f"Importer match: no Customer for trprt_bill_to_acct_nbr={row.trprt_bill_to_acct_nbr} "
                           f"(shipment {row.local_shipment_oid_nbr})")
        logic_row.log(f"Importer match: no Customer for trprt_bill_to_acct_nbr={row.trprt_bill_to_acct_nbr}")
        return
    party = models.ShipmentParty()
    party.shipment = row                      # attach via the relationship: the parent is not flushed yet
    party.shipment_party_type_cd = "I"
    party.customer_acct_nbr = customer.duty_bill_to_acct_nbr
    party.company_nm = customer.name
    party.address_1 = customer.address1
    party.address_2 = customer.address2
    party.city_nm = customer.city
    party.state_cd = customer.state
    party.country_cd = customer.country
    party.postal_cd = customer.postal
    party.business_nbr = customer.business_nbr
    party.contact_phone_nbr = customer.phone_nbr
    party.broker_id_cd = customer.broker_cd
    logic_row.session.add(party)
    logic_row.insert(reason="Importer match", row=party)


def declare_logic():
    Rule.row_event(on_class=models.Shipment, calling=_match_importer)
