from django.db import transaction
from system.models import PortfolioPosition, PortfolioSummary
from system.services.risk_service import RiskService


class PortfolioService:

    @staticmethod
    @transaction.atomic
    def update_position(symbol, position_size, price):

        exposure = position_size * price
        risk = RiskService.get_config()

        summary = PortfolioSummary.objects.select_for_update().first()

        if not summary:
            raise Exception("PortfolioSummary not initialized.")

        # Current asset exposure
        existing_position = PortfolioPosition.objects.filter(symbol=symbol).first()
        current_asset_exposure = existing_position.exposure if existing_position else 0.0

        new_asset_exposure = exposure
        new_total_exposure = summary.used_capital - current_asset_exposure + new_asset_exposure

        max_asset_allowed = risk["total_capital"] * risk["max_exposure_per_asset"]
        max_total_allowed = risk["total_capital"] * risk["max_total_exposure"]

        # Rule 1: Asset-level cap
        if new_asset_exposure > max_asset_allowed:
            raise Exception("Asset exposure limit exceeded.")

        # Rule 2: Portfolio-level cap
        if new_total_exposure > max_total_allowed:
            raise Exception("Total portfolio exposure limit exceeded.")

        # Rule 3: Free capital check
        if exposure > summary.free_capital:
            raise Exception("Insufficient free capital.")

        # --- SAFE TO UPDATE ---

        position, created = PortfolioPosition.objects.get_or_create(symbol=symbol)
        position.position_size = position_size
        position.average_price = price
        position.exposure = exposure
        position.save()

        summary.used_capital = sum(
            p.exposure for p in PortfolioPosition.objects.all()
        )
        summary.free_capital = summary.total_capital - summary.used_capital
        summary.total_exposure = summary.used_capital
        summary.save()

        return {
            "symbol": symbol,
            "position_size": position_size,
            "exposure": exposure,
            "used_capital": summary.used_capital,
            "free_capital": summary.free_capital,
        }