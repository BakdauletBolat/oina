from django.urls import path
from tournament import views


urlpatterns = [
    path('', views.TournamentCreateView.as_view(), name='tournament-create'),
    path('approve/<int:pk>/<int:tournament_id>/', views.TournamentRecordResultsView.as_view(), name='request_game'),
    path('<int:pk>/', views.TournamentDetailView.as_view(), name='tournament-detail'),
    path('list/', views.TournamentListView.as_view(), name='tournament-list'),
]