#!/usr/bin/env bash
# integration/kafka/isdc_reset.sh — reset Kafka topics and log for the ISDC pipeline.
# Run from project root: bash integration/kafka/isdc_reset.sh

set -e

if [ -f logs/als.log ]; then > logs/als.log && echo "Log cleared."; fi

docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic isdc --delete --if-exists || true
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic isdc_processed --delete --if-exists || true
sleep 2
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic isdc
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic isdc_processed
echo "Kafka topics reset: isdc, isdc_processed"

# Useful inspection commands (run manually):
#   docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
#   docker exec broker1 /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic isdc --from-beginning --group fresh-group-1
#   Clone/rename: set KAFKA_CONSUMER_GROUP in config/default.env to a project-unique name.
