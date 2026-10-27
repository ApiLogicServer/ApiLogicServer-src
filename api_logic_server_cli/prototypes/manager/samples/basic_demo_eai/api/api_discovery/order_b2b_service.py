"""
Feature: B2B Order Integration

  Scenario: Accept order from external partner
    Given an inbound B2B order in partner format (message_formats/order_b2b.json)
    When the order is received via a Custom API endpoint named OrderB2B
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
"""
import logging

import safrs
from flask import request
from safrs import jsonapi_rpc

from integration.row_dict_maps.OrderB2BMapper import OrderB2BMapper

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """API service OrderB2B: exposes POST /api/OrderB2B/OrderB2B."""
    api.expose_object(OrderB2B)


class OrderB2B(safrs.JABase):
    """API service OrderB2B: accepts an order in partner format and creates Order + Items (rules apply)."""

    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def OrderB2B(self, *args, **kwargs):
        """
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

        Creates a B2B order from a partner system: Customer and Product are looked up by name, and every rule
        (unit price copy, amounts, balance, credit limit) applies.
        """
        db = safrs.DB
        session = db.session

        try:
            mapper_def = OrderB2BMapper()
            request_dict_data = request.json["meta"]["args"]["data"]
            app_logger.info(f"OrderB2B: Processing order for account: {request_dict_data.get('Account')}")

            sql_alchemy_row = mapper_def.dict_to_row(row_dict=request_dict_data, session=session)

            session.add(sql_alchemy_row)
            session.flush()  # ensures the id is generated

            order_id = sql_alchemy_row.id
            customer_name = sql_alchemy_row.customer.name if sql_alchemy_row.customer else "Unknown"
            item_count = len(sql_alchemy_row.ItemList)

            return {
                "message": "B2B Order created successfully",
                "order_id": order_id,
                "customer": customer_name,
                "items_count": item_count
            }

        except Exception as e:
            app_logger.error(f"OrderB2B: Error creating order: {str(e)}")
            session.rollback()
            # raise, do NOT `return {...}, 400`: under jsonapi_rpc a returned tuple is wrapped in an HTTP 200 response,
            # so a rejected order would look accepted to the partner. ValidationError is answered with HTTP 400.
            raise safrs.ValidationError(f"Failed to create B2B order: {e}")
