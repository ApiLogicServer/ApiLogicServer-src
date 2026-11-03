"""Flask REST API (JSON, filter by attribute, create/update/delete), secured by Keycloak tokens."""
import json
import os
import sys
from datetime import date

import jwt
from flask import Flask, abort, g, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import integration, logic, messaging, security
from .models import TABLES, Customer, Order

# Derived columns are set by the business logic, never by clients.
DERIVED = {"customer": {"balance"}, "order": {"amount_total"}, "item": {"amount", "unit_price"}}
OPEN_PATHS = {"/health", "/kafka_log"}


def to_dict(obj):
    return {c.name: (v.isoformat() if isinstance(v := getattr(obj, c.name), date) else v)
            for c in obj.__table__.columns}


def coerce(column, value):
    if value is None:
        return None
    t = column.type.python_type
    if t is date:
        return date.fromisoformat(value)
    if t is bool:
        return value if isinstance(value, bool) else str(value).lower() in ("1", "true")
    return t(value)


def create_app(db_path, kafka_server=None):
    app = Flask(__name__)
    engine = create_engine(f"sqlite:///{os.path.abspath(db_path)}")
    Session = sessionmaker(engine)
    messaging.configure(kafka_server)
    if kafka_server:
        integration.start_consumer(kafka_server, Session)

    @app.before_request
    def authenticate():
        g.session = Session()
        if request.path in OPEN_PATHS or request.path.startswith("/consume_debug/"):
            return
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="missing bearer token"), 401
        try:
            g.user = security.authenticate(header[7:])
        except jwt.PyJWTError as e:
            return jsonify(error=f"invalid token: {e}"), 401

    @app.teardown_request
    def close(_):
        g.session.close()

    @app.errorhandler(logic.CreditError)
    @app.errorhandler(ValueError)
    def bad_request(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(LookupError)
    def unprocessable(e):
        return jsonify(error=str(e.args[0] if e.args else e)), 422

    def model_for(table):
        return TABLES.get(table) or abort(404, f"no such table: {table}")

    def query(model):
        q = g.session.query(model)
        criterion = security.row_filter(g.user, model)
        return q.filter(criterion) if criterion is not None else q

    def writable(model, data):
        cols = {c.name: c for c in model.__table__.columns}
        derived = DERIVED.get(model.__tablename__, set())
        unknown = set(data) - set(cols)
        if unknown:
            raise ValueError(f"unknown attribute(s): {sorted(unknown)}")
        return {k: coerce(cols[k], v) for k, v in data.items() if k not in derived and k != "id"}

    @app.get("/health")
    def health():
        return jsonify(status="ok", kafka=messaging.mode())

    @app.get("/kafka_log")
    def kafka_log():
        return jsonify([{"topic": t, "message": m} for t, m in messaging.published])

    @app.get("/api/<table>")
    def list_rows(table):
        model = model_for(table)
        q = query(model)
        cols = {c.name: c for c in model.__table__.columns}
        for key, value in request.args.items():
            if key in ("limit", "offset"):
                continue
            if key not in cols:
                raise ValueError(f"cannot filter on unknown attribute {key!r}")
            q = q.filter(getattr(model, key) == coerce(cols[key], value))
        q = q.order_by(model.id).offset(request.args.get("offset", 0, int)).limit(request.args.get("limit", 100, int))
        return jsonify(data=[to_dict(o) for o in q])

    @app.get("/api/<table>/<int:id>")
    def get_row(table, id):
        model = model_for(table)
        return jsonify(to_dict(query(model).filter(model.id == id).first() or abort(404)))

    @app.post("/api/<table>")
    def create_row(table):
        model = model_for(table)
        obj = model(**writable(model, request.get_json()))
        g.session.add(obj)
        g.session.commit()
        return jsonify(to_dict(obj)), 201

    @app.route("/api/<table>/<int:id>", methods=["PATCH", "PUT"])
    def update_row(table, id):
        model = model_for(table)
        obj = query(model).filter(model.id == id).first() or abort(404)
        for k, v in writable(model, request.get_json()).items():
            setattr(obj, k, v)
        g.session.commit()
        return jsonify(to_dict(obj))

    @app.delete("/api/<table>/<int:id>")
    def delete_row(table, id):
        model = model_for(table)
        g.session.delete(query(model).filter(model.id == id).first() or abort(404))
        g.session.commit()
        return "", 204

    @app.post("/OrderB2B")
    def order_b2b():
        order_id = integration.consume("order_b2b", request.get_json(), Session)
        return jsonify(to_dict(g.session.get(Order, order_id))), 201

    @app.get("/consume_debug/<topic>")
    def consume_debug(topic):
        """Runs the same parse-and-save the Kafka consumer uses, on a message read from a file (no broker needed)."""
        path = request.args.get("file") or abort(400, "file= required")
        if not os.path.abspath(path).startswith(os.getcwd() + os.sep):
            abort(400, "file must be under the project directory")
        with open(path) as f:
            order_id = integration.consume(topic, f.read(), Session)
        return jsonify(topic=topic, mode=request.args.get("mode", "simulated"), order_id=order_id)

    return app
