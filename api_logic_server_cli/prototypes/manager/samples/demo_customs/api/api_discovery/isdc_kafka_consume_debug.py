"""
Debug endpoint for the isdc Kafka consume pipeline.
Enabled when APILOGICPROJECT_CONSUME_DEBUG=true (set in config/default.env).

Usage:
  curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'

Returns JSON with success, awb_nbr, piece/party/commodity/special-handling counts.
"""

import logging
import os
from pathlib import Path

import safrs
from flask import jsonify, request

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    if not os.getenv('APILOGICPROJECT_CONSUME_DEBUG'):
        return

    @app.route('/consume_debug/isdc')
    def consume_debug_isdc():
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({"success": False, "message": "Missing ?file= parameter"}), 400

        from integration.kafka.kafka_subscribe_discovery.isdc import process_isdc_payload
        try:
            payload = Path(file_path).read_text()
            shipment, blob = process_isdc_payload(payload, safrs.DB.session)
            return jsonify({
                "success": True,
                "topic": "isdc",
                "blob_id": blob.id,
                "local_shipment_oid_nbr": shipment.local_shipment_oid_nbr,
                "awb_nbr": shipment.awb_nbr,
                "pieces": len(shipment.PieceList),
                "parties": len(shipment.ShipmentPartyList),
                "commodities": len(shipment.ShipmentCommodityList),
                "special_handling": len(shipment.SpecialHandlingList),
                "file": file_path,
            })
        except Exception as e:
            app_logger.exception(f"consume_debug/isdc error")
            return jsonify({"success": False, "topic": "isdc", "error": str(e)}), 500
