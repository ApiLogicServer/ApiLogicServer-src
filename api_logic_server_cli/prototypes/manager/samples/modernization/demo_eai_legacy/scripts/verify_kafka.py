"""Live check of the Kafka integration: reset topics, start the app against the broker, send the sample, confirm the order.
Run from the project directory:  python scripts/verify_kafka.py"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import requests
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
TOPICS = ["order_b2b", "order_shipping"]
admin = AdminClient({"bootstrap.servers": SERVER})


def wait(fn, what, seconds=30):
    end = time.time() + seconds
    while time.time() < end:
        try:
            result = fn()
        except requests.ConnectionError:
            result = None
        if result:
            return result
        time.sleep(0.5)
    sys.exit(f"FAIL: timed out waiting for {what}")


# 1. reset topics so old messages are not replayed
existing = [t for t in TOPICS if t in admin.list_topics(timeout=10).topics]
for fut in admin.delete_topics(existing).values():
    fut.result()
wait(lambda: not any(t in admin.list_topics(timeout=10).topics for t in TOPICS), "topic deletion")
for attempt in range(10):
    futs = admin.create_topics([NewTopic(t, 1, 1) for t in TOPICS])
    errs = [f.exception() for f in futs.values() if f.exception()]
    if not errs:
        break
    time.sleep(1)
else:
    sys.exit(f"FAIL: could not recreate topics: {errs}")
print("topics reset:", TOPICS)
admin.delete_consumer_groups(["demo_eai_native"])
time.sleep(1)

# 2. start the app on a scratch copy of the database, Kafka enabled
tmp = tempfile.mkdtemp()
db = os.path.join(tmp, "db.sqlite")
shutil.copy("database/db.sqlite", db)
proc = subprocess.Popen([sys.executable, "-m", "app"], env={**os.environ, "DB_PATH": db, "KAFKA_SERVER": SERVER},
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    wait(lambda: requests.get("http://localhost:5656/health").ok if proc.poll() is None else sys.exit("app died"),
         "app start")
    print("app kafka mode:", requests.get("http://localhost:5656/health").json()["kafka"])
    kc = "http://localhost:8080/realms/kcals/protocol/openid-connect/token"
    token = requests.post(kc, data=dict(grant_type="password", client_id="alsclient", username="admin",
                                        password="p")).json()["access_token"]
    H = {"Authorization": f"Bearer {token}"}
    orders = lambda: requests.get("http://localhost:5656/api/order", headers=H).json()["data"]
    before = len(orders())

    # 3. subscribe: send the sample message on order_b2b, expect a new order
    msg = open("docs/requirements/demo_eai/message_formats/order_b2b.json").read()
    p = Producer({"bootstrap.servers": SERVER})
    p.produce("order_b2b", msg.encode())
    p.flush(10)
    new = wait(lambda: orders()[before:], "new order from order_b2b")
    print(f"order_b2b -> order {new[0]['id']} total {new[0]['amount_total']}  (live)")

    # 4. publish: ship that order, expect a message on order_shipping
    from confluent_kafka import Consumer
    c = Consumer({"bootstrap.servers": SERVER, "group.id": "verify", "auto.offset.reset": "earliest"})
    c.subscribe(["order_shipping"])
    requests.patch(f"http://localhost:5656/api/order/{new[0]['id']}", headers=H, json={"date_shipped": "2026-10-25"})
    got = wait(lambda: (m := c.poll(1.0)) and not m.error() and json.loads(m.value()), "order_shipping message")
    print("order_shipping <-", json.dumps(got))
    c.close()
    print("PASS")
finally:
    proc.terminate()
