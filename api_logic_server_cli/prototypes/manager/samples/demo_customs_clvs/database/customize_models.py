import sqlite3
from database import models
from safrs import jsonapi_attr
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, remote, foreign
import logging

app_logger = logging.getLogger(__name__)

from database.database_discovery.auto_discovery import discover_models
discover_models()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable FK enforcement per SQLite connection — required for ON DELETE CASCADE."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

"""
If you wish to drive models from the database schema,
you can use this file to customize your schema (add relationships, derived attributes),
and preserve customizations over iterations (regenerations of models.py).

Called from models.py (classes describing schema, per introspection).

Your Code Goes Here
"""
