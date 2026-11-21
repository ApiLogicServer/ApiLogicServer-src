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
import logging

import safrs
from api.system import api_utils
from flask import request
from safrs import jsonapi_rpc

from database import models
from integration.row_dict_maps.OrderB2BMapper import OrderB2BMapper

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """API service OrderB2B: exposes POST /api/OrderB2B/OrderB2B."""
    api.expose_object(OrderB2B)


class OrderB2B(safrs.JABase):
    """API service OrderB2B: accepts a partner order, records the request with its outcome, and creates the Order."""

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
                      QuantityOrdered: 5
                    - Name: "Gadget"
                      QuantityOrdered: 3
            ---

        API service OrderB2B: creates an Order from a partner's B2B format - Account is looked up as Customer.name,
        Items.Name as Product.name, Items.QuantityOrdered is Item.quantity; the Check Credit rules price the order
        and reject it if the customer's balance would exceed the credit limit.  Each request is recorded first
        (OrderB2bRequest), then marked processed, or given the error text when rejected.
        """
        session = safrs.DB.session
        request_dict_data = request.json["meta"]["args"]["data"]

        # Tx 1: record the request, so it is kept even if processing fails.
        # TODO retention: never delete OrderB2bRequest rows - DailyFlow counts them (a delete changes history).
        #      To limit size, clear old payloads but keep the rows.
        b2b_request = models.OrderB2bRequest(payload=json.dumps(request_dict_data), is_processed=False)
        session.add(b2b_request)
        session.commit()
        request_id = b2b_request.id

        # Tx 2: create the order (rules: price, totals, credit check), and mark the request processed.
        try:
            app_logger.info(f"OrderB2B: request {request_id}, account {api_utils.safe_log(request_dict_data.get('Account'))}")
            order = OrderB2BMapper().dict_to_row(row_dict=request_dict_data, session=session)
            session.add(order)
            b2b_request.is_processed = True
            session.flush()  # assigns order.id; the request commits after the response (governed session)
            return {
                "message": "B2B Order created successfully",
                "order_id": order.id,
                "request_id": request_id,
                "customer": order.customer.name if order.customer else "Unknown",
                "items_count": len(order.ItemList)
            }
        except Exception as e:
            app_logger.error(f"OrderB2B: request {request_id} rejected: {e}")
            session.rollback()  # this service owns its transaction
            failed = session.get(models.OrderB2bRequest, request_id)
            if failed is not None:
                failed.error_text = str(e)
                session.commit()  # governed session: the daily rejected count sees it
            # raise, do NOT `return {...}, 400`: jsonapi_rpc wraps a returned tuple in an HTTP 200 response
            raise safrs.ValidationError(f"Failed to create B2B order: {e}")
