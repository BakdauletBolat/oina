from django.urls import path

from users.views import AuthView, UserMeView, UsersListView


urlpatterns = [
    path('', UsersListView.as_view()),
    path('auth/', AuthView.as_view()),
    path('me/', UserMeView.as_view()),
]