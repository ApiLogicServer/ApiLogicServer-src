"""Business logic, hooked on the SQLAlchemy session so it applies to every write path (REST, B2B, Kafka)."""
from sqlalchemy import event, text
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import get_history

from . import messaging
from .models import Customer, Item, Order, Product


class CreditError(ValueError):
    pass


def _changed(obj, attr):
    """(old, new) of attr, or None when attr is unchanged."""
    h = get_history(obj, attr)
    if not h.has_changes():
        return None
    return (h.deleted[0] if h.deleted else None), (h.added[0] if h.added else None)


def _acc(session, key):
    return session.info.setdefault(key, set())


@event.listens_for(Session, "before_flush")
def before_flush(session, ctx, instances):
    orders, customers, shipped = _acc(session, "orders"), _acc(session, "customers"), _acc(session, "shipped")
    for obj in list(session.new) + list(session.dirty):
        if isinstance(obj, Item):
            product = session.get(Product, obj.product_id)
            if product is None:
                raise ValueError(f"product {obj.product_id} not found")
            if obj in session.new or _changed(obj, "product_id"):
                obj.unit_price = product.unit_price  # copy the price from the product
            obj.amount = obj.quantity * obj.unit_price
            change = _changed(obj, "order_id")
            orders.update(i for i in (change or ()) if i is not None)
            orders.add(obj.order_id)
        elif isinstance(obj, Order):
            if session.get(Customer, obj.customer_id) is None:
                raise ValueError(f"customer {obj.customer_id} not found")
            if obj.id is not None:
                orders.add(obj.id)
            change = _changed(obj, "customer_id")
            if change:
                customers.update(i for i in change if i is not None)
            if _changed(obj, "date_shipped") and obj.date_shipped is not None:
                shipped.add(obj)
        elif isinstance(obj, Customer) and obj not in session.new and _changed(obj, "credit_limit"):
            customers.add(obj.id)
    for obj in list(session.deleted):
        if isinstance(obj, Item):
            orders.add(obj.order_id)
        elif isinstance(obj, Order):
            customers.add(obj.customer_id)
            for item in session.query(Item).filter_by(order_id=obj.id):
                session.delete(item)


@event.listens_for(Session, "after_flush")
def after_flush(session, ctx):
    orders, customers, shipped = (session.info.pop(k, set()) for k in ("orders", "customers", "shipped"))
    for obj in session.new:
        if isinstance(obj, Order):
            orders.add(obj.id)
            customers.add(obj.customer_id)
            if obj.date_shipped is not None:
                shipped.add(obj)
        elif isinstance(obj, Item):
            orders.add(obj.order_id)
    orders.discard(None)
    for oid in orders:
        session.execute(text('UPDATE "order" SET amount_total = '
                             '(SELECT COALESCE(SUM(amount), 0) FROM item WHERE order_id = :o) WHERE id = :o'), {"o": oid})
        row = session.execute(text('SELECT customer_id FROM "order" WHERE id = :o'), {"o": oid}).first()
        if row:
            customers.add(row[0])
    for cid in customers:
        session.execute(text('UPDATE customer SET balance = (SELECT COALESCE(SUM(amount_total), 0) '
                             'FROM "order" WHERE customer_id = :c AND date_shipped IS NULL) WHERE id = :c'), {"c": cid})
        name, balance, limit = session.execute(
            text("SELECT name, balance, credit_limit FROM customer WHERE id = :c"), {"c": cid}).one()
        if balance > limit:
            raise CreditError(f"{name}: balance {balance} exceeds credit limit {limit}")
    for obj in list(session.identity_map.values()):  # raw UPDATEs bypassed the ORM
        if isinstance(obj, Order):
            session.expire(obj, ["amount_total"])
        elif isinstance(obj, Customer):
            session.expire(obj, ["balance"])
    for order in shipped:
        session.info.setdefault("outbox", []).append(_shipping_message(session, order.id))


def _shipping_message(session, order_id):
    o = session.execute(text('SELECT o.id, o.CreatedOn, o.amount_total, c.name FROM "order" o '
                             "JOIN customer c ON c.id = o.customer_id WHERE o.id = :o"), {"o": order_id}).one()
    items = session.execute(text("SELECT i.quantity, p.name, i.unit_price FROM item i "
                                 "JOIN product p ON p.id = i.product_id WHERE i.order_id = :o ORDER BY i.id"),
                            {"o": order_id}).all()
    return ("order_shipping", {
        "order_id": o[0], "order_date": str(o[1]), "customer_name": o[3], "total": o[2],
        "items": [{"quantity": q, "product_name": n, "unit_price": p} for q, n, p in items]})


@event.listens_for(Session, "after_commit")
def after_commit(session):
    for topic, message in session.info.pop("outbox", []):
        messaging.publish(topic, message)


@event.listens_for(Session, "after_rollback")
def after_rollback(session):
    for key in ("orders", "customers", "shipped", "outbox"):
        session.info.pop(key, None)
