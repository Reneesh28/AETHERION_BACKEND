from fastapi_market.connectors.us_base_connector import USBaseConnector


class NyseConnector(USBaseConnector):
    """
    NYSE specific connector
    """

    def __init__(self, symbol: str):
        super().__init__(symbol)

        if not symbol.startswith("NYSE:"):
            raise ValueError("Invalid NYSE symbol format")
