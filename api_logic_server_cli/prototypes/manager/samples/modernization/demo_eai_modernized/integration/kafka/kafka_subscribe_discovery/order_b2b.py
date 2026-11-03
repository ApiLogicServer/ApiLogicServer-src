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

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b
       reads message, inserts raw payload into OrderB2bMessage blob (Tx 1)
  2. logic/logic_discovery/order_b2b_consume.py
       insert -> publishes payload to topic: order_b2b_processed
  3. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b_processed
       parses payload -> Order + Items (lookups + LogicBank rules) (Tx 2)
  4. api/api_discovery/order_b2b_kafka_consume_debug.py
       /consume_debug/order_b2b bypasses Kafka (or publishes live), calls the same parse function

Creating prompt: docs/requirements/demo_eai/requirements.md section 4 (verbatim above).

Debug / test: see the docstring of api/api_discovery/order_b2b_kafka_consume_debug.py for the curl commands.
Live Kafka: KAFKA_SERVER and KAFKA_CONSUMER_GROUP in config/default.env; reset topics + log with
  bash integration/kafka/order_b2b_reset.sh
"""
import logging
from datetime import datetime
import safrs
from database import models
from integration.OrderB2bMapper import build_order
from integration.system.EaiSubscribeMapper import record_error_text

logger = logging.getLogger('integration.kafka')


def process_order_b2b_payload(payload: str, session, blob_id: int = None):
    """
    Parse payload, resolve lookups, persist the Order and Items, mark blob processed (one transaction).
    Called by consumer 2 (Kafka) and by /consume_debug (simulated).

    blob_id=None (debug path): blob created inside this function in the same Tx.
    blob_id set  (Kafka path): existing blob fetched and is_processed set to True.
    """
    order_row = build_order(payload, session)
    session.add(order_row)
    if blob_id:
        blob = session.get(models.OrderB2bMessage, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.OrderB2bMessage(payload=payload, is_processed=True, received_at=datetime.utcnow())
        session.add(blob)
    session.commit()
    return order_row, blob


def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('order_b2b')
    def order_b2b(msg, safrs_api):
        """Consumer 1: save blob, commit.  The row event publishes to order_b2b_processed."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.OrderB2bMessage(payload=msg.value().decode('utf-8'), is_processed=False,
                                          received_at=datetime.utcnow())
            session.add(blob)
            session.commit()   # blob.id assigned; row event publishes to order_b2b_processed

    @bus.handle('order_b2b_processed')
    def order_b2b_processed(msg, safrs_api):
        """Consumer 2: parse + persist the order, mark blob processed (atomic Tx 2).  A poison or rejected message is
        logged and recorded on its blob (error_text); it never stops the consumer."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_order_b2b_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception as e:
                logger.exception(f"order_b2b_processed error (blob_id={blob_id})")
                if blob_id:
                    try:
                        record_error_text(models.OrderB2bMessage, blob_id, str(e))
                    except Exception:   # never let error-recording end the consumer
                        logger.exception(f"could not record error_text for blob_id={blob_id}")
