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
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _publish_order_b2b(row: models.OrderB2bMessage, old_row, logic_row: LogicRow):
    """OrderB2bMessage event: publishes the raw blob to order_b2b_processed after Tx 1 commits, so
    Consumer 2 can parse it in a clean Tx 2 (2-message pattern)."""
    if not logic_row.is_inserted() or not row.payload:
        return
    if row.is_processed:
        # debug path: process_order_b2b_payload() already ran Tx 2 inline (blob created with is_processed=True)
        # do NOT re-publish - Consumer 2 would attempt a duplicate insert
        logic_row.log(f"_publish_order_b2b: skipping re-publish - blob.id={row.id} already is_processed=True (debug path)")
        return
    import integration.kafka.kafka_producer as kafka_producer
    if not kafka_producer.kafka_available():
        # Kafka not configured, or the broker does not answer - /consume_debug simulates Tx 2 directly
        logic_row.log("_publish_order_b2b: Kafka not configured or broker not reachable - skipping publish")
        return
    kafka_producer.producer.produce(topic='order_b2b_processed', key=str(row.id), value=row.payload.encode('utf-8'))
    kafka_producer.producer.flush(timeout=10)


def declare_logic():
    Rule.after_flush_row_event(on_class=models.OrderB2bMessage, calling=_publish_order_b2b)
