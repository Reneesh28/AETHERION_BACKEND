import requests

FASTAPI_STRATEGY_URL = "http://127.0.0.1:8001/api/decision/latest"

class StrategyService:

    @staticmethod
    def get_current_strategy():
        """
        Calls FastAPI strategy service and returns latest decision.
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

            return response.json(), 200

        except requests.exceptions.RequestException as e:
            return {
                "error": "Strategy service unavailable.",
                "details": str(e)
            }, 503