from services.ingestion_service.src.normalizers.tick_normalizer import (
    TickNormalizer,
)


class NormalizationService:

    @staticmethod
    def normalize_trade_event(
        raw_event: dict
    ):

        return (
            TickNormalizer
            .normalize_binance_trade(
                raw_event
            )
        )