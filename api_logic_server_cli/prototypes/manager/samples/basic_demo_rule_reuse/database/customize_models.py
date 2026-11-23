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

# SysConfig.current(session) - convenience accessor for the single-row runtime-settings
# table (the starter.sqlite / System Creation Services pattern - see
# docs/training/logic_bank_api.md). SysConfig has no FK from any transactional table (it's
# a global settings row, not a per-row parent), so rule functions that need a threshold
# would otherwise each repeat `logic_row.session.query(models.SysConfig).first()` -
# duplicated code, and a common place to introduce a silent bug (a guessed fallback like
# `config.rate if config else 0.05` that never errors, just quietly uses the wrong value
# forever). Added conditionally: most projects do NOT have a SysConfig table at all, so this
# must not raise or log at import time when it's absent - only .current() itself raises,
# and only when actually called with no row present.
if hasattr(models, 'SysConfig'):
    def _sys_config_current(session):
        """Return the single SysConfig row (runtime thresholds/settings).

        Use `models.SysConfig.current(logic_row.session)` instead of repeating
        `logic_row.session.query(models.SysConfig).first()` in every rule function.

        Raises RuntimeError if the row is missing - a missing SysConfig row means every
        threshold-based rule in the system would silently use None (or a guessed
        fallback), not a recoverable condition to paper over.
        """
        config = session.query(models.SysConfig).first()
        if config is None:
            raise RuntimeError(
                "SysConfig has no row - rules that read SysConfig thresholds/settings "
                "depend on it. Seed one row before running any logic that calls "
                "SysConfig.current()."
            )
        return config

    models.SysConfig.current = staticmethod(_sys_config_current)
