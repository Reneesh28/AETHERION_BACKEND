from fastapi_market.connectors.us_base_connector import USBaseConnector


class NasdaqConnector(USBaseConnector):
    """
    NASDAQ specific connector
    """

    def __init__(self, symbol: str):
        super().__init__(symbol)

        if not symbol.startswith("NASDAQ:"):
            raise ValueError("Invalid NASDAQ symbol format")
