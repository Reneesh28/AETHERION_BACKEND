from shared.schemas.market import (
    MarketTickEvent,
    TickPayload,
)

from shared.utils.ids import (
    generate_event_id,
    generate_trace_id,
)

from shared.utils.time import utc_now


class TickNormalizer:

    @staticmethod
    def normalize_binance_trade(
        raw_event: dict
    ) -> MarketTickEvent:

        payload = TickPayload(
            price=float(raw_event["p"]),
            quantity=float(raw_event["q"]),
            side=(
                "sell"
                if raw_event["m"]
                else "buy"
            ),
            trade_id=str(raw_event["t"]),
        )

        event = MarketTickEvent(
            event_id=generate_event_id(),

            trace_id=generate_trace_id(),

            event_type="market.tick.raw",

            service_name="ingestion_service",

            source="binance",

            event_time=utc_now(),

            symbol=raw_event["s"],

            payload=payload,
        )

        return event