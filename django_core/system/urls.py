from django.urls import path
from .views import health, get_portfolio_exposure, get_portfolio_config, get_enriched_decision


urlpatterns = [
    path("health/", health),
    path("api/portfolio/exposure/", get_portfolio_exposure),
    path("api/portfolio/config/", get_portfolio_config),
    path("api/decision/enriched/", get_enriched_decision),

]
