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

API service order_b2b debug: test the order_b2b subscribe pipeline by hand or from tests, with or without a broker.
Thin file: the engine is integration/system/EaiDebug.py.  Development only: no authentication, and the reset is
destructive.  Enabled by APILOGICPROJECT_CONSUME_DEBUG = true (config/default.env); false turns both off.

Send the sample message - live through Kafka when a broker is configured and answering, else simulated (no Kafka):

    curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json"

Force a mode (live answers 409 if Kafka is not available):

    curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json&mode=simulated"
    curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json&mode=live"

Live is asynchronous (the reply is the broker's acknowledgement).  See the outcome in logs/als.log, or the blob table:

    TOKEN=$(curl -s -X POST http://localhost:5656/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"p"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
    curl "http://localhost:5656/api/OrderB2bMessage/?sort=-id&page%5Blimit%5D=1" -H "Authorization: Bearer $TOKEN"

Purge the messages in topics order_b2b and order_b2b_processed (the topics and consumers stay; nothing to do without a broker):

    curl -X POST "http://localhost:5656/consume_debug/order_b2b/reset"
"""
from integration.system.EaiDebug import register_consume_debug, register_queue_reset

SAMPLE_FILE = "docs/requirements/demo_eai/message_formats/order_b2b.json"


def _simulate(payload: str, session) -> dict:
    """order_b2b debug: runs the live consumer's parse-and-save function directly (no Kafka); returns the outcome."""
    from integration.kafka.kafka_subscribe_discovery.order_b2b import process_order_b2b_payload
    order_row, blob = process_order_b2b_payload(payload, session)
    return {"blob_id": blob.id, "order_id": order_row.id}


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """API service order_b2b debug: registers /consume_debug/order_b2b and its reset (only when debug is enabled)."""
    register_consume_debug(app, topic="order_b2b", simulate=_simulate, port=PORT, sample_file=SAMPLE_FILE,
                           outcome_hint="GET /api/OrderB2bMessage/?sort=-id&page[limit]=1 (is_processed, error_text)")
    register_queue_reset(app, name="order_b2b", topics=["order_b2b", "order_b2b_processed"], port=PORT)
