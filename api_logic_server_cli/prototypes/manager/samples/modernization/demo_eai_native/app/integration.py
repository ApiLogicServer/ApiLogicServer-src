"""B2B / Kafka order intake. One mapping function serves the OrderB2B endpoint, the Kafka consumer and /consume_debug."""
import json
import logging
import threading
from datetime import date

from .models import Customer, Item, Order, Product

log = logging.getLogger("integration")


def process_order_b2b(session, msg):
    """Map a partner-format order to Order + Items (Account -> Customer by name, Items.Name -> Product by name)."""
    customer = session.query(Customer).filter_by(name=msg.get("Account")).first()
    if customer is None:
        raise LookupError(f"unknown customer: {msg.get('Account')!r}")
    lines = msg.get("Items") or []
    if not lines:
        raise ValueError("order has no Items")
    order = Order(customer_id=customer.id, notes=msg.get("Notes"), CreatedOn=date.today())
    session.add(order)
    session.flush()  # assigns order.id
    for line in lines:
        product = session.query(Product).filter_by(name=line.get("Name")).first()
        if product is None:
            raise LookupError(f"unknown product: {line.get('Name')!r}")
        quantity = line.get("QuantityOrdered")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError(f"bad QuantityOrdered for {line.get('Name')!r}: {quantity!r}")
        session.add(Item(order_id=order.id, product_id=product.id, quantity=quantity))
    return order


def consume(topic, payload, session_factory):
    """Parse-and-save for one message; shared by the consumer thread and /consume_debug."""
    with session_factory() as session:
        try:
            order = process_order_b2b(session, json.loads(payload) if isinstance(payload, (str, bytes)) else payload)
            session.commit()
            return order.id
        except Exception:
            session.rollback()
            raise


def start_consumer(server, session_factory, topics=("order_b2b",)):
    from confluent_kafka import Consumer

    consumer = Consumer({"bootstrap.servers": server, "group.id": "demo_eai_native",
                         "auto.offset.reset": "earliest", "enable.auto.commit": True})
    consumer.subscribe(list(topics))

    def loop():
        while True:
            msg = consumer.poll(1.0)
            if msg is None or msg.error():
                continue
            try:
                log.info("order_b2b -> order %s", consume(msg.topic(), msg.value(), session_factory))
            except Exception as e:  # a bad message must not stop the consumer
                log.error("message on %s rejected: %s", msg.topic(), e)

    threading.Thread(target=loop, daemon=True, name="kafka-consumer").start()
