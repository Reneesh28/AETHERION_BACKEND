from django.urls import path
from .views import (
    health, 
    get_portfolio_exposure,
    get_portfolio_config,
    get_enriched_decision,
    trade_history,
    risk_dashboard,
    get_current_regime,
    get_current_strategy,
    get_market_snapshot)

urlpatterns = [
    path("health/", health),
    path("portfolio/exposure/", get_portfolio_exposure),
    path("portfolio/config/", get_portfolio_config),
    path("decision/enriched/", get_enriched_decision),
    path("trades/history/", trade_history),
    path("risk/dashboard/", risk_dashboard),
    path("regime/current/", get_current_regime),
    path("strategy/current/", get_current_strategy),
    path("market/snapshot/", get_market_snapshot),
]
