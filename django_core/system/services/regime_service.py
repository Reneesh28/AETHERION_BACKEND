# system/services/regime_service.py

import requests
from .broadcast_service import BroadcastService


FLASK_REGIME_URL = "http://127.0.0.1:5001/detect_regime"


class RegimeService:

    _last_broadcasted_regime = None  # In-memory state tracking

    @staticmethod
    def get_current_regime(market: str, symbol: str):
        """
        Calls Flask regime detection service and returns regime data.
        Automatically broadcasts regime updates if changed.
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

            regime_data = response.json()

            # 🔹 Broadcast only if regime changed
            if regime_data != RegimeService._last_broadcasted_regime:
                print("🔥 BROADCAST TRIGGERED")
                BroadcastService.send(
                    channel="regime",
                    data=regime_data
                )

                RegimeService._last_broadcasted_regime = regime_data

            return regime_data, 200

        except requests.exceptions.RequestException as e:
            return {
                "error": "Regime service unavailable.",
                "details": str(e)
            }, 503