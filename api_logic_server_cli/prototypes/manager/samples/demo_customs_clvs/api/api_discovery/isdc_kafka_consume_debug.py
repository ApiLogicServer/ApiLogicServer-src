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
        """Debug the isdc consume pipeline without Kafka.
        Enable with: export APILOGICPROJECT_CONSUME_DEBUG=true
        curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'
        """
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({"success": False, "message": "Missing ?file= parameter"})
        from integration.kafka.kafka_subscribe_discovery.isdc import process_isdc_payload
        try:
            payload = Path(file_path).read_text()
            parent_row, blob = process_isdc_payload(payload, safrs.DB.session)
            return jsonify({
                "success": True, "topic": "isdc", "blob_id": blob.id, "file": file_path,
                "awb_nbr": parent_row.awb_nbr,
                "pieces": len(parent_row.PieceList),
                "parties": len(parent_row.ShipmentPartyList),
                "commodities": len(parent_row.ShipmentCommodityList),
            })
        except Exception as e:
            app_logger.error(f"consume_debug/isdc: {e}")
            return jsonify({"success": False, "topic": "isdc", "error": str(e)}), 500
