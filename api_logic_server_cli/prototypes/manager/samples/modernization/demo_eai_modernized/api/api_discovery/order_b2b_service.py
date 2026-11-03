"""
Feature: Order B2B Intake

* **Partner Payload Transformation (`process_order_b2b`)**:
  * Accepts `{ "Account": "<customer name>", "Notes": "...", "Items": [{ "Name": "<product name>", "QuantityOrdered": <int> }] }`.
  * Resolves `Account` by `Customer.name` and each item's `Name` by `Product.name`; raises `LookupError` (mapped to HTTP `422`) if either is unknown.
  * Validates that `Items` is non-empty and every `QuantityOrdered` is a positive integer (`> 0`); raises `ValueError` (mapped to HTTP `400`) otherwise.
  * Sets `Order.CreatedOn` to `date.today()` and commits the order and items atomically (rolling back if credit check or validation fails in `consume`).
* **Multi-Channel Intake**:
  1. **Synchronous REST (`POST /OrderB2B`)**: Processes a JSON request body and returns the created order (`201 Created`).
  2. **Asynchronous Kafka Consumer (`start_consumer`)**: Background daemon thread subscribed to topic `order_b2b` (consumer group `demo_eai_native`); logs and skips poison/rejected messages so a bad payload never halts the consumer.
  3. **Brokerless Debug Endpoint (`GET /consume_debug/<topic>?file=<path>`)**: Reads a payload file located within the project directory and runs the exact same `consume` pipeline.

Synchronous REST channel: POST /OrderB2B with the partner payload as the JSON body (see
docs/requirements/demo_eai/message_formats/order_b2b.json).  Same build and rules as the Kafka channel
(integration/OrderB2bMapper.py).  Needs a bearer token when security is enabled.
"""
import logging
import safrs
from flask import request, jsonify

from integration.OrderB2bMapper import build_order

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """ registers POST /OrderB2B (plain Flask route, so the statuses are 201 / 400 / 422), bearer token required when
    security is enabled (method_decorators is empty at this point: authentication is configured after the services) """

    def order_b2b():
        """ Creates an order from a partner payload: 201 created, 400 invalid payload or rejected by a rule, 422 unknown Account/Name """
        session = safrs.DB.session
        try:
            payload = request.get_data(as_text=True)
            order_row = build_order(payload, session)
            session.add(order_row)
            session.commit()
            return jsonify({"message": "B2B Order created successfully", "order_id": order_row.id,
                            "customer": order_row.customer.name, "items_count": len(order_row.ItemList)}), 201
        except LookupError as e:        # unknown Account or product Name
            session.rollback()
            return jsonify({"error": str(e)}), 422
        except Exception as e:          # ValueError, bad JSON, and constraint errors (e.g. credit limit)
            session.rollback()
            app_logger.info(f"OrderB2B rejected: {e}")
            return jsonify({"error": str(e)}), 400

    view = order_b2b
    from config.config import Config
    if Config.SECURITY_ENABLED:
        from flask_jwt_extended import jwt_required
        view = jwt_required()(view)
    app.add_url_rule("/OrderB2B", endpoint="order_b2b_rest", view_func=view, methods=["POST"])
