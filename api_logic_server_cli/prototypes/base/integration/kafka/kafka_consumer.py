"""
Invoked at server start (api_logic_server_run.py -> config/setup.py)

Listen/consume Kafka topics, if KAFKA_CONSUMER specified in Config.py

DO NOT add topic handlers here.  Instead, create a file in:
    integration/kafka/kafka_discovery/

Each file must expose:  def register(bus): ...
It will be auto-discovered and registered before bus.run().

See: integration/kafka/kafka_discovery/auto_discovery.py
"""

from config.config import Args
try:
    from confluent_kafka import Producer, KafkaException, Consumer
except ImportError:
    Producer = None
    KafkaException = None
    Consumer = None
    # Kafka support not available on this platform
import logging
import safrs
from threading import Event
from integration.system.FlaskKafka import FlaskKafka
from integration.kafka.kafka_discovery.auto_discovery import discover_topic_handlers


logger = logging.getLogger('integration.kafka')
if Consumer is None:
    logger.fatal("SEVERE WARNING - KAFKA NOT AVAILABLE FOR IMPORT - DISABLED")
else:
    logger.debug("kafka_consumer imported")


def kafka_consumer(safrs_api: safrs.SAFRSAPI = None):
    """
    Called by api_logic_server_run to listen on Kafka.
    Enabled by config.KAFKA_CONSUMER.
    Topic handlers are discovered from integration/kafka/kafka_discovery/*.py
    """

    if not Args.instance.kafka_consumer:
        logger.debug(f'Kafka Consumer not activated')
        return

    conf = Args.instance.kafka_consumer
    logger.debug(f'\nKafka Consumer configured, starting')

    INTERRUPT_EVENT = Event()
    bus = FlaskKafka(interrupt_event=INTERRUPT_EVENT, conf=conf, safrs_api=safrs_api)

    discover_topic_handlers(bus)   # scans kafka_discovery/*.py, calls register(bus) on each

    bus.run()   # MUST be after all register() calls — subscribes to discovered topics

    logger.debug(f'Kafka Listener thread activated {bus}')

