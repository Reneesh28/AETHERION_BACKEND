from system.models import RiskConfiguration


class RiskService:

    @staticmethod
    def get_config():
        config = RiskConfiguration.objects.first()

        if not config:
            raise Exception("RiskConfiguration not initialized.")

        return {
            "total_capital": config.total_capital,
            "risk_per_trade": config.risk_per_trade,
            "max_exposure_per_asset": config.max_exposure_per_asset,
            "max_total_exposure": config.max_total_exposure,
            "atr_multiplier": config.atr_multiplier,
            "kelly_enabled": config.kelly_enabled,
        }