"""
Debug endpoint for ISDC Kafka consume pipeline.
Gated by APILOGICPROJECT_CONSUME_DEBUG env var.

Usage:
    curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'
    curl 'http://localhost:5656/consume_debug/isdc' -d @payload.xml -H 'Content-Type: text/xml'
"""

import os
import logging
from flask import request, jsonify
import safrs

app_logger = logging.getLogger("api_logic_server_app")

_DEBUG_ENABLED = os.getenv('APILOGICPROJECT_CONSUME_DEBUG', 'false').lower() not in ('false', '0', 'no', '')


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=None):

    if not _DEBUG_ENABLED:
        return

    @app.route('/consume_debug/isdc', methods=['GET', 'POST'])
    def consume_debug_isdc():
        """
        Debug ISDC XML consume — bypasses Kafka, same parse+persist logic as Consumer 2.
        GET  ?file=<relative-path>   — read XML from file
        POST  body                   — XML as request body
        """
        try:
            if request.method == 'POST':
                xml_text = request.data.decode('utf-8')
            else:
                file_param = request.args.get('file')
                if not file_param:
                    return jsonify({'success': False, 'error': 'Provide ?file= or POST XML body'}), 400
                xml_path = os.path.join(project_dir, file_param)
                with open(xml_path, 'r', encoding='utf-8') as fh:
                    xml_text = fh.read()

            db = safrs.DB
            session = db.session

            from integration.kafka.kafka_subscribe_discovery.isdc import process_isdc_payload
            blob_needed = True
            from database import models
            blob = models.ShipmentXml(payload=xml_text)
            session.add(blob)
            session.flush()

            summary = process_isdc_payload(xml_text, session)
            blob.is_processed = 1
            session.commit()

            return jsonify(summary)

        except Exception as exc:
            app_logger.error(f'consume_debug/isdc error: {exc}', exc_info=True)
            try:
                safrs.DB.session.rollback()
            except Exception:
                pass
            return jsonify({'success': False, 'error': str(exc)}), 500
