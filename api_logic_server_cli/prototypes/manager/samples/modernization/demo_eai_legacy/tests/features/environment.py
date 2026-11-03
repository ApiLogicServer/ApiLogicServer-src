import os
import shutil
import tempfile

import requests

from app import messaging
from app.api import create_app

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYCLOAK_TOKEN = "http://localhost:8080/realms/kcals/protocol/openid-connect/token"


def token_for(username):
    r = requests.post(KEYCLOAK_TOKEN, data=dict(grant_type="password", client_id="alsclient",
                                                username=username, password="p"))
    r.raise_for_status()
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def before_all(context):
    os.chdir(ROOT)  # /consume_debug resolves file= against the project directory
    context.tokens = {u: token_for(u) for u in ("admin", "u1")}


def before_scenario(context, scenario):
    """Every scenario gets a pristine copy of the database and an empty Kafka log."""
    context.tmp = tempfile.mkdtemp()
    db = os.path.join(context.tmp, "db.sqlite")
    shutil.copy(os.path.join(ROOT, "database", "db.sqlite"), db)
    context.client = create_app(db).test_client()
    context.headers = context.tokens["admin"]
    messaging.published.clear()


def after_scenario(context, scenario):
    shutil.rmtree(context.tmp, ignore_errors=True)
