"""
B2B Order API — Accept inbound orders from external partners
=============================================================
Req §2: POST /api/OrderB2B — maps Account→Customer by name,
        Items.Name→Product by name, enforces Check Credit rules.
"""
import logging
import safrs
from flask import request, jsonify
from database import models

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):

    @app.route('/api/OrderB2B', methods=['POST'])
    def order_b2b_api():
        """
        Accept an inbound B2B order from an external partner.

        Payload (message_formats/order_b2b.json):
            {
              "Account": "Alice",
              "Notes": "optional notes",
              "Items": [
                { "Name": "Widget", "QuantityOrdered": 1 },
                { "Name": "Gadget", "QuantityOrdered": 2 }
              ]
            }

        Maps:
          Account            → Customer.name lookup → Order.customer_id
          Items[].Name       → Product.name lookup  → Item.product_id
          Items[].QuantityOrdered                  → Item.quantity

        All Check Credit rules (copy price, compute amount, sum totals,
        enforce credit limit) are automatically enforced by LogicBank.

        Test:
          curl -X POST http://localhost:5656/api/OrderB2B \\
            -H "Content-Type: application/json" \\
            -d '{"Account":"Alice","Notes":"test","Items":[{"Name":"Widget","QuantityOrdered":1}]}'
        """
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Missing JSON body"}), 400

        session = safrs.DB.session

        customer = session.query(models.Customer).filter(
            models.Customer.name == data.get('Account')
        ).first()
        if not customer:
            return jsonify({"success": False,
                            "error": f"Customer not found: {data.get('Account')}"}), 404

        order = models.Order(
            customer_id=customer.id,
            notes=data.get('Notes'),
        )

        for item_data in data.get('Items', []):
            product = session.query(models.Product).filter(
                models.Product.name == item_data.get('Name')
            ).first()
            if not product:
                return jsonify({"success": False,
                                "error": f"Product not found: {item_data.get('Name')}"}), 404
            item = models.Item(
                product_id=product.id,
                quantity=item_data.get('QuantityOrdered', 0),
            )
            order.ItemList.append(item)

        session.add(order)
        session.flush()   # DB-assigns order.id; LogicBank rules fire
        order_id = order.id
        session.commit()

        app_logger.info(f"OrderB2B: created order_id={order_id} for customer={customer.name}")
        return jsonify({"success": True, "order_id": order_id})
