from rest_framework import serializers
from system.models import TradeExecution

class TradeExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeExecution
        fields = [
            "symbol",
            "action",
            "position_size",
            "price",
            "capital_allocated",
            "meta_regime",
            "strategy",
            "executed_at",
        ]