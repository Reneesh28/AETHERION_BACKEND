import requests
from system.services.risk_service import RiskService
from system.services.portfolio_service import PortfolioService
from system.models import TradeExecution

FASTAPI_URL = "http://127.0.0.1:8001/api/position/size"


class ExecutionService:
    @staticmethod
    def execute_trade(symbol, price, atr):
        risk_config = RiskService.get_config()
        payload = {
            "price": price,
            "atr": atr,
            "risk_config": risk_config
        }
        response = requests.post(FASTAPI_URL, json=payload)
        if response.status_code != 200:
            raise Exception("Position sizing engine error")
        sizing_result = response.json()
        # Now enforce exposure + update portfolio
        portfolio_result = PortfolioService.update_position(
            symbol=symbol,
            position_size=sizing_result["position_size"],
            price=price
        )
        
        TradeExecution.objects.create(
            symbol=symbol,
            action="BUY" if sizing_result["position_size"] > 0 else "SELL",
            position_size=abs(sizing_result["position_size"]),
            price=price,
            capital_allocated=abs(sizing_result["position_size"] * price),
            meta_regime="UNKNOWN",  # Not passed yet — governance safe default
            strategy="AUTO",        # No strategy logic touched
            )
        return portfolio_result