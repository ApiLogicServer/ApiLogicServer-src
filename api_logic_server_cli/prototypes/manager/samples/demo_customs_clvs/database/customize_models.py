from database import models
from safrs import jsonapi_attr
from sqlalchemy.orm import relationship, remote, foreign
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

app_logger = logging.getLogger(__name__)

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma_foreign_keys(dbapi_connection, connection_record):
    """SQLite disables FK enforcement per-connection by default; ON DELETE CASCADE
    clauses in the schema (shipment -> piece/shipment_party/special_handling/shipment_commodity)
    are silent no-ops without this."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

from database.database_discovery.auto_discovery import discover_models
discover_models()

"""
If you wish to drive models from the database schema,
you can use this file to customize your schema (add relationships, derived attributes),
and preserve customizations over iterations (regenerations of models.py).

Called from models.py (classes describing schema, per introspection).

Your Code Goes Here
"""
