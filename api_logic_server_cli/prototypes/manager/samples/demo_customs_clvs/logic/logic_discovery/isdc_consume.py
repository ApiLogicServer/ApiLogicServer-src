"""
Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.
...
(Step 1 — EAI row_event bridge: after ShipmentXml insert, publish blob.id to isdc_processed)
"""

from logic_bank.logic_bank import Rule
from database import models
import integration.kafka.kafka_producer as kafka_producer


def declare_logic():

    def _publish_isdc_processed(row: models.ShipmentXml, old_row: models.ShipmentXml, logic_row):
        """Publish ShipmentXml.id to isdc_processed topic so Consumer 2 can parse the blob."""
        if not row.is_processed:
            kafka_producer.publish_kafka_message(topic='isdc_processed', logic_row=logic_row)

    Rule.after_flush_row_event(on_class=models.ShipmentXml, calling=_publish_isdc_processed)
