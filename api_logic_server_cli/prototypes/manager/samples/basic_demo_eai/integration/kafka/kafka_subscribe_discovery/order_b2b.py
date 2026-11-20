"""
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity

Basic Design:
  1. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b
       reads message, inserts raw payload into OrderB2bMessage blob (Tx 1)
  2. logic/logic_discovery/order_b2b_consume.py
       insert -> publishes payload to topic: order_b2b_processed
  3. integration/kafka/kafka_subscribe_discovery/order_b2b.py  - order_b2b_processed
       parses payload -> Order + Items (lookups + LogicBank rules) (Tx 2)
  4. api/api_discovery/order_b2b_kafka_consume_debug.py
       /consume_debug/order_b2b: live through Kafka when a broker answers, else calls the same parse function directly

Creating prompt: docs/requirements/demo_eai/requirements.md, section 3 (Kafka Subscribe).

Test without Kafka (sample: docs/requirements/demo_eai/message_formats/order_b2b.json):
    curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json&mode=simulated"
Tests: test/api_logic_server_behave/features (Kafka Subscribe Order Integration); publisher: test/send_order_b2b.py

Enable Kafka (config/default.env, or environment variables), then (re)start the server AFTER Kafka is up:
    KAFKA_SERVER = localhost:9092
    KAFKA_CONSUMER_GROUP = demo_eai-group1
Reset topics + log between runs:  bash integration/kafka/order_b2b_reset.sh
"""
import datetime
import json
import logging
import safrs
from database import models
from integration.system.EaiSubscribeMapper import resolve_lookups, record_error_text

logger = logging.getLogger('integration.kafka')

ORDER_B2B_PARENT_LOOKUPS = [(models.Customer, models.Customer.name, 'Account', 'customer_id')]
ORDER_B2B_CHILD_LOOKUPS  = [(models.Product, models.Product.name, 'Name', 'product_id')]
ORDER_B2B_CHILD_KEY = 'Items'


def process_order_b2b_payload(payload: str, session, blob_id: int = None):
    """Kafka subscribe order_b2b: parse the payload, resolve lookups, persist the Order + Items, mark the blob processed.
    Called by Consumer 2 (blob_id set) and by /consume_debug simulated (blob_id None: blob created in the same Tx)."""
    from integration.OrderB2bMapper import parse
    raw = json.loads(payload)
    order_row, item_rows = parse(payload)
    if item_rows and not hasattr(item_rows[0], '__tablename__'):
        raise TypeError(f"parse() must return list[model_instance]; got {type(item_rows[0]).__name__} - check OrderB2bMapper.parse()")
    resolve_lookups(order_row, raw, ORDER_B2B_PARENT_LOOKUPS, session)
    for item_row, item_src in zip(item_rows, raw.get(ORDER_B2B_CHILD_KEY, [])):
        resolve_lookups(item_row, item_src, ORDER_B2B_CHILD_LOOKUPS, session)
        order_row.ItemList.append(item_row)
    session.add(order_row)
    if blob_id:
        blob = session.get(models.OrderB2bMessage, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.OrderB2bMessage(payload=payload, is_processed=True, received_at=datetime.datetime.now())
        session.add(blob)
    session.commit()
    return order_row, blob


def register(bus):
    """Kafka subscribe order_b2b: registers the two consumers (called by kafka_subscribe_discovery/auto_discovery.py)."""

    @bus.handle('order_b2b')
    def order_b2b(msg, safrs_api):
        """Kafka subscribe order_b2b: Consumer 1 - save the raw blob and commit (Tx 1); the row event publishes it on."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.OrderB2bMessage(payload=msg.value().decode('utf-8'), is_processed=False,
                                          received_at=datetime.datetime.now())
            session.add(blob)
            session.commit()

    @bus.handle('order_b2b_processed')
    def order_b2b_processed(msg, safrs_api):
        """Kafka subscribe order_b2b_processed: Consumer 2 - parse + persist the Order (Tx 2); a failure is recorded on the blob."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_order_b2b_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception as e:
                logger.exception(f"order_b2b_processed parse error (blob_id={blob_id})")
                if blob_id:
                    try:
                        record_error_text(models.OrderB2bMessage, blob_id, str(e))
                    except Exception:   # never let error-recording end the consumer
                        logger.exception(f"could not record error_text for blob_id={blob_id}")
