import requests
from .broadcast_service import BroadcastService

FASTAPI_STRATEGY_URL = "http://127.0.0.1:8001/api/decision/latest"

class StrategyService:

    _last_broadcasted_strategy = None  # In-memory debounce

    @staticmethod
    def get_current_strategy():
        """
        Calls FastAPI strategy service and returns latest decision.
        Automatically broadcasts strategy updates if changed.
        """

        try:
            response = requests.get(
                FASTAPI_STRATEGY_URL,
                timeout=5
            )

            if response.status_code != 200:
                return {
                    "error": "Strategy service error.",
                    "details": response.json()
                }, response.status_code

            strategy_data = response.json()

            # 🔥 Broadcast only if strategy changed
            if strategy_data != StrategyService._last_broadcasted_strategy:
                print("🔥 STRATEGY BROADCAST TRIGGERED")

                BroadcastService.send(
                    channel="strategy",
                    data=strategy_data
                )

                StrategyService._last_broadcasted_strategy = strategy_data

            return strategy_data, 200

        except requests.exceptions.RequestException as e:
            return {
                "error": "Strategy service unavailable.",
                "details": str(e)
            }, 503