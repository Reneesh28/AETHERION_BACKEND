from typing import List, Dict


# INTERNAL UNIFIED TRADE SCHEMA
def unified_trade_schema(
    market_type: str,
    symbol: str,
    price: float,
    quantity: float,
    side: str,
    exchange_timestamp: int,
    receive_timestamp: int
) -> Dict:

    return {
        "market_type": market_type,        # CRYPTO | US_STOCK | NSE
        "symbol": symbol,                  # BTCUSDT | NASDAQ:AAPL | NSE:RELIANCE
        "price": price,
        "quantity": quantity,
        "side": side,                      # BUY | SELL
        "exchange_timestamp": exchange_timestamp,
        "receive_timestamp": receive_timestamp
    }

# INTERNAL UNIFIED ORDERBOOK SCHEMA
def unified_orderbook_schema(
    market_type: str,
    symbol: str,
    bids: List[List[float]],
    asks: List[List[float]],
    exchange_timestamp: int,
    receive_timestamp: int
) -> Dict:

    return {
        "market_type": market_type,
        "symbol": symbol,
        "bids": bids,      # [[price, quantity], ...]
        "asks": asks,      # [[price, quantity], ...]
        "exchange_timestamp": exchange_timestamp,
        "receive_timestamp": receive_timestamp
    }
