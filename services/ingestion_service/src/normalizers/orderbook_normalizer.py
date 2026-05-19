from shared.schemas.market import (
    MarketOrderBookEvent,
    OrderBookPayload,
)

from shared.utils.ids import (
    generate_event_id,
    generate_trace_id,
)

from shared.utils.time import utc_now


class OrderBookNormalizer:

    @staticmethod
    def normalize_binance_orderbook(
        raw_event: dict
    ) -> MarketOrderBookEvent:

        best_bid = raw_event["bids"][0]

        best_ask = raw_event["asks"][0]

        bid_price = float(best_bid[0])

        ask_price = float(best_ask[0])

        payload = OrderBookPayload(
            bid_price=bid_price,
            ask_price=ask_price,
            bid_quantity=float(best_bid[1]),
            ask_quantity=float(best_ask[1]),
            spread=ask_price - bid_price,
        )

        event = MarketOrderBookEvent(
            event_id=generate_event_id(),

            trace_id=generate_trace_id(),

            event_type="market.orderbook.raw",

            service_name="ingestion_service",

            source="binance",

            event_time=utc_now(),

            symbol=raw_event["symbol"],

            payload=payload,
        )

        return event