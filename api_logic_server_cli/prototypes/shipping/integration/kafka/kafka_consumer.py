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
from integration.row_dict_maps.OrderToShip import OrderToShip


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
        logger.debug("kafka_consumer#order_shipping receives msg..")
        message_data = msg.value().decode("utf-8")
        msg_dict = json.loads(message_data)
        order_dict = msg_dict['order']
        logger.debug(f' * Processing message: [{str(order_dict)}')
        pass

        db = safrs.DB         # Use the safrs.DB, not db!
        session = db.session  # sqlalchemy.orm.scoping.scoped_session

        order_b2b_def = OrderToShip()
        sql_alchemy_row = order_b2b_def.dict_to_row(row_dict = order_dict, session = session)

        session.add(sql_alchemy_row)
        session.commit()
        logger.debug(f' * Committed Message')


    # FIXME multiple topics fail -- @bus.handle('another_topic')
    def another_topic_handler(msg):
        print("consumed {} from another_topic topic consumer".format(msg))
        pass
