from django.shortcuts import render
from django.http import JsonResponse
from system.models import Decision
from system.models import PortfolioSummary, PortfolioPosition
from system.services.risk_service import RiskService
import requests

FASTAPI_BASE = "http://127.0.0.1:8000"

def health(request):
    return JsonResponse({"status": "django_core running"})

def get_portfolio_exposure(request):
    summary = PortfolioSummary.objects.first()

    if not summary:
        return JsonResponse({"error": "PortfolioSummary not initialized."}, status=404)

    positions = PortfolioPosition.objects.all()

    open_positions = [
        {
            "symbol": p.symbol,
            "position_size": p.position_size,
            "exposure": p.exposure
        }
        for p in positions
    ]

    return JsonResponse({
        "total_capital": summary.total_capital,
        "used_capital": summary.used_capital,
        "free_capital": summary.free_capital,
        "total_exposure": summary.total_exposure,
        "open_positions": open_positions
    })

def get_portfolio_config(request):
    try:
        config = RiskService.get_config()
        return JsonResponse(config)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_enriched_decision(request):

    try:
        decision = Decision.objects.order_by("-created_at").first()

        if not decision:
            return JsonResponse({"message": "No decisions available yet."})

        # Get latest price from FastAPI
        snapshot_resp = requests.get(
            f"{FASTAPI_BASE}/api/market/snapshot/{decision.market}"
        )

        snapshot_data = snapshot_resp.json().get("data")

        if not snapshot_data:
            return JsonResponse({"error": "No market snapshot available."})

        price = snapshot_data["price"]

        # Placeholder ATR (we replace later with real ATR)
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

        return JsonResponse(enriched)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

