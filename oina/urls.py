from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),

    path('users/', include('users.urls')),
    path('games/', include('games.urls')),
    path('tournaments/', include('tournament.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')
]
