from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "system"

    def ready(self):
        # 🔥 Start market snapshot streaming once Django boots
        from .services.market_service import MarketService
        MarketService.start_streaming()