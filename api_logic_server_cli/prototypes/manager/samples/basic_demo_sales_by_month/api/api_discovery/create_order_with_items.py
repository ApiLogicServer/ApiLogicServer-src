import logging

import safrs
from flask import jsonify, request

from database import models

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """
    Custom endpoint: POST /api/ints/CreateOrderWithItems/

    Not required to work around a bug (see internal_dev/composite_key_issue/composite_key_issue.md
    v1.2 - the original "Bug 2" was a LogicBank engine bug, since fixed in gold source; a plain
    JSON:API POST to /api/Order/ with sales_rep_id set now works correctly too). Kept as a
    convenience: lets a caller supply sales_rep_name instead of sales_rep_id (looked up here,
    same convention as basic_demo_eai's order_b2b_api.py Customer/Product lookups):
        {
          "customer_id": 2,
          "sales_rep_id": 3,          // or: "sales_rep_name": "Jane"
          "notes": "optional",
          "items": [
            {"product_id": 3, "quantity": 2},
            {"product_id": 4, "quantity": 1}
          ]
        }

    Response JSON (201):
        {
          "id": <order.id>,
          "customer_id": 2,
          "sales_rep_id": 3,
          "CreatedOnYearMonth": "2026-09",
          "amount_total": 123.45,
          "items": [{"id": ..., "product_id": 3, "quantity": 2, "unit_price": ..., "amount": ...}, ...]
        }
    """

    @app.route('/api/ints/CreateOrderWithItems/', methods=['POST'])
    def create_order_with_items():
        data = request.get_json(force=True) or {}

        customer_id = data.get('customer_id')
        sales_rep_id = data.get('sales_rep_id')
        sales_rep_name = data.get('sales_rep_name')
        items = data.get('items') or []

        if customer_id is None:
            return jsonify({"error": "customer_id is required"}), 400
        if not items:
            return jsonify({"error": "items must be a non-empty list"}), 400

        session = safrs.DB.session

        if sales_rep_id is None and sales_rep_name:
            sales_rep = session.query(models.SalesRep).filter(
                models.SalesRep.name == sales_rep_name
            ).first()
            if not sales_rep:
                return jsonify({"error": f"SalesRep not found: {sales_rep_name}"}), 404
            sales_rep_id = sales_rep.id

        try:
            order = models.Order(
                customer_id=customer_id,
                sales_rep_id=sales_rep_id,
                notes=data.get('notes'))
            session.add(order)

            for item in items:
                session.add(models.Item(
                    order=order,
                    product_id=item.get('product_id'),
                    quantity=item.get('quantity', 1)))

            session.commit()  # LogicBank rules fire here: CreatedOn/CreatedOnYearMonth stamping,
                               # amounts, credit check, SalesRepTotal insert_parent + sum/count
        except Exception as e:
            session.rollback()
            app_logger.info(f"create_order_with_items failed: {e}")
            return jsonify({"error": str(e)}), 400

        return jsonify({
            "id": order.id,
            "customer_id": order.customer_id,
            "sales_rep_id": order.sales_rep_id,
            "CreatedOnYearMonth": order.CreatedOnYearMonth,
            "amount_total": order.amount_total,
            "items": [{
                "id": i.id,
                "product_id": i.product_id,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
                "amount": i.amount,
            } for i in order.ItemList],
        }), 201
