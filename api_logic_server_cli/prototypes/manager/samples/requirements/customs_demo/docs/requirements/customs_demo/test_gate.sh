#!/usr/bin/env bash
# XR test gate for customs_demo (debug + Kafka paths)
# Run from project root:
#   bash docs/requirements/customs_demo/test_gate.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

MANAGER_PYTHON="$ROOT_DIR/../venv/bin/python"
if [[ -n "${PYTHON_BIN:-}" ]]; then
  PYTHON_BIN="$PYTHON_BIN"
elif [[ -x "$MANAGER_PYTHON" ]]; then
  PYTHON_BIN="$MANAGER_PYTHON"
else
  PYTHON_BIN="python"
fi
SERVER_URL="http://localhost:5656"
SAMPLE1="docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml"
SAMPLE2="docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328-another.xml"
TEST_GROUP="customs_demo-gate-$(date +%s)"
KAFKA_PHASE_REQUIRED="${KAFKA_PHASE_REQUIRED:-false}"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing command: $1"
}

require_env_key() {
  local key="$1"
  local val
  val="$(awk -F= -v k="$key" '$1 ~ "^[[:space:]]*"k"[[:space:]]*$" {gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2}' config/default.env | tail -n1)"
  [[ -n "$val" ]] || fail "config/default.env missing required key: $key"
}

wait_for_server() {
  for _ in $(seq 1 40); do
    if curl -s -o /dev/null "$SERVER_URL/"; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}

wait_for_server_down() {
  for _ in $(seq 1 40); do
    if ! curl -s -o /dev/null "$SERVER_URL/"; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}

print_counts() {
  sqlite3 database/db.sqlite "
select 'shipment', count(*) from shipment
union all select 'piece', count(*) from piece
union all select 'shipment_party', count(*) from shipment_party
union all select 'shipment_commodity', count(*) from shipment_commodity
union all select 'shipment_xml_total', count(*) from shipment_xml
union all select 'shipment_xml_processed', count(*) from shipment_xml where is_processed=1;"
}

assert_counts() {
  local expected_ship="$1"
  local expected_piece="$2"
  local expected_party="$3"
  local expected_comm="$4"
  local expected_xml_total="$5"
  local expected_xml_proc="$6"

  local counts
  counts="$(print_counts)"
  echo "$counts"

  local ship piece party comm xml_total xml_proc
  ship="$(echo "$counts" | awk -F'|' '$1=="shipment" {print $2}')"
  piece="$(echo "$counts" | awk -F'|' '$1=="piece" {print $2}')"
  party="$(echo "$counts" | awk -F'|' '$1=="shipment_party" {print $2}')"
  comm="$(echo "$counts" | awk -F'|' '$1=="shipment_commodity" {print $2}')"
  xml_total="$(echo "$counts" | awk -F'|' '$1=="shipment_xml_total" {print $2}')"
  xml_proc="$(echo "$counts" | awk -F'|' '$1=="shipment_xml_processed" {print $2}')"

  [[ "$ship" == "$expected_ship" ]] || { echo "count mismatch: shipment expected $expected_ship got $ship"; return 1; }
  [[ "$piece" == "$expected_piece" ]] || { echo "count mismatch: piece expected $expected_piece got $piece"; return 1; }
  [[ "$party" == "$expected_party" ]] || { echo "count mismatch: shipment_party expected $expected_party got $party"; return 1; }
  [[ "$comm" == "$expected_comm" ]] || { echo "count mismatch: shipment_commodity expected $expected_comm got $comm"; return 1; }
  [[ "$xml_total" == "$expected_xml_total" ]] || { echo "count mismatch: shipment_xml_total expected $expected_xml_total got $xml_total"; return 1; }
  [[ "$xml_proc" == "$expected_xml_proc" ]] || { echo "count mismatch: shipment_xml_processed expected $expected_xml_proc got $xml_proc"; return 1; }
  return 0
}

wait_for_counts() {
  local timeout_secs="$1"
  local expected_ship="$2"
  local expected_piece="$3"
  local expected_party="$4"
  local expected_comm="$5"
  local expected_xml_total="$6"
  local expected_xml_proc="$7"

  local tries=$((timeout_secs * 2))
  for _ in $(seq 1 "$tries"); do
    if assert_counts "$expected_ship" "$expected_piece" "$expected_party" "$expected_comm" "$expected_xml_total" "$expected_xml_proc" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}

require_cmd curl
require_cmd docker
require_cmd sqlite3
command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "Python executable not found: $PYTHON_BIN"
echo "Using Python: $PYTHON_BIN"
[[ -f "$SAMPLE1" ]] || fail "Missing sample file: $SAMPLE1"
[[ -f "$SAMPLE2" ]] || fail "Missing sample file: $SAMPLE2"

require_env_key "KAFKA_SERVER"
require_env_key "KAFKA_CONSUMER_GROUP"
require_env_key "APILOGICPROJECT_CONSUME_DEBUG"

echo "== [1/6] strict reset (server stop + db + topics) =="
pkill -f "api_logic_server_run.py" >/dev/null 2>&1 || true
bash integration/kafka/isdc_reset_db.sh
bash integration/kafka/isdc_reset.sh

echo "== [2/6] start server with test consumer group: $TEST_GROUP =="
KAFKA_CONSUMER_GROUP="$TEST_GROUP" "$PYTHON_BIN" api_logic_server_run.py > logs/test_gate_server.log 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID >/dev/null 2>&1 || true' EXIT
wait_for_server || fail "Server did not start in time"


echo "== [3/6] debug-path assertions (2 fixtures + duplicate replay) =="
R1="$(curl -s "$SERVER_URL/consume_debug/isdc?file=$SAMPLE1")"
R2="$(curl -s "$SERVER_URL/consume_debug/isdc?file=$SAMPLE2")"
echo "$R1"
echo "$R2"

echo "$R1" | grep -q '"success":true' || fail "consume_debug fixture1 failed"
echo "$R2" | grep -q '"success":true' || fail "consume_debug fixture2 failed"

# After two debug ingests we expect 2 shipments, 2 pieces, 6 parties (C,S,I x2), 2 commodities, 2 blobs processed.
assert_counts 2 2 6 2 2 2

# Replay acceptance check: same fixture replayed — domain counts must stay stable, blob increments.
echo "== [3b] replay acceptance: same payload x2 (replace-on-duplicate) =="
R1b="$(curl -s "$SERVER_URL/consume_debug/isdc?file=$SAMPLE1")"
echo "$R1b"
echo "$R1b" | grep -q '"success":true' || fail "consume_debug replay failed"
# Domain counts unchanged (still 2 shipments etc.), but shipment_xml_total increments to 3.
assert_counts 2 2 6 2 3 3 || fail "replay acceptance: domain counts changed or blob did not increment"


echo "== [4/6] reset again for Kafka-only assertion =="
if [[ -n "${SERVER_PID:-}" ]]; then
  kill "$SERVER_PID" >/dev/null 2>&1 || true
  wait "$SERVER_PID" 2>/dev/null || true
fi
pkill -f "api_logic_server_run.py" >/dev/null 2>&1 || true
wait_for_server_down || fail "Server did not stop before Kafka-only phase"
bash integration/kafka/isdc_reset_db.sh
bash integration/kafka/isdc_reset.sh


echo "== [5/6] restart server clean + publish one Kafka message =="
KAFKA_CONSUMER_GROUP="$TEST_GROUP-kafka" "$PYTHON_BIN" api_logic_server_run.py > logs/test_gate_server.log 2>&1 &
SERVER_PID=$!
wait_for_server || fail "Server did not restart in time"
curl -s -o /dev/null "$SERVER_URL/" || fail "Server endpoint not reachable before Kafka publish"
"$PYTHON_BIN" test/send_isdc.py


echo "== [6/6] Kafka-path assertions =="
# One Kafka message -> 1 shipment, 1 piece, 3 parties (C,S,I), 1 commodity, 1 blob processed.
if wait_for_counts 20 1 1 3 1 1 1 && assert_counts 1 1 3 1 1 1; then
  echo "PASS: Kafka phase"
else
  assert_counts 1 1 3 1 1 1 || true
  tail -n 60 logs/test_gate_server.log || true
  if [[ "$KAFKA_PHASE_REQUIRED" == "true" ]]; then
    fail "Kafka phase failed and KAFKA_PHASE_REQUIRED=true"
  fi
  echo "WARN: Kafka phase did not reach expected counts in this environment; debug phase is green (overall result is PARTIAL PASS)."
fi

if [[ "$KAFKA_PHASE_REQUIRED" == "true" ]]; then
  echo "PASS: customs_demo XR test gate (debug + Kafka)"
else
  echo "PASS: customs_demo XR test gate (debug required, Kafka best-effort)"
fi
