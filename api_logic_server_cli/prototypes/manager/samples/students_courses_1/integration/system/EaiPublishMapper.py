"""
EAI Publish Mapper Utilities
=============================
Generic engine for the Kafka EAI publish pattern.

Provides:
  serialize_row(row, sample, exceptions) → dict

Maps a SQLAlchemy row to a shaped output dict, driven by a SAMPLE template
and an optional FIELD_EXCEPTIONS dict declared in each per-topic mapper file.

Resolution order per sample key:
  1. sample[key] is a list  → child collection:
       exceptions[key] = SQLAlchemy relationship name on row
       recurse with child_sample = sample[key][0] for each child row
  2. key in exceptions, value contains '.'  → dot-notation join:
       "RelAttr.column"  →  getattr(getattr(row, RelAttr), column)
  3. key in exceptions, plain string  → column rename:
       getattr(row, exceptions[key])
  4. otherwise  → auto-match by exact name:
       getattr(row, key)

All values pass through _serialize_value() for date/datetime → ISO string.

Usage in a generated per-topic mapper (e.g. kafka_publish_discovery/order_shipping.py):

    from integration.system.EaiPublishMapper import serialize_row

    def row_to_dict(row):
        return serialize_row(row, sample=SAMPLE, exceptions=FIELD_EXCEPTIONS)

See demo_eai/readme.md Section 6 for full pattern documentation.

version: 1.0  (April 2026)
"""

from datetime import date, datetime
import logging

logger = logging.getLogger('integration.eai')


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _serialize_value(value):
    """Convert date/datetime to ISO string; pass everything else through."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def serialize_row(row, sample: dict, exceptions: dict = None) -> dict:
    """
    Walk *sample* keys and resolve each to a value from *row*.

    Args:
        row:        SQLAlchemy model instance (the mapped row)
        sample:     dict whose keys define the output shape; list values
                    signal child collections (one-element list with child sample)
        exceptions: optional FIELD_EXCEPTIONS dict — maps sample key → column/
                    relationship reference; see module docstring for syntax

    Returns:
        dict with the same key structure as *sample*, populated from *row*
    """
    if exceptions is None:
        exceptions = {}

    result = {}

    for key, sample_val in sample.items():

        if isinstance(sample_val, list):
            # ── Child collection ──────────────────────────────────────────
            rel_name = exceptions.get(key, key)
            child_rows = getattr(row, rel_name, None) or []
            child_sample = sample_val[0] if sample_val else {}
            result[key] = [
                serialize_row(child, child_sample, exceptions)
                for child in child_rows
            ]

        elif key in exceptions:
            mapping = exceptions[key]
            if '.' in mapping:
                # ── Dot-notation join: "RelAttr.column" ──────────────────
                rel_attr, col_name = mapping.split('.', 1)
                rel_obj = getattr(row, rel_attr, None)
                result[key] = _serialize_value(
                    getattr(rel_obj, col_name, None) if rel_obj is not None else None
                )
            else:
                # ── Simple rename ─────────────────────────────────────────
                result[key] = _serialize_value(getattr(row, mapping, None))

        else:
            # ── Auto-match by exact key name ─────────────────────────────
            result[key] = _serialize_value(getattr(row, key, None))

    return result
