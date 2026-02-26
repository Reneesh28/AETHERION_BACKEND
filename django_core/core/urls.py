from django.urls import path, include

urlpatterns = [
    path("api/system/", include("system.urls")),
    path('api/auth/', include('users.urls')),
]