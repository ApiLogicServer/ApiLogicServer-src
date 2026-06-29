from database import models
from safrs import jsonapi_attr
from sqlalchemy.orm import relationship, remote, foreign
import logging

app_logger = logging.getLogger(__name__)

from database.database_discovery.auto_discovery import discover_models
discover_models()

"""
If you wish to drive models from the database schema,
you can use this file to customize your schema (add relationships, derived attributes),
and preserve customizations over iterations (regenerations of models.py).

Called from models.py (classes describing schema, per introspection).

Your Code Goes Here
"""
