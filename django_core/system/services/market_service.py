import requests

FASTAPI_MARKET_BASE = "http://127.0.0.1:8001/api/market/snapshot"

class MarketService:
    VALID_MARKETS = ["CRYPTO", "NASDAQ", "NYSE"]
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
