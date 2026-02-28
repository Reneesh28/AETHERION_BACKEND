from django.shortcuts import render
from django.http import JsonResponse
from system.models import Decision
from system.models import PortfolioSummary, PortfolioPosition
from system.services.risk_service import RiskService
from rest_framework.decorators import api_view
from rest_framework.response import Response
from system.models import TradeExecution
from system.serializers import TradeExecutionSerializer
from system.services.regime_service import RegimeService
from system.services.strategy_service import StrategyService
from system.services.market_service import MarketService

import requests

FASTAPI_BASE = "http://127.0.0.1:8001"

def health(request):
    return JsonResponse({"status": "django_core running"})

@api_view(["GET"])
def get_portfolio_exposure(request):
    summary = PortfolioSummary.objects.first()

    if not summary:
        return Response({"error": "PortfolioSummary not initialized."}, status=404)

    positions = PortfolioPosition.objects.all()

    open_positions = [
        {
            "symbol": p.symbol,
            "position_size": p.position_size,
            "exposure": p.exposure
        }
        for p in positions
    ]

    return Response({
        "total_capital": summary.total_capital,
        "used_capital": summary.used_capital,
        "free_capital": summary.free_capital,
        "total_exposure": summary.total_exposure,
        "open_positions": open_positions
    })

@api_view(["GET"])
def get_portfolio_config(request):
    try:
        config = RiskService.get_config()
        return Response(config)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
def get_enriched_decision(request):

    try:
        decision = Decision.objects.order_by("-created_at").first()

        if not decision:
            return Response({"message": "No decisions available yet."})

        snapshot_resp = requests.get(
            f"{FASTAPI_BASE}/api/market/snapshot/{decision.market}"
        )

        snapshot_data = snapshot_resp.json().get("data")

        if not snapshot_data:
            return Response({"error": "No market snapshot available."})

        price = snapshot_data["price"]
        atr = 10

        risk_config = RiskService.get_config()

        sizing_resp = requests.post(
            f"{FASTAPI_BASE}/api/position/size",
            json={
                "price": price,
                "atr": atr,
                "risk_config": risk_config
            }
        )

        sizing_data = sizing_resp.json()

        enriched = {
            "market": decision.market,
            "symbol": decision.symbol,
            "meta_regime": decision.meta_regime,
            "strategy": decision.strategy,
            "action": decision.action,
            "confidence": decision.confidence,
            "created_at": decision.created_at,
            **sizing_data,
            "preview": True
        }

        return Response(enriched)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
def trade_history(request):
    trades = TradeExecution.objects.all()
    serializer = TradeExecutionSerializer(trades, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def risk_dashboard(request):

    summary = PortfolioSummary.objects.first()

    if not summary:
        return Response({"error": "PortfolioSummary not initialized."}, status=404)

    risk_config = RiskService.get_config()

    total_capital = summary.total_capital
    used_capital = summary.used_capital
    free_capital = summary.free_capital
    current_exposure = summary.total_exposure

    max_exposure_allowed = risk_config.get("max_total_exposure", 0)
    risk_per_trade = risk_config.get("risk_per_trade_amount", 0)

    capital_utilization_percent = (
        (used_capital / total_capital) * 100
        if total_capital > 0 else 0
    )

    remaining_capacity = max_exposure_allowed - current_exposure

    return Response({
        "total_capital": total_capital,
        "used_capital": used_capital,
        "free_capital": free_capital,
        "capital_utilization_percent": round(capital_utilization_percent, 2),
        "max_total_exposure_allowed": max_exposure_allowed,
        "current_total_exposure": current_exposure,
        "remaining_capacity": remaining_capacity,
        "risk_per_trade_amount": risk_per_trade,
    })

@api_view(["GET"])
def get_current_regime(request):
    market = request.query_params.get("market")
    symbol = request.query_params.get("symbol")

    data, status_code = RegimeService.get_current_regime(market, symbol)

    return Response(data, status=status_code)

@api_view(["GET"])
def get_current_strategy(request):
    data, status_code = StrategyService.get_current_strategy()
    return Response(data, status=status_code)

@api_view(["GET"])
def get_market_snapshot(request):
    market = request.query_params.get("market")
    data, status_code = MarketService.get_market_snapshot(market)
    return Response(data, status=status_code)