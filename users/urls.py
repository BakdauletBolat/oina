from django.urls import path

from users.views import AuthView, UserMeView, UsersListView, UserDetailView

urlpatterns = [
    path('', UsersListView.as_view()),
    path('<int:pk>/', UserDetailView.as_view()),
    path('auth/', AuthView.as_view()),
    path('me/', UserMeView.as_view()),
]