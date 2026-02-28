import requests
import threading
import time
from .broadcast_service import BroadcastService

FASTAPI_MARKET_BASE = "http://127.0.0.1:8000/api/market/snapshot"


class MarketService:

    VALID_MARKETS = ["CRYPTO", "NASDAQ", "NYSE"]

    _last_broadcasted_snapshot = {}
    _streaming_started = False

    @staticmethod
    def get_market_snapshot(market: str):
        """
        Calls FastAPI market snapshot endpoint.
        """
        if not market:
            return {"error": "Market parameter is required."}, 400

        market = market.upper()

        if market not in MarketService.VALID_MARKETS:
            return {"error": "Invalid market type."}, 400

        try:
            response = requests.get(
                f"{FASTAPI_MARKET_BASE}/{market}",
                timeout=15
            )

            if response.status_code != 200:
                return {
                    "error": "Market service error.",
                    "details": response.json()
                }, response.status_code

            return response.json(), 200

        except requests.exceptions.RequestException as e:
            return {
                "error": "Market service unavailable.",
                "details": str(e)
            }, 503

    # ===============================
    # 🔥 BACKGROUND STREAMING
    # ===============================

    @staticmethod
    def _poll_market():
        """
        Background polling loop.
        Runs every 5 seconds.
        """

        print("📡 Market snapshot streaming started")

        while True:
            try:
                for market in MarketService.VALID_MARKETS:
                    response, status = MarketService.get_market_snapshot(market)

                    if status != 200:
                        continue

                    previous = MarketService._last_broadcasted_snapshot.get(market)

                    # 🔥 Debounce: broadcast only if changed
                    if response != previous:
                        print(f"🔥 MARKET BROADCAST TRIGGERED ({market})")

                        BroadcastService.send(
                            channel="market",
                            data={
                                "market": market,
                                "snapshot": response
                            }
                        )

                        MarketService._last_broadcasted_snapshot[market] = response

                time.sleep(5)

            except Exception as e:
                print("Market streaming error:", str(e))
                time.sleep(5)

    @staticmethod
    def start_streaming():
        """
        Starts background streaming once.
        """
        if not MarketService._streaming_started:
            MarketService._streaming_started = True

            thread = threading.Thread(
                target=MarketService._poll_market,
                daemon=True
            )
            thread.start()