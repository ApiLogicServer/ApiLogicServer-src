#!/usr/bin/env bash
set -euo pipefail

docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic isdc >/dev/null 2>&1 || true
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic isdc_processed >/dev/null 2>&1 || true
sleep 3
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic isdc --partitions 1 --replication-factor 1 >/dev/null
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic isdc_processed --partitions 1 --replication-factor 1 >/dev/null
echo "Kafka topics reset complete: isdc, isdc_processed"
