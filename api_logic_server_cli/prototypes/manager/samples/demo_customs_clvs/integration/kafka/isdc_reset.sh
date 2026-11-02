#!/usr/bin/env bash
# integration/kafka/isdc_reset.sh - reset Kafka topics and log for the isdc pipeline.
# Run from project root: bash integration/kafka/isdc_reset.sh
#
# WARNING: deletes and recreates topics isdc and isdc_processed on the broker, losing their messages (and any other
#          project using the same topic names on that broker). To purge messages WITHOUT deleting the topics, use
#          the debug endpoint instead: curl -X POST http://localhost:5656/consume_debug/isdc/reset
# Broker container: BROKER_CONTAINER (default broker1); bootstrap server inside it: BROKER_BOOTSTRAP (default localhost:9092).
set -e
CONTAINER_CLI=$(command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1 && echo docker || echo podman)
BROKER_CONTAINER=${BROKER_CONTAINER:-broker1}
BROKER_BOOTSTRAP=${BROKER_BOOTSTRAP:-localhost:9092}
TOPICS="$CONTAINER_CLI exec $BROKER_CONTAINER /opt/kafka/bin/kafka-topics.sh --bootstrap-server $BROKER_BOOTSTRAP"

if [ -f logs/als.log ]; then > logs/als.log && echo "Log cleared."; fi

$TOPICS --topic isdc --delete --if-exists >/dev/null 2>&1 || true
$TOPICS --topic isdc_processed --delete --if-exists >/dev/null 2>&1 || true
sleep 3
$TOPICS --create --if-not-exists --replication-factor 1 --partitions 1 --topic isdc >/dev/null
$TOPICS --create --if-not-exists --replication-factor 1 --partitions 1 --topic isdc_processed >/dev/null
echo "Kafka topics reset complete: isdc, isdc_processed"
