"""

Invoked at server start (api_logic_server_run.py)

Connect to Kafka, if KAFKA_CONNECT specified in Config.py

"""
from config import Args
from confluent_kafka import Producer, KafkaException, Consumer
import signal
import logging
import json
import socket
import safrs
from threading import Event
from integration.system.FlaskKafka import FlaskKafka


conf = None

logger = logging.getLogger('integration.kafka')
logger.debug("kafka_producer imported")
pass


def kafka_consumer(safrs_api: safrs.SAFRSAPI = None):
    """
    Called by api_logic_server_run to listen on kafka

    Enabled by config.KAFKA_CONSUMER

    Args:
        app (Flask): flask_app
    """

    if not Args.instance.kafka_consumer:
        logger.debug(f'Kafka Consumer not activated')
        return

    conf = Args.instance.kafka_consumer
    # conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
    logger.debug(f'\nKafka producer configured')

    
    if "client.id" not in conf:
        conf["client.id"] = socket.gethostname()
    # conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
    logger.debug(f'\nKafka producer starting')


    INTERRUPT_EVENT = Event()

    bus = FlaskKafka(interrupt_event=INTERRUPT_EVENT, conf=conf, safrs_api=safrs_api)
    
    bus.run()

    logger.debug(f'Kafka Listener activated {bus}')


    @bus.handle('order_shipping')
    def order_shipping(msg: object, safrs_api: safrs.SAFRSAPI):
        logger.debug("consumed {} from order_shipping topic consumer".format(msg))
        message_data = msg.value() .decode("utf-8")
        # Assuming the JSON message has a 'message_id' and 'message data' f
        json_message = json.loads(message_data)
        message_id = json_message.get('message_id')
        message_data = json_message.get( 'message_data' )
        # TODO: create/use an IntegrationService to map message and insert row
        logger.debug(f'Received and persisted message with ID: (message_data)')
        pass

    # FIXME multiple topics fail -- @bus.handle('another_topic')
    def another_topic_handler(msg):
        print("consumed {} from another_topic topic consumer".format(msg))
        pass
