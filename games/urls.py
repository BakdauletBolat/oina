from django.urls import path

from games.views import GameDetailView, GameRequestView, GameStartView, GameResultApproveView, GameListView

urlpatterns = [
    path('', GameListView.as_view(), name='game_list'),
    path('<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('request/', GameRequestView.as_view(), name='request_game'),
    path('<int:pk>/start/', GameStartView.as_view(), name='start_game'),
    path('<int:pk>/approve/', GameResultApproveView.as_view(), name='approve_game'),
    path('winning-user-games/', GameListView.as_view(), name='winning_user_games', kwargs={
        "action": "winning-user-games"
    }),
    path('lose-user-games/', GameListView.as_view(), name='winning_user_games', kwargs={
        "action": "lose-user-games"
    }),
    path('user-games/', GameListView.as_view(), name='winning_user_games', kwargs={
        "action": "user-games"
    }),
]