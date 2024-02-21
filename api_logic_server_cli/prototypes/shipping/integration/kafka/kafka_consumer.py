"""
Invoked at server start (api_logic_server_run.py)

Listen/consume Kafka topis, if KAFKA_CONSUMER specified in Config.py

Alter this file to add handlers for consuming kafka topics
"""

from config.config import Args
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
logger.debug("kafka_consumer imported")


def kafka_consumer(safrs_api: safrs.SAFRSAPI = None):
    """
    Called by api_logic_server_run to listen on kafka

    Enabled by config.KAFKA_CONSUMER

    Args:
        app (safrs.SAFRSAPI): safrs_api
    """

    if not Args.instance.kafka_consumer:
        logger.debug(f'Kafka Consumer not activated')
        return

    conf = Args.instance.kafka_consumer
    #  eg, KAFKA_CONSUMER = '{"bootstrap.servers": "localhost:9092", "group.id": "als-default-group1", "auto.offset.reset":"smallest"}'
    logger.debug(f'\nKafka Consumer configured, starting')

    INTERRUPT_EVENT = Event()

    bus = FlaskKafka(interrupt_event=INTERRUPT_EVENT, conf=conf, safrs_api=safrs_api)
    
    bus.run()  # Kafka consumption, threading, handler annotations

    logger.debug(f'Kafka Listener thread activated {bus}')

    '''   Your Code Goes Here
    
    #als: consume Kafka messages
    '''


    @bus.handle('order_shipping')
    def order_shipping(msg: object, safrs_api: safrs.SAFRSAPI):
        """
        Defining this annotated method:

        1. Identifies Kafka topic to listen on
        2. Handles a message instance (here, saves order for shipping)

        Args:
            msg (object): Kafka Message
            safrs_api (safrs.SAFRSAPI): activated safrs server (in Flask)
        """
        logger.debug("kafka_consumer#order_shipping receives msg..")
        message_data = msg.value().decode("utf-8")
        message_id = msg.key()
        msg_dict = json.loads(message_data)
        order_dict = msg_dict['Order']  # Class name of producer object
        logger.debug(f' * Processing message - id: {message_id} msg_dict: {str(order_dict)}')

        with safrs_api.app.app_context():
            db = safrs.DB         # Use the safrs.DB, not db!
            session = db.session  # sqlalchemy.orm.scoping.scoped_session

            order_b2b_def = OrderToShip()
            sql_alchemy_row = order_b2b_def.dict_to_row(row_dict = order_dict, session = session)

            session.add(sql_alchemy_row)
            session.commit()
            logger.debug(f' * processing completed - id: {message_id} msg_dict: {str(order_dict)}')
            logger.debug(f' * sql_alchemy_row  OrderID: {sql_alchemy_row.OrderID}, CustomerID: {sql_alchemy_row.Customer.CustomerID}, Customer.Balance: {sql_alchemy_row.Customer.Balance}')

        logger.debug(f' * kafka_consumer#order_shipping completed\n')


    @bus.handle('another_topic')
    def another_topic_handler(msg: object, safrs_api: safrs.SAFRSAPI):
        print("consumed key: {}, message:{} from another_topic topic consumer".format(msg.key(),msg.value()))
