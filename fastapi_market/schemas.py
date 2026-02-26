from typing import List, Dict

SUPPORTED_MARKETS = {"CRYPTO", "NASDAQ", "NYSE"}
def unified_trade_schema(
    market_type: str,
    symbol: str,
    price: float,
    quantity: float,
    side: str,
    exchange_timestamp: int,
    receive_timestamp: int
) -> Dict:

    if market_type not in SUPPORTED_MARKETS:
        raise ValueError(f"Unsupported market_type: {market_type}")

    return {
        "market_type": market_type,        # CRYPTO | NASDAQ | NYSE
        "symbol": symbol,                  # BTCUSDT | NASDAQ:AAPL | NYSE:IBM
        "price": float(price),
        "quantity": float(quantity),
        "side": side,                      # BUY | SELL
        "exchange_timestamp": exchange_timestamp,
        "receive_timestamp": receive_timestamp
    }

def unified_orderbook_schema(
    market_type: str,
    symbol: str,
    bids: List[List[float]],
    asks: List[List[float]],
    exchange_timestamp: int,
    receive_timestamp: int
) -> Dict:

    if market_type not in SUPPORTED_MARKETS:
        raise ValueError(f"Unsupported market_type: {market_type}")

    return {
        "market_type": market_type,
        "symbol": symbol,
        "bids": bids,      # [[price, quantity], ...]
        "asks": asks,      # [[price, quantity], ...]
        "exchange_timestamp": exchange_timestamp,
        "receive_timestamp": receive_timestamp
    }