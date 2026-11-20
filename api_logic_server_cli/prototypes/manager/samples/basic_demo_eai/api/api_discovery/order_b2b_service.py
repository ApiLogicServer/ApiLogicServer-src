"""
Feature: B2B Order Integration

  Scenario: Accept order from external partner
    Given an inbound B2B order in partner format (message_formats/order_b2b.json)
    When the order is received via a Custom API endpoint named OrderB2B
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
    And record each request, with its outcome, for the order flow dashboard
"""
import json
from flask import request
from safrs import jsonapi_rpc
import safrs
from database import models
from integration.row_dict_maps.OrderB2BMapper import OrderB2BMapper
import logging

app_logger = logging.getLogger("api_logic_server_app")

# TODO (retention): request rows are never purged. The daily totals count them, so deleting rows would lower the
# totals (a delete adjusts the counts). To purge, clear `payload` but keep the row, or freeze closed days - then
# change this TODO to DONE.


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    """API service OrderB2B: exposes POST /api/OrderB2B/OrderB2B for partner orders."""
    api.expose_object(OrderB2B)


class OrderB2B(safrs.JABase):
    """API service OrderB2B: records the request, creates the Order and its Items (the rules derive the rest), and
    records the outcome on the request row."""

    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def OrderB2B(self, *args, **kwargs):  # yaml comment => swagger description
        """ # yaml creates Swagger description
            args :
                data:
                    Account: "Alice"
                    Notes: "Rush order for Q4 promotion"
                    Items :
                    - Name: "Widget"
                      QuantityOrdered: 1
                    - Name: "Gadget"
                      QuantityOrdered: 2
            ---

        Creates a B2B order from a partner system: Customer and Product looked up by name;
        prices, amounts, the order total and the customer balance are derived by the rules,
        and the credit limit is checked.  Each request is recorded with its outcome.
        """
        session = safrs.DB.session
        request_dict_data = request.json["meta"]["args"]["data"]

        # Tx 1: record the request first, so it is counted even if processing fails
        request_row = models.OrderB2bRequest(payload=json.dumps(request_dict_data), is_processed=False)
        session.add(request_row)
        session.commit()
        request_id = request_row.id

        try:   # Tx 2: process it
            sql_alchemy_row = OrderB2BMapper().dict_to_row(row_dict=request_dict_data, session=session)
            session.add(sql_alchemy_row)
            request_row.is_processed = True
            session.flush()  # assigns the order id, and runs the rules
            return {
                "message": "B2B Order created successfully",
                "order_id": sql_alchemy_row.id,
                "request_id": request_id,
                "customer": sql_alchemy_row.customer.name if sql_alchemy_row.customer else "Unknown",
                "items_count": len(sql_alchemy_row.ItemList)
            }
        except Exception as e:
            app_logger.error(f"OrderB2B: Error creating order: {str(e)}")
            session.rollback()   # discard Tx 2; the request row (Tx 1) stays
            failed = session.get(models.OrderB2bRequest, request_id)
            if failed:
                failed.is_processed = False
                failed.error_text = str(e)
                session.commit()   # on the governed session: the daily totals count the failure
            # raise (not return {...}, 400): under jsonapi_rpc a returned tuple is answered with HTTP 200
            raise safrs.ValidationError(f"Failed to create B2B order: {e}")
