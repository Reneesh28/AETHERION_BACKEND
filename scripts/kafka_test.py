from datetime import datetime

from shared.kafka.producer import KafkaEventProducer
from shared.kafka.consumer import KafkaEventConsumer
from shared.kafka.topics import MARKET_TOPIC

from shared.schemas.market import MarketTickEvent


event = MarketTickEvent(
    trace_id="test-trace",
    event_time=datetime.utcnow(),
    service_name="kafka_test",

    symbol="BTCUSDT",

    price=100000,
    volume=5.0,

    timestamp=str(datetime.utcnow())
)


producer = KafkaEventProducer()

producer.send_event(
    MARKET_TOPIC,
    event
)

print("Event sent successfully")


consumer = KafkaEventConsumer(
    MARKET_TOPIC
)

for message in consumer.listen():

    print("Received message:")
    print(message)

    break