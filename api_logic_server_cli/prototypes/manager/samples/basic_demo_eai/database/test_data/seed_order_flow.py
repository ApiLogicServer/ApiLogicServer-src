#!/usr/bin/env python
"""
Seed order history for the Order Flow Dashboard - through the rules (not SQL).

    cd demo_eai && PROJECT_DIR=$(pwd) python database/test_data/seed_order_flow.py      (stop the server first)

What it writes, for the 30 days before today:
  - orders arriving as B2B requests (OrderB2bRequest, then the Order via OrderB2BMapper) and as Kafka messages
    (OrderB2bMessage blob, then the Order via the order_b2b mapper + lookups) - the same mappers the live paths use
  - weekday volumes (requests 3-6, messages 2-5 a day) and weekend volumes (0-2 each)
  - a few ordinary rejections (unknown product); one day (9 days ago) with mostly rejected messages
  - no activity 3 and 2 days ago
Every row is inserted on the governed session, so LogicBank prices the orders, checks credit and maintains DailyFlow.
Historical orders are inserted already shipped (date_shipped = their day), so customer balances stay as they are.
CreatedOn is set to the historical arrival time; the stamping handler keeps a supplied CreatedOn and derives CreatedOnDay.

Also: orders that predate the dashboard get their day key (CreatedOnDay) from CreatedOn, by an update through the rules.
Run once: re-running adds another 30 days of history on top.  Seeded rows carry notes starting with 'seed:'.
"""
import os, sys, logging, json, random, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # project root
os.environ["PROJECT_DIR"] = os.environ.get("PROJECT_DIR", str(Path(__file__).parent.parent.parent))
os.chdir(os.environ["PROJECT_DIR"])

from config import server_setup
from flask import Flask
import config.config as config

app_logger = server_setup.logging_setup()
app_logger.setLevel(logging.INFO)
logging.getLogger('logic_logger').setLevel(logging.WARNING)

flask_app = Flask("API Logic Server", template_folder='ui/templates')
flask_app.config.from_object(config.Config)
flask_app.config.from_prefixed_env(prefix="APILOGICPROJECT")
args = server_setup.get_args(flask_app)
server_setup.api_logic_server_setup(flask_app, args)

import safrs
from database import models
from integration.OrderB2bKafkaMapper import parse
from integration.kafka.kafka_subscribe_discovery.order_b2b import ORDER_B2B_PARENT_LOOKUPS, ORDER_B2B_CHILD_LOOKUPS
from integration.row_dict_maps.OrderB2BMapper import OrderB2BMapper
from integration.system.EaiSubscribeMapper import resolve_lookups, record_error_text

random.seed(20261119)
ACCOUNTS = ["Alice", "Bob", "Charlie", "Silent", "Diana"]
PRODUCTS = ["Widget", "Gadget", "Doodad", "Green"]
REJECTED_DAY_OFFSET = 9          # the day with mostly rejected messages
QUIET_OFFSETS = {3, 2}           # no activity


def good_order(day_label: str) -> dict:
    """A partner order that the rules accept (shipped on arrival, so balances are unaffected)."""
    return {"Account": random.choice(ACCOUNTS), "Notes": f"seed: {day_label}",
            "Items": [{"Name": name, "QuantityOrdered": random.randint(1, 3)}
                      for name in random.sample(PRODUCTS, random.randint(1, 2))]}


def bad_order(day_label: str, kind: str) -> tuple:
    """A partner order that is rejected: unknown product or account (lookup), or over the credit limit (unshipped)."""
    if kind == "product":
        return {"Account": random.choice(ACCOUNTS), "Notes": f"seed: {day_label} unknown product",
                "Items": [{"Name": "Sprocket", "QuantityOrdered": 2}]}, True
    if kind == "account":
        return {"Account": "Acme Partners", "Notes": f"seed: {day_label} unknown account",
                "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, True
    return {"Account": "Diana", "Notes": f"seed: {day_label} over credit limit",            # credit: unshipped
            "Items": [{"Name": "Thingamajig", "QuantityOrdered": 1}]}, False


def arrival(day: datetime.date) -> datetime.datetime:
    return datetime.datetime.combine(day, datetime.time(random.randint(7, 18), random.randint(0, 59), random.randint(0, 59)))


def send_message(session, day: datetime.date, data: dict, shipped: bool) -> bool:
    """Kafka path: Tx 1 saves the blob; Tx 2 parses it into an Order (same mapper and lookups as consumer 2)."""
    payload = json.dumps(data)
    blob = models.OrderB2bMessage(payload=payload, is_processed=False, CreatedOn=arrival(day))
    session.add(blob)
    session.commit()
    blob_id = blob.id
    try:
        order, items = parse(payload)
        resolve_lookups(order, data, ORDER_B2B_PARENT_LOOKUPS, session)
        for item, item_src in zip(items, data["Items"]):
            resolve_lookups(item, item_src, ORDER_B2B_CHILD_LOOKUPS, session)
            order.ItemList.append(item)
        order.CreatedOn = day
        order.date_shipped = day if shipped else None
        session.add(order)
        session.get(models.OrderB2bMessage, blob_id).is_processed = True
        session.commit()
        return True
    except Exception as e:
        record_error_text(models.OrderB2bMessage, blob_id, str(e))   # rolls back Tx 2, records on the governed session
        return False


def send_request(session, day: datetime.date, data: dict, shipped: bool) -> bool:
    """B2B API path: record the request (Tx 1), then the Order via OrderB2BMapper (Tx 2), as the OrderB2B service does."""
    req = models.OrderB2bRequest(payload=json.dumps(data), is_processed=False, CreatedOn=arrival(day))
    session.add(req)
    session.commit()
    req_id = req.id
    try:
        order = OrderB2BMapper().dict_to_row(row_dict=data, session=session)
        order.CreatedOn = day
        order.date_shipped = day if shipped else None
        session.add(order)
        session.get(models.OrderB2bRequest, req_id).is_processed = True
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        failed = session.get(models.OrderB2bRequest, req_id)
        failed.error_text = str(e)
        session.commit()
        return False


with flask_app.app_context():
    session = safrs.DB.session

    # 0. day key for orders that predate the dashboard (update through the rules; their DailyFlow buckets are created)
    old = session.query(models.Order).filter(models.Order.CreatedOnDay.is_(None), models.Order.CreatedOn.isnot(None)).all()
    for each in old:
        each.CreatedOnDay = each.CreatedOn.strftime('%Y-%m-%d')
    session.commit()
    print(f"backfilled CreatedOnDay on {len(old)} existing orders")

    today = datetime.date.today()
    totals = {"msg_ok": 0, "msg_bad": 0, "req_ok": 0, "req_bad": 0}
    for offset in range(30, 0, -1):
        day = today - datetime.timedelta(days=offset)
        label = day.isoformat()
        if offset in QUIET_OFFSETS:
            continue
        weekend = day.weekday() >= 5
        if offset == REJECTED_DAY_OFFSET:      # mostly rejected messages; requests normal
            messages = [bad_order(label, k) for k in ("account", "product", "credit", "account", "product")] + \
                       [(good_order(label), True)]
            requests = [(good_order(label), True) for _ in range(random.randint(3, 5))]
        else:
            n_msg = random.randint(0, 2) if weekend else random.randint(2, 5)
            n_req = random.randint(0, 2) if weekend else random.randint(3, 6)
            messages = [(good_order(label), True) for _ in range(n_msg)]
            requests = [(good_order(label), True) for _ in range(n_req)]
            if not weekend and random.random() < 0.3:          # an occasional ordinary rejection
                requests.append(bad_order(label, "product"))
        for data, shipped in messages:
            ok = send_message(session, day, data, shipped)
            totals["msg_ok" if ok else "msg_bad"] += 1
        for data, shipped in requests:
            ok = send_request(session, day, data, shipped)
            totals["req_ok" if ok else "req_bad"] += 1
    print(f"seeded: {totals}")
