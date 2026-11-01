#!/usr/bin/env bash
# integration/kafka/isdc_reset_db.sh - clear the isdc domain and blob tables for repeatable reruns.
# Run from project root, with the server stopped: bash integration/kafka/isdc_reset_db.sh
set -e
sqlite3 database/db.sqlite "
DELETE FROM special_handling;
DELETE FROM shipment_commodity;
DELETE FROM shipment_party;
DELETE FROM piece;
DELETE FROM shipment;
DELETE FROM shipment_xml;"
echo "isdc tables cleared."
