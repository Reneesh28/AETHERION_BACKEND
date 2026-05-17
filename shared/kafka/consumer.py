import json

from kafka import KafkaConsumer

from shared.config.settings import settings


class KafkaEventConsumer:

    def __init__(self, topic):

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset="earliest",
            group_id="aetherion-group"
        )

    def listen(self):

        for message in self.consumer:

            yield json.loads(
                message.value.decode("utf-8")
            )