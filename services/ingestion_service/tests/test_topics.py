from src.kafka.topic_router import TopicRouter


def test_topic_router():

    assert (
        TopicRouter.get_tick_topic()
        == "market.tick.raw"
    )

    assert (
        TopicRouter.get_orderbook_topic()
        == "market.orderbook.raw"
    )