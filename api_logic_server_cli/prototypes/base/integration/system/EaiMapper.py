"""
EAI Consume Mapper Utilities
============================
Generic helpers for the 2-message Kafka EAI consume pattern.

Provides:
  - populate_row()           XML element → SQLAlchemy row  (Tier 1 + Tier 2 + Tier 3)
  - populate_row_from_dict() JSON dict  → SQLAlchemy row  (Tier 1 + Tier 2 + Tier 3)
  - resolve_lookups()        name → FK resolution after parse() (post-parse, optional)

Both functions apply the same 3-tier mapping contract:
  Tier 1: automatic lowercase(field_name) → column name  (zero config)
  Tier 2: FIELD_EXCEPTIONS dict           → skip or remap
  Tier 3: custom callback                 → full control after Tier 1+2

Usage in a generated mapper (e.g. integration/XyzMapper.py):

    from integration.system.EaiMapper import populate_row, populate_row_from_dict

See docs/training/eai_consume.md for full pattern documentation.

Design note — why this file exists, and why it is not sufficient alone:
  EXISTS:      Provides the named 3-tier contract (Tier 1/2/3), type coercion,
               XML namespace stripping, and FK column validation — boilerplate that
               would otherwise be reinvented (badly) in every custom mapper.
               Its presence also guides AI generation: the CE can say "use the
               3-tier contract" rather than leaving AI to invent an ad-hoc approach.
  NOT ENOUGH:  Per-topic facts — parent/child model classes, child array key,
               EXCEPTIONS dicts, TAG_ROUTING (XML), FK lookup config — are
               domain-specific and must live in a thin XyzMapper.py per pipeline.
               EaiMapper supplies the engine; XyzMapper supplies the config.

version: 1.1  (April 2026)
"""

import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import Callable, Optional

from sqlalchemy import inspect as sa_inspect

import logging
logger = logging.getLogger('integration.eai')


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _local(tag: str) -> str:
    """Strip Clark-notation XML namespace: {uri}localname → localname."""
    return re.sub(r"\{[^}]*\}", "", tag)


def _column_names(model_class) -> frozenset:
    """Return frozenset of column attribute names for a SQLAlchemy model class."""
    return frozenset(col.key for col in sa_inspect(model_class).mapper.column_attrs)


def _coerce(text: str, col_name: str, model_class) -> object:
    """
    Coerce a string value to the Python type expected by the SQLAlchemy column:
      - Date     columns → datetime.date
      - DateTime columns → datetime.datetime
      - Everything else  → str (SQLAlchemy handles int/decimal transparently)
    Returns None for empty/None input.
    """
    if not text:
        return None
    try:
        col_type = sa_inspect(model_class).mapper.columns[col_name].type.__class__.__name__
    except Exception:
        return text     # column not found in mapper — pass through

    if col_type == "Date":
        t = text.rstrip("Z").split("T")[0]
        try:
            return date.fromisoformat(t)
        except ValueError:
            return None
    if col_type == "DateTime":
        t = text.rstrip("Z")
        if "." in t:
            base, frac = t.split(".", 1)
            t = f"{base}.{frac[:6]}"
        try:
            return datetime.fromisoformat(t)
        except ValueError:
            return None
    if col_type == "Integer":
        try:
            return int(text)
        except (ValueError, TypeError):
            return None
    if col_type in ("Numeric", "Float"):
        from decimal import Decimal
        try:
            return Decimal(text)
        except Exception:
            return None
    return text


# ---------------------------------------------------------------------------
# Public: populate a row from an XML element
# ---------------------------------------------------------------------------

def populate_row(
    row: object,
    element: ET.Element,
    exceptions: Optional[dict] = None,
    overrides: Optional[dict] = None,
    custom: Optional[Callable] = None,
) -> object:
    """
    Populate *row* in-place from the children of an XML *element*.

    3-tier mapping contract:
      Tier 1: lowercase(local_name) → column name if it exists on the model
      Tier 2: exceptions dict — None = skip, str = remap to that column name
      Tier 3: custom(row, element) callback called after Tier 1+2

    Args:
        row:        SQLAlchemy model instance to populate
        element:    XML element whose children are the fields
        exceptions: FIELD_EXCEPTIONS dict  {xml_name: None | "col_name"}
        overrides:  forced column values applied last  {col_name: value}
        custom:     callback(row, element) for complex derivations

    Returns the same *row* instance.
    """
    model_class = type(row)
    valid = _column_names(model_class)
    exceptions = exceptions or {}

    for child in element:
        local = _local(child.tag)
        text = child.text.strip() if (child.text and child.text.strip()) else None

        if local in exceptions:
            mapped = exceptions[local]
            if mapped is None:
                continue            # Tier 2: skip
            col_name = mapped       # Tier 2: remap
        else:
            col_name = local.lower()  # Tier 1: auto

        if col_name not in valid:
            continue                # no matching column — skip silently

        setattr(row, col_name, _coerce(text, col_name, model_class))

    if overrides:
        for col, val in overrides.items():
            setattr(row, col, val)

    if custom:
        custom(row, element)        # Tier 3: escape hatch

    return row


# ---------------------------------------------------------------------------
# Public: populate a row from a JSON dict
# ---------------------------------------------------------------------------

def populate_row_from_dict(
    row: object,
    data: dict,
    exceptions: Optional[dict] = None,
    overrides: Optional[dict] = None,
    custom: Optional[Callable] = None,
) -> object:
    """
    Populate *row* in-place from a JSON *data* dict.

    3-tier mapping contract — same as populate_row() but for JSON:
      Tier 1: lowercase(key) → column name if it exists on the model
      Tier 2: exceptions dict — None = skip, str = remap to that column name
      Tier 3: custom(row, data) callback called after Tier 1+2

    Args:
        row:        SQLAlchemy model instance to populate
        data:       dict of field_name → value (one level; nested handled by TAG_ROUTING)
        exceptions: FIELD_EXCEPTIONS dict  {json_key: None | "col_name"}
        overrides:  forced column values applied last  {col_name: value}
        custom:     callback(row, data) for complex derivations

    Returns the same *row* instance.
    """
    model_class = type(row)
    valid = _column_names(model_class)
    exceptions = exceptions or {}

    for key, value in data.items():
        if not isinstance(value, (str, int, float, bool, type(None))):
            continue                # skip nested objects/lists — handled by TAG_ROUTING

        if key in exceptions:
            mapped = exceptions[key]
            if mapped is None:
                continue            # Tier 2: skip
            col_name = mapped       # Tier 2: remap
        else:
            col_name = key.lower()  # Tier 1: auto

        if col_name not in valid:
            continue

        text = str(value) if value is not None else None
        setattr(row, col_name, _coerce(text, col_name, model_class))

    if overrides:
        for col, val in overrides.items():
            setattr(row, col, val)

    if custom:
        custom(row, data)           # Tier 3: escape hatch

    return row


# ---------------------------------------------------------------------------
# Public: resolve FK lookups after parse()
# ---------------------------------------------------------------------------

def resolve_lookups(
    row: object,
    source,
    lookups: list,
    session,
) -> None:
    """
    Resolve FK lookups after parse(). Call once for parent_row, then once per child row.

    For each entry in *lookups*, queries *lookup_model* with one or more filter
    conditions, then sets *fk_col* on *row* to the PK of the found row.

    Args:
        row:      SQLAlchemy row instance to update in-place
        source:   dict (JSON) or ET.Element (XML) — the raw parsed payload
        lookups:  list of lookup tuples (see formats below)
        session:  SQLAlchemy session

    Single-field lookup tuple:  (lookup_model, lookup_col, source_field, fk_col)
        lookup_model  — model class to query                e.g. models.Customer
        lookup_col    — column to filter by (need not be PK) e.g. models.Customer.Id
        source_field  — key/tag in source payload           e.g. 'AccountId'
        fk_col        — FK attribute to set on row          e.g. 'CustomerId'

    Compound-field lookup tuple:  (lookup_model, [(col, source_field), ...], fk_col)
        Use when uniqueness requires multiple filter columns, e.g.:
        (models.Employee,
         [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')],
         'EmployeeId')

    Raises:
        ValueError: if the lookup finds zero or multiple rows (must be unique)
    """
    if not lookups:
        return

    def _get(key: str):
        if isinstance(source, dict):
            return source.get(key)
        el = source.find(key)                           # ET.Element path
        return (el.text or "").strip() if el is not None else None

    for entry in lookups:
        lookup_model = entry[0]
        query = session.query(lookup_model)

        if isinstance(entry[1], list):
            # Compound lookup: (model, [(col, source_field), ...], fk_col)
            filter_pairs = entry[1]
            fk_col = entry[2]
            for (lookup_col, source_field) in filter_pairs:
                value = _get(source_field)
                if value is None:
                    break
                query = query.filter(lookup_col == value)
            else:
                # all filters applied — fall through to result check
                pass
        else:
            # Single-field lookup: (model, lookup_col, source_field, fk_col)
            lookup_col = entry[1]
            source_field = entry[2]
            fk_col = entry[3]
            value = _get(source_field)
            if value is None:
                continue
            query = query.filter(lookup_col == value)

        rows = query.all()
        if len(rows) == 0:
            raise ValueError(
                f"resolve_lookups: no {lookup_model.__name__} found "
                f"for fk_col={fk_col!r} from source fields"
            )
        if len(rows) > 1:
            raise ValueError(
                f"resolve_lookups: multiple {lookup_model.__name__} found "
                f"for fk_col={fk_col!r} — lookup must be unique"
            )
        found = rows[0]
        pk_cols = sa_inspect(lookup_model).mapper.primary_key
        pk_val = getattr(found, pk_cols[0].name)
        setattr(row, fk_col, pk_val)
