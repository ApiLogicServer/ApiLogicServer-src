"""
Debug endpoint for ISDC EAI consume pipeline (no Kafka required).
Enabled when APILOGICPROJECT_CONSUME_DEBUG is set in config/default.env.

Usage:
  curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'
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

    @app.route('/consume_debug/isdc')
    def consume_debug_isdc():
        """Debug the ISDC consume pipeline without Kafka.
        curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'
        """
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({"success": False, "message": "Missing ?file= parameter"})
        from integration.kafka.kafka_subscribe_discovery.isdc import process_isdc_payload
        try:
            payload = Path(file_path).read_text()
            shipment_row, blob = process_isdc_payload(payload, safrs.DB.session)
            return jsonify({
                "success": True,
                "topic": "isdc",
                "blob_id": blob.id,
                "file": file_path,
                "awb_nbr": shipment_row.awb_nbr,
                "pieces": len(shipment_row.PieceList),
                "parties": len(shipment_row.ShipmentPartyList),
                "commodities": len(shipment_row.ShipmentCommodityList),
            })
        except Exception as e:
            app_logger.exception(f"consume_debug/isdc: {e}")
            return jsonify({"success": False, "topic": "isdc", "error": str(e)}), 500
