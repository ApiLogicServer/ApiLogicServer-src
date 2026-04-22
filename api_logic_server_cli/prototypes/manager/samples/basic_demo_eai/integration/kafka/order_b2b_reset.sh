#!/usr/bin/env bash
# integration/kafka/order_b2b_reset.sh — reset Kafka topics and log for the order_b2b pipeline.
# Run from project root: bash integration/kafka/order_b2b_reset.sh

set -e

# Truncate log
if [ -f logs/als.log ]; then > logs/als.log && echo "Log cleared."; fi

# Delete + recreate topics so consumer offsets start fresh
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic order_b2b --delete --if-exists || true
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic order_b2b_processed --delete --if-exists || true
sleep 2
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic order_b2b
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic order_b2b_processed
echo "Kafka topics reset."

# ---------------------------------------------------------------------------
# Useful inspection commands (run manually):
# ---------------------------------------------------------------------------
# List all topics:
#   docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
#
# Read order_b2b topic from the beginning:
#   docker exec broker1 /opt/kafka/bin/kafka-console-consumer.sh \
#     --bootstrap-server localhost:9092 --topic order_b2b --from-beginning --group fresh-group-1
#
# Publish a test message (compact JSON to single line first):
#   jq -c . docs/requirements/demo-eai/message_formats/order_b2b.json | docker exec -i broker1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic order_b2b
#
# NOTE: increment fresh-group-N each time to avoid offset-skipping on re-reads.
#
# Clone/rename guidance:
#   For copied projects, update KAFKA_CONSUMER_GROUP in config/default.env to a
#   project-unique name to avoid rebalancing conflicts with other running services.
