from django.urls import path, include

print("CORE URLS LOADED")
urlpatterns = [
    path("api/system/", include("system.urls")),
    path('api/auth/', include('users.urls')),
]