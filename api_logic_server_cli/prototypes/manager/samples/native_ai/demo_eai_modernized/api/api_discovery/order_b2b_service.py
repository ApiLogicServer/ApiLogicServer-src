"""
Feature: B2B Order Integration

  Scenario: Accept order from external partner
    Given an inbound B2B order in partner format (message_formats/order_b2b.json)
    When the order is received via a Custom API endpoint named OrderB2B
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
"""

from flask import request
from safrs import jsonapi_rpc
import safrs
from integration.row_dict_maps.OrderB2BMapper import OrderB2BMapper
import logging

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """API service OrderB2B: exposes the /api/OrderB2B/OrderB2B endpoint for partner order submissions."""
    api.expose_object(OrderB2B)


class OrderB2B(safrs.JABase):
    """API service OrderB2B: accepts external partner orders and maps Account/Items into Order and Item rows."""

    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def OrderB2B(self, *args, **kwargs):
        """ # yaml creates Swagger description
            args :
                data:
                    Account: "Alice"
                    Notes: "Kafka order from sales"
                    Items :
                    - Name: "Widget"
                      QuantityOrdered: 1
                    - Name: "Gadget"
                      QuantityOrdered: 2
            ---

        API service OrderB2B: creates B2B orders from external partner payloads with Customer/Product name lookups and LogicBank credit enforcement.
        """
        db = safrs.DB
        session = db.session

        try:
            mapper_def = OrderB2BMapper()
            request_dict_data = request.json["meta"]["args"]["data"]

            app_logger.info(f"OrderB2B: Processing order for account: {request_dict_data.get('Account')}")

            sql_alchemy_row = mapper_def.dict_to_row(row_dict=request_dict_data, session=session)

            session.add(sql_alchemy_row)
            session.flush()

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
            raise safrs.ValidationError(f"Failed to create B2B order: {e}")

