#!/usr/bin/env bash
# integration/kafka/order_b2b_reset.sh — reset Kafka topics and log for the order_b2b pipeline.
# Run from project root: bash integration/kafka/order_b2b_reset.sh

set -e

CONTAINER_CLI=$(command -v docker >/dev/null 2>&1 && echo docker || echo podman)
BROKER_CONTAINER=${BROKER_CONTAINER:-broker1}
BROKER_BOOTSTRAP=${BROKER_BOOTSTRAP:-localhost:9092}
TOPICS="$CONTAINER_CLI exec $BROKER_CONTAINER /opt/kafka/bin/kafka-topics.sh --bootstrap-server $BROKER_BOOTSTRAP"

# Truncate log
if [ -f logs/als.log ]; then > logs/als.log && echo "Log cleared."; fi

# Delete + recreate topics so consumer offsets start fresh
$TOPICS --topic order_b2b --delete --if-exists || true
$TOPICS --topic order_b2b_processed --delete --if-exists || true
sleep 2
$TOPICS --create --replication-factor 1 --partitions 1 --topic order_b2b
$TOPICS --create --replication-factor 1 --partitions 1 --topic order_b2b_processed
echo "Kafka topics reset."

