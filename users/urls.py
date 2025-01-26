from django.urls import path

from users.views import AuthView, UserMeView


urlpatterns = [
    path('auth/', AuthView.as_view()),
    path('me/', UserMeView.as_view()),
]