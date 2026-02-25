class PositionEngine:

    @staticmethod
    def size_position(price: float, atr: float, risk_config: dict):

        if atr <= 0:
            raise ValueError("ATR must be positive.")

        total_capital = risk_config["total_capital"]
        risk_per_trade = risk_config["risk_per_trade"]
        atr_multiplier = risk_config["atr_multiplier"]

        # 1️⃣ Risk capital
        risk_amount = total_capital * risk_per_trade

        # 2️⃣ Stop distance
        stop_distance = atr * atr_multiplier

        if stop_distance <= 0:
            raise ValueError("Invalid stop distance.")

        # 3️⃣ Position size
        position_size = risk_amount / stop_distance

        # 4️⃣ Capital allocated
        capital_allocated = position_size * price

        return {
            "position_size": position_size,
            "risk_amount": risk_amount,
            "capital_allocated": capital_allocated,
        }