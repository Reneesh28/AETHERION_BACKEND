# system/services/regime_service.py

import requests


FLASK_REGIME_URL = "http://127.0.0.1:5001/detect_regime"


class RegimeService:

    @staticmethod
    def get_current_regime(market: str, symbol: str):
        """
        Calls Flask regime detection service and returns regime data.
        """

        if not market or not symbol:
            return {
                "error": "Market and symbol are required."
            }, 400

        try:
            response = requests.post(
                FLASK_REGIME_URL,
                json={
                    "market": market,
                    "symbol": symbol
                },
                timeout=5
            )

            if response.status_code != 200:
                return {
                    "error": "Regime service error.",
                    "details": response.json()
                }, response.status_code

            return response.json(), 200

        except requests.exceptions.RequestException as e:
            return {
                "error": "Regime service unavailable.",
                "details": str(e)
            }, 503