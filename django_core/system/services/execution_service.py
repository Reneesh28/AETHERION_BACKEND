import requests
from system.services.risk_service import RiskService
from system.services.portfolio_service import PortfolioService


FASTAPI_URL = "http://127.0.0.1:8000/api/position/size"


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

        # 🔥 Now enforce exposure + update portfolio
        return PortfolioService.update_position(
            symbol=symbol,
            position_size=sizing_result["position_size"],
            price=price
        )