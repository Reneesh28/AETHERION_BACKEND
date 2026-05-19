from shared.constants.topics import (
    MARKET_TICK_RAW_TOPIC,
    MARKET_ORDERBOOK_RAW_TOPIC,
)


class TopicRouter:

    @staticmethod
    def get_tick_topic() -> str:
        return MARKET_TICK_RAW_TOPIC

    @staticmethod
    def get_orderbook_topic() -> str:
        return MARKET_ORDERBOOK_RAW_TOPIC