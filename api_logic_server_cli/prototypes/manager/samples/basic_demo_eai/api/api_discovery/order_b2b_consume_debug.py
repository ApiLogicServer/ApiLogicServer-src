"""
Debug Endpoint — /consume_debug/order_b2b
==========================================
Req §3 / §6: Test the order_b2b consume pipeline without Kafka.

Enabled when APILOGICPROJECT_CONSUME_DEBUG=true (set in config/default.env).

Test:
  curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json"

Calls process_order_b2b_payload() — the same function Consumer 2 uses — so the
debug path exercises identical logic to the production Kafka path.
"""
import logging
import os
from pathlib import Path

import safrs
from flask import request, jsonify

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    if not os.getenv('APILOGICPROJECT_CONSUME_DEBUG'):
        return

    @app.route('/consume_debug/order_b2b')
    def consume_debug_order_b2b():
        """
        Debug the order_b2b consume pipeline without Kafka.

        Query param:
          file — path to JSON file containing the order_b2b payload

        Example:
          curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json"
        """
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({"success": False,
                            "message": "Missing ?file= parameter"}), 400

        from integration.kafka.kafka_subscribe_discovery.order_b2b import process_order_b2b_payload
        try:
            payload = Path(file_path).read_text()
            order_row, blob = process_order_b2b_payload(payload, safrs.DB.session)
            return jsonify({
                "success":  True,
                "topic":    "order_b2b",
                "blob_id":  blob.id,
                "order_id": order_row.id,
                "file":     file_path,
            })
        except Exception as e:
            app_logger.error(f"consume_debug/order_b2b: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "topic":   "order_b2b",
                "error":   str(e),
            }), 500
