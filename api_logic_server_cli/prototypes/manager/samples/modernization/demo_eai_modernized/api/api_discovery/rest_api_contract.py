"""
Feature: REST API Contract

* **Generic CRUD (`/api/<table>` & `/api/<table>/<int:id>`)**:
  * Supports `GET` (list with exact-match attribute filtering, `limit` default `100`, `offset` default `0`, ordered by `id`), `GET` by ID, `POST` (`201`), `PATCH`/`PUT` (`200`), and `DELETE` (`204`).
* **Write Protection on Derived Columns (`DERIVED`, `writable`)**:
  * Client-supplied values for `id`, `customer.balance`, `order.amount_total`, `item.amount`, and `item.unit_price` are silently ignored on create/update; unknown column names are rejected with `400 Bad Request`.
* **Error Mapping**:
  * `ValueError` and `CreditError` → `400 Bad Request`
  * Missing/invalid JWT → `401 Unauthorized`
  * Unknown table or row (including RLS-hidden rows) → `404 Not Found`
  * `LookupError` (unknown B2B `Account` or `Product`) → `422 Unprocessable Entity`

The generated JSON:API endpoints (/api/<table>) already give the CRUD, filtering, paging and the 404 / 401 mapping; the
rules give the 400 for a rejected transaction.  This request guard adds the two clauses they do not: client values for
derived columns are silently dropped, and unknown column names are rejected with 400.
"""
import logging
from flask import request, jsonify
from sqlalchemy import inspect as sa_inspect

app_logger = logging.getLogger("api_logic_server_app")

DERIVED = {
    "Customer": {"balance"},
    "Order": {"amount_total"},
    "Item": {"amount", "unit_price"},
}
""" columns the rules own: a client value is ignored on create and update (id is never client-writable either) """

ALWAYS_ALLOWED = {"S_CheckSum"}   # the optimistic-locking checksum the Admin App sends


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """ registers the request guard for JSON:API writes """

    @app.before_request
    def rest_api_contract():
        """ POST / PATCH / PUT on /api/<type>: drop derived (and id) attributes, 400 on unknown column names """
        if request.method not in ("POST", "PATCH", "PUT") or not request.path.startswith("/api/"):
            return None
        body = request.get_json(silent=True)    # cached: the in-place changes below are what the endpoint reads
        data = body.get("data") if isinstance(body, dict) else None
        if not isinstance(data, dict) or not isinstance(data.get("attributes"), dict):
            return None
        from database import models
        model_class = getattr(models, str(data.get("type")), None)
        if model_class is None or not hasattr(model_class, "__table__"):
            return None
        attributes = data["attributes"]
        columns = {each.key for each in sa_inspect(model_class).mapper.column_attrs}
        unknown = sorted(name for name in attributes if name not in columns and name not in ALWAYS_ALLOWED)
        if unknown:
            return jsonify({"errors": [{"title": f"Unknown column(s) for {data['type']}: {', '.join(unknown)}",
                                        "code": "400"}]}), 400
        for name in DERIVED.get(data["type"], set()) | {"id"}:
            if name in attributes:
                app_logger.info(f"rest_api_contract: ignoring client value for derived column {data['type']}.{name}")
                del attributes[name]
        return None
