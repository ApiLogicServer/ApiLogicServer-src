"""
EAI debug endpoints (development only)
======================================
Generic engine for testing a Kafka subscribe pipeline by hand or from tests, with or without a broker.
Each pipeline's thin file in api/api_discovery/ (e.g. order_b2b_kafka_consume_debug.py) calls:

    register_consume_debug(app, topic, simulate, ...)   GET  /consume_debug/<topic>?file=...&mode=auto|simulated|live
    register_queue_reset(app, name, topics, ...)        POST /consume_debug/<name>/reset

consume_debug - send a message from a file:
    simulated  No broker needed.  Calls `simulate(payload, session)`, which runs the same parse-and-save function the
               live consumer uses, in one transaction.  Kafka is not involved.  The response has the outcome.
    live       Publishes the file's contents to the topic with the server's own producer and returns when the broker
               acknowledges it - like any sender.  Processing is asynchronous (Consumer 1, the row-event bridge,
               Consumer 2); see logs/als.log, or query the pipeline's blob table (`outcome_hint`).
    auto       (default) live when a producer AND a consumer are configured (KAFKA_SERVER, KAFKA_CONSUMER_GROUP) and
               the broker answers; otherwise simulated.  The response always says which one ran ("mode").

reset - purge the pipeline's topics (messages only; the topics, consumers and offsets stay in place), so a test run
    starts from an empty queue and a server restart replays nothing.  Without a broker there is nothing to purge.

Both are enabled only when APILOGICPROJECT_CONSUME_DEBUG is true / 1 / yes / on (config/default.env).  false, 0 or unset
leaves them unregistered.  They have NO authentication (and the reset is destructive): development and demo only.

version: 1.0 (October 2026)
"""
import logging
import os
from pathlib import Path

import safrs
from flask import request, jsonify

app_logger = logging.getLogger("api_logic_server_app")


def debug_enabled() -> bool:
    """ APILOGICPROJECT_CONSUME_DEBUG true / 1 / yes / on turns the endpoints on; false, 0, empty or unset leaves them off """
    return os.getenv('APILOGICPROJECT_CONSUME_DEBUG', '').strip().lower() in ('1', 'true', 'yes', 'on')


def kafka_unavailable_reason(consumer_needed: bool = True) -> str:
    """ why live Kafka cannot be used right now ("" when it can): needs a producer, (a consumer,) and a broker that answers """
    import integration.kafka.kafka_producer as kafka_producer
    from config.config import Args
    if kafka_producer.producer is None:
        return "KAFKA_SERVER is not set (Kafka is in fallback mode)"
    if consumer_needed and not Args.instance.kafka_consumer:
        return "KAFKA_CONSUMER_GROUP is not set, so nothing would consume the message"
    if not kafka_producer.kafka_available():
        return "the broker does not answer"
    return ""


def _broker() -> str:
    import integration.kafka.kafka_producer as kafka_producer
    return (kafka_producer.conf or {}).get("bootstrap.servers", "")


def register_consume_debug(app, topic: str, simulate, port=5656, sample_file: str = "",
                           outcome_hint: str = "") -> None:
    """
    Register GET /consume_debug/<topic> (see module docstring).

    Args:
        topic:        the inbound topic, e.g. "order_b2b"
        simulate:     function(payload: str, session) -> dict; runs the live consumer's parse-and-save function and
                      returns what to report (e.g. {"blob_id": 3, "order_id": 7}); raises on failure
        port:         the server port, for the copy-paste curl lines in the log
        sample_file:  default file for those curl lines
        outcome_hint: how to see the result of a live message (shown in the live response)
    """
    if not debug_enabled():
        return
    url = f"http://localhost:{port}/consume_debug/{topic}"
    sample = sample_file or "<path/to/message.json>"

    @app.route(f"/consume_debug/{topic}", endpoint=f"consume_debug_{topic}")
    def consume_debug():
        """ EAI debug: sends the message in ?file= to the topic, live through Kafka or simulated """
        file_path = request.args.get("file")
        mode = request.args.get("mode", "auto")
        if not file_path:
            return jsonify({"success": False, "message": "Missing ?file= parameter"}), 400
        if mode not in ("auto", "simulated", "live"):
            return jsonify({"success": False, "message": "mode must be auto, simulated or live"}), 400
        try:
            payload = Path(file_path).read_text()
        except OSError as e:
            return jsonify({"success": False, "topic": topic, "error": str(e)}), 400

        why_not = "" if mode == "simulated" else kafka_unavailable_reason()
        if mode == "live" and why_not:
            return jsonify({"success": False, "mode": "live", "topic": topic,
                            "error": f"live mode requested, but {why_not}"}), 409
        if mode != "simulated" and not why_not:
            return _publish_live(topic, payload, file_path, outcome_hint)
        return _simulate(topic, simulate, payload, file_path, note=why_not if mode == "auto" else "")

    app_logger.info(f"consume_debug enabled for topic {topic} (no authentication - development only). Copy/paste:\n"
                    f"  curl \"{url}?file={sample}\"                # live Kafka if a broker is up, else simulated\n"
                    f"  curl \"{url}?file={sample}&mode=simulated\"  # no Kafka\n"
                    f"  curl \"{url}?file={sample}&mode=live\"       # error 409 if Kafka is not available")


def register_queue_reset(app, name: str, topics: list, port=5656) -> None:
    """
    Register POST /consume_debug/<name>/reset: purge the messages in `topics` (see module docstring).

    Args:
        name:    the pipeline's name (its first topic), used in the URL
        topics:  every topic of the pipeline, e.g. ["order_b2b", "order_b2b_processed"]
    """
    if not debug_enabled():
        return

    @app.route(f"/consume_debug/{name}/reset", methods=["POST"], endpoint=f"consume_debug_reset_{name}")
    def consume_debug_reset():
        """ EAI debug: purges the messages in the pipeline's topics (the topics and consumers stay) """
        why_not = kafka_unavailable_reason(consumer_needed=False)
        if why_not:
            return jsonify({"success": True, "mode": "simulated", "purged": {},
                            "note": f"nothing to purge: {why_not}"})
        try:
            return jsonify({"success": True, "mode": "live", "broker": _broker(), "purged": _purge(topics)})
        except Exception as e:
            app_logger.error(f"consume_debug reset {name}: {e}", exc_info=True)
            return jsonify({"success": False, "mode": "live", "error": str(e)}), 500

    app_logger.info(f"consume_debug reset enabled for topics {topics} (destructive, no authentication). Copy/paste:\n"
                    f"  curl -X POST \"http://localhost:{port}/consume_debug/{name}/reset\"")


def _publish_live(topic: str, payload: str, file_path: str, outcome_hint: str):
    """ publish the message to the topic; return when the broker acknowledges it """
    import integration.kafka.kafka_producer as kafka_producer
    outcome = {}

    def delivered(err, msg):
        outcome.update(error=str(err) if err else None,
                       partition=None if err else msg.partition(), offset=None if err else msg.offset())

    kafka_producer.producer.produce(topic, value=payload.encode("utf-8"), callback=delivered)
    kafka_producer.producer.flush(timeout=10)
    if outcome.get("error") or "offset" not in outcome:
        kafka_producer.mark_unavailable()
        app_logger.error(f"consume_debug {topic}: not delivered: {outcome}")
        return jsonify({"success": False, "mode": "live", "topic": topic,
                        "error": outcome.get("error") or "no delivery report within 10 s"}), 502
    app_logger.info(f"consume_debug {topic}: published (partition {outcome['partition']}, offset {outcome['offset']}); "
                    f"processing is asynchronous - see the lines that follow")
    return jsonify({"success": True, "mode": "live", "published": True, "topic": topic, "broker": _broker(),
                    "file": file_path, "partition": outcome["partition"], "offset": outcome["offset"],
                    "next": "processing is asynchronous: see logs/als.log" + (f", or {outcome_hint}" if outcome_hint else "")})


def _simulate(topic: str, simulate, payload: str, file_path: str, note: str = ""):
    """ run the live consumer's parse-and-save function directly; no Kafka """
    base = {"mode": "simulated", "published": False, "topic": topic, "file": file_path}
    if note:
        base["note"] = f"simulated because {note}"
    try:
        return jsonify({**base, "success": True, **simulate(payload, safrs.DB.session)})
    except Exception as e:
        app_logger.error(f"consume_debug {topic}: {e}", exc_info=True)
        return jsonify({**base, "success": False, "error": str(e)}), 500


def _purge(topics: list) -> dict:
    """ delete every message currently in the topics (to the high watermark); returns {topic: messages purged} """
    from confluent_kafka import Consumer, TopicPartition
    from confluent_kafka.admin import AdminClient
    conf = {"bootstrap.servers": _broker()}
    admin = AdminClient(conf)
    if not hasattr(admin, "delete_records"):
        raise RuntimeError("purging needs a newer confluent-kafka (AdminClient.delete_records)")
    watermarks = Consumer({**conf, "group.id": "eai-debug-reset", "enable.auto.commit": False})
    try:
        metadata = admin.list_topics(timeout=5)
        purged, to_delete = {}, []
        for each in topics:
            topic_metadata = metadata.topics.get(each)
            if topic_metadata is None or topic_metadata.error is not None:
                purged[each] = "topic does not exist"
                continue
            purged[each] = 0
            for partition in topic_metadata.partitions:
                low, high = watermarks.get_watermark_offsets(TopicPartition(each, partition), timeout=5)
                if high > low:
                    to_delete.append(TopicPartition(each, partition, high))
                    purged[each] += high - low
        if to_delete:
            for future in admin.delete_records(to_delete).values():
                future.result(timeout=10)
        return purged
    finally:
        watermarks.close()
