#!/usr/bin/env bash
# integration/kafka/order_b2b_reset.sh — reset Kafka topics and log for the order_b2b pipeline.
# Run from project root: bash integration/kafka/order_b2b_reset.sh
#
# WARNING: deletes and recreates topics order_b2b and order_b2b_processed on the broker, losing their messages (and any
#          other project using the same topic names on that broker). To purge messages WITHOUT deleting the topics, use
#          the debug endpoint instead: curl -X POST http://localhost:5656/consume_debug/order_b2b/reset
# Broker container: BROKER_CONTAINER (default broker1); bootstrap server inside it: BROKER_BOOTSTRAP (default localhost:9092).

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

# Useful inspection commands (substitute `podman` for `docker` if that's what's installed):
#   docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
#   docker exec broker1 /opt/kafka/bin/kafka-console-consumer.sh \
#     --bootstrap-server localhost:9092 --topic order_b2b --from-beginning --group fresh-group-1
#   (increment the group number each time - Kafka tracks the last-read offset per consumer group)
