import random
import time
from loguru import logger

logger.add("market.log", rotation="5 MB")

class MarketSimulator:
    def __init__(self, start_price=100.0):
        self.price = start_price

    def generate_tick(self):
        change = random.uniform(-0.8, 0.8)
        self.price += change
        self.price = max(self.price, 1)

        tick = {
            "price": round(self.price, 2),
            "volume": random.randint(100, 1000),
            "timestamp": time.time()
        }

        logger.info(f"Tick Generated: {tick}")

        return tick
