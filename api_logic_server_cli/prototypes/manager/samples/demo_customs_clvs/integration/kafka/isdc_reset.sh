#!/usr/bin/env bash
set -euo pipefail

# Docker or Podman -- whichever is installed (same broker1 container either way)
CONTAINER_CLI=$(command -v docker >/dev/null 2>&1 && echo docker || echo podman)

$CONTAINER_CLI exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic isdc >/dev/null 2>&1 || true
$CONTAINER_CLI exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic isdc_processed >/dev/null 2>&1 || true
sleep 3
$CONTAINER_CLI exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic isdc --partitions 1 --replication-factor 1 >/dev/null
$CONTAINER_CLI exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic isdc_processed --partitions 1 --replication-factor 1 >/dev/null
echo "Kafka topics reset complete: isdc, isdc_processed"
