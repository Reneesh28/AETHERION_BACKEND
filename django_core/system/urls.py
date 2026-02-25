from django.urls import path
from .views import health, get_portfolio_exposure, get_portfolio_config, get_enriched_decision, trade_history, risk_dashboard

urlpatterns = [
    path("health/", health),
    path("api/portfolio/exposure/", get_portfolio_exposure),
    path("api/portfolio/config/", get_portfolio_config),
    path("api/decision/enriched/", get_enriched_decision),
    path("api/trades/history", trade_history),
    path("api/risk/dashboard", risk_dashboard),
]
