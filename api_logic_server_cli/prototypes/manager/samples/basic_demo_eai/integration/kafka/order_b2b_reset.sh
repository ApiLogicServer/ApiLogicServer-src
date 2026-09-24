#!/usr/bin/env bash
# integration/kafka/order_b2b_reset.sh — reset Kafka topics and log for the order_b2b pipeline.
# Run from project root: bash integration/kafka/order_b2b_reset.sh

set -e

# Docker or Podman -- whichever is installed (same broker1 container either way)
CONTAINER_CLI=$(command -v docker >/dev/null 2>&1 && echo docker || echo podman)

# Truncate log
if [ -f logs/als.log ]; then > logs/als.log && echo "Log cleared."; fi

# Delete + recreate topics so consumer offsets start fresh
$CONTAINER_CLI exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic order_b2b --delete --if-exists || true
$CONTAINER_CLI exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic order_b2b_processed --delete --if-exists || true
sleep 2
$CONTAINER_CLI exec broker1 /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic order_b2b
$CONTAINER_CLI exec broker1 /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic order_b2b_processed
echo "Kafka topics reset."
