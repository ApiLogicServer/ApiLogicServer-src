"""
Feature: Subscribe to Kafka and persist shipments

Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.

API service isdc debug: test the isdc subscribe pipeline by hand or from tests, with or without a broker.
Thin file: the engine is integration/system/EaiDebug.py.  Development only: no authentication, and the reset is
destructive.  Enabled by APILOGICPROJECT_CONSUME_DEBUG = true (config/default.env); false turns both off.

Send the sample message - live through Kafka when a broker is configured and answering, else simulated (no Kafka):

    curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'

Force a mode (live answers 409 if Kafka is not available):

    curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml&mode=simulated'
    curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml&mode=live'

Live is asynchronous (the reply is the broker's acknowledgement).  See the outcome in logs/als.log, or the blob table:

    TOKEN=$(curl -s -X POST http://localhost:5656/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"p"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
    curl "http://localhost:5656/api/ShipmentXml/?sort=-id&page%5Blimit%5D=1" -H "Authorization: Bearer $TOKEN"

Purge the messages in topics isdc and isdc_processed (the topics and consumers stay; nothing to do without a broker):

    curl -X POST "http://localhost:5656/consume_debug/isdc/reset"
"""
from integration.system.EaiDebug import register_consume_debug, register_queue_reset

SAMPLE_FILE = "docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml"


def _simulate(payload: str, session) -> dict:
    """isdc debug: runs the live Consumer 2 parse-and-save function directly (no Kafka); returns the outcome."""
    from integration.kafka.kafka_subscribe_discovery.isdc import process_isdc_payload
    shipment, blob = process_isdc_payload(payload, session)
    return {"blob_id": blob.id,
            "awb_nbr": shipment.awb_nbr,
            "local_shipment_oid_nbr": shipment.local_shipment_oid_nbr,
            "pieces": len(shipment.PieceList),
            "parties": len(shipment.ShipmentPartyList),
            "commodities": len(shipment.ShipmentCommodityList)}


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """API service isdc debug: registers /consume_debug/isdc and its reset (only when debug is enabled)."""
    register_consume_debug(app, topic="isdc", simulate=_simulate, port=PORT, sample_file=SAMPLE_FILE,
                           outcome_hint="GET /api/ShipmentXml/?sort=-id&page[limit]=1 (is_processed, error_text)")
    register_queue_reset(app, name="isdc", topics=["isdc", "isdc_processed"], port=PORT)
