#!/usr/bin/env python
"""
Seed order history for the Order Flow Dashboard (requirement 6): the 30 days before today.

Run from the project root, with the server STOPPED and Kafka off for the seed:

    KAFKA_SERVER= PROJECT_DIR=$(pwd) python database/test_data/seed_order_flow.py

What it creates (deterministic: fixed random seed, dates relative to today, so a rebuild draws the same picture):
  - 4 demo customers with high credit limits (the 5 sample customers are not touched)
  - normal flow: 5-9 orders per weekday, 1-3 per weekend day; about 60% arrive as order_b2b messages
    (a processed message row per order), the rest as B2B requests (a processed request row per order);
    now and then a B2B request is rejected (credit limit)
  - a bad-data day (9 days ago): messages keep arriving, but most fail (unknown account) - rejected, with error_text
  - the flow stopping: no orders and no messages 3 and 2 days ago; yesterday it recovers
  - orders older than 7 days are shipped 2 days after they were placed, so balances stay realistic

Everything goes through the ORM inside the app (Flask context, LogicBank active): Item prices and amounts, Order
totals and Customer balances are derived by the rules, and the credit limit is checked - nothing is computed here.
Every row is given its CreatedOn (a day in the past); stamping keeps a supplied CreatedOn and derives CreatedOnDay,
so the rules create and maintain each day's DailyFlow totals.  Messages and requests are inserted already processed
(or rejected, with an error text the seed supplies): they are NOT delivered through the B2B API or Kafka, and the
row-event bridge publishes nothing.
Refuses to run twice (it checks for the seed customers).
"""
import os, sys, json, random, datetime, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))   # project root on the path
os.environ["PROJECT_DIR"] = os.environ.get("PROJECT_DIR", str(Path(__file__).parent.parent.parent))

from flask import Flask
from config import server_setup
import config.config as config

app_logger = server_setup.logging_setup()
app_logger.setLevel(logging.WARNING)

flask_app = Flask("API Logic Server", template_folder='ui/templates')
flask_app.config.from_object(config.Config)
flask_app.config.from_prefixed_env(prefix="APILOGICPROJECT")
args = server_setup.get_args(flask_app)
server_setup.api_logic_server_setup(flask_app, args)

import safrs
from database import models

SEED_NOTE = "seed: order flow"
CUSTOMERS = ["Northwind Traders", "Contoso Retail", "Fabrikam Stores", "Tailspin Toys"]
PRODUCTS = ["Widget", "Gadget", "Doodad", "Green"]
BAD_DAY, QUIET_DAYS, DAYS = 9, (3, 2), 30          # days before today
BAD_ACCOUNT = "ACME-EU"


def at(day: datetime.date) -> datetime.datetime:
    """A business-hours timestamp on the day."""
    return datetime.datetime.combine(day, datetime.time(hour=rng.randint(8, 17), minute=rng.randint(0, 59)))


def message_payload(account: str, items: list) -> str:
    """The order_b2b message shape (docs/requirements/demo_eai/message_formats/order_b2b.json)."""
    return json.dumps({"Account": account, "Notes": "Kafka order from sales",
                       "Items": [{"Name": name, "QuantityOrdered": qty} for name, qty in items]}, indent=2)


rng = random.Random(20261119)
today = datetime.date.today()

with flask_app.app_context():
    session = safrs.DB.session
    if session.query(models.Customer).filter(models.Customer.name == CUSTOMERS[0]).first():
        print("already seeded (Northwind Traders exists) - nothing done")
        sys.exit(0)

    customers = [models.Customer(name=name, credit_limit=100000) for name in CUSTOMERS]
    session.add_all(customers)
    session.commit()
    products = {p.name: p for p in session.query(models.Product).filter(models.Product.name.in_(PRODUCTS))}

    # Create the day rows first.  LogicBank 1.34.04 insert_parent creates a parent per child when several new children
    # of the same NEW parent are inserted in one transaction (UNIQUE constraint failed: daily_flow.day); with the day
    # rows present, the rules just adjust them.
    all_days = [(today - datetime.timedelta(days=back)).isoformat() for back in range(DAYS, 0, -1)]
    existing = {d.day for d in session.query(models.DailyFlow).filter(models.DailyFlow.day.in_(all_days))}
    session.add_all([models.DailyFlow(day=d) for d in all_days if d not in existing])
    session.commit()

    counts = {"orders": 0, "messages": 0, "rejected": 0, "requests": 0, "rejected_requests": 0, "shipped": 0}
    for back in range(DAYS, 0, -1):
        day = today - datetime.timedelta(days=back)
        if back in QUIET_DAYS:
            continue                                          # the flow stopped: nothing arrives
        weekend = day.weekday() >= 5
        n_orders = rng.randint(1, 3) if weekend else rng.randint(5, 9)
        if back == BAD_DAY:
            n_orders = 2                                      # most of the day's messages fail
        for _ in range(n_orders):
            customer = rng.choice(customers)
            lines = [(name, rng.randint(1, 5)) for name in rng.sample(PRODUCTS, rng.randint(1, 3))]
            order = models.Order(customer_id=customer.id, CreatedOn=day, notes=SEED_NOTE)
            for name, qty in lines:
                order.ItemList.append(models.Item(product_id=products[name].id, quantity=qty))
            session.add(order)
            when = at(day)
            if rng.random() < 0.6:                            # arrived as an order_b2b message, processed
                session.add(models.OrderB2bMessage(payload=message_payload(customer.name, lines), is_processed=True,
                                                   received_at=when, CreatedOn=when))
                counts["messages"] += 1
            else:                                             # arrived as a B2B request, processed
                session.add(models.OrderB2bRequest(payload=message_payload(customer.name, lines), is_processed=True,
                                                   CreatedOn=when))
                counts["requests"] += 1
            counts["orders"] += 1
        if back != BAD_DAY and rng.random() < 0.25:           # a B2B request rejected by the credit limit
            session.add(models.OrderB2bRequest(payload=message_payload("Diana", [("Widget", 20)]), is_processed=False,
                                               CreatedOn=at(day),
                                               error_text="Customer balance (1800.00) exceeds credit limit (1000.00)"))
            counts["requests"] += 1
            counts["rejected_requests"] += 1
        n_rejected = 8 if back == BAD_DAY else (1 if rng.random() < 0.2 else 0)
        for _ in range(n_rejected):                           # unknown account: Tx 2 failed, reason recorded
            when = at(day)
            session.add(models.OrderB2bMessage(payload=message_payload(BAD_ACCOUNT, [("Widget", 1)]), is_processed=False,
                                               received_at=when, CreatedOn=when,
                                               error_text=f"resolve_lookups: no Customer found where name == '{BAD_ACCOUNT}'"))
            counts["messages"] += 1
            counts["rejected"] += 1
        session.commit()

    for order in session.query(models.Order).filter(models.Order.notes == SEED_NOTE,
                                                    models.Order.CreatedOn <= today - datetime.timedelta(days=7)):
        order.date_shipped = order.CreatedOn + datetime.timedelta(days=2)   # shipped orders leave the balance
        counts["shipped"] += 1
    session.commit()

    print(f"seeded {DAYS} days before {today}: {counts['orders']} orders ({counts['shipped']} shipped), "
          f"{counts['messages']} order_b2b messages ({counts['rejected']} rejected), "
          f"{counts['requests']} B2B requests ({counts['rejected_requests']} rejected); "
          f"bad-data day {today - datetime.timedelta(days=BAD_DAY)}, "
          f"no activity {', '.join(str(today - datetime.timedelta(days=d)) for d in QUIET_DAYS)}")
    for c in customers:
        session.refresh(c)
        print(f"  {c.name}: balance {c.balance} (limit {c.credit_limit})")
