#!/usr/bin/env bash
# Reset ISDC domain tables for repeatable XR/CE test runs.
# Run from project root: bash integration/kafka/isdc_reset_db.sh

set -e

sqlite3 database/db.sqlite <<'SQL'
PRAGMA foreign_keys = OFF;
DELETE FROM shipment_party;
DELETE FROM shipment_commodity;
DELETE FROM special_handling;
DELETE FROM piece;
DELETE FROM shipment;
DELETE FROM shipment_xml;
PRAGMA foreign_keys = ON;
SQL

echo "Reset complete: shipment domain tables and shipment_xml cleared."
