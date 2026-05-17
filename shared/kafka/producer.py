from kafka import KafkaProducer

from shared.config.settings import settings
from shared.kafka.serializer import serialize_event


class KafkaEventProducer:

    def __init__(self):

        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )

    def send_event(self, topic, event):

        self.producer.send(
            topic,
            serialize_event(event)
        )

        self.producer.flush()