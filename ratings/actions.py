from django.db.models import Sum

from games.models import Game
from ratings import models
from users import models as user_models

MINIMAL_POINT = 100
MINIMAL_LOOSER_POINT = 10
COEFFICIENT = 0.10


class RatingCreateAction:

    @staticmethod
    def handle(user_id: int, point: float):
        return models.Rating.objects.create(user_id=user_id, point=point)


class RatingCalculateAction:

    @staticmethod
    def handle(winner_id: int, looser_id: int):
        looser_point = models.Rating.objects.filter(user_id=looser_id).aggregate(Sum('point'))['point__sum']
        winner_point = models.Rating.objects.filter(user_id=winner_id).aggregate(Sum('point'))['point__sum']

        max_get_point = looser_point / 2

        point = float(looser_point) * COEFFICIENT

        if point > max_get_point:
            point = max_get_point

        models.Rating.objects.create(user_id=winner_id, point=point)
        user_models.User.objects.filter(pk=winner_id).update(rating_sum=float(winner_point)+point)
        models.Rating.objects.create(user_id=looser_id, point=-point)
        user_models.User.objects.filter(pk=looser_id).update(rating_sum=float(looser_point)-point)
        return

class GameCalculateAction:

    @staticmethod
    def handle(winner_id: int, looser_id: int):
        loser_game_count = Game.objects.filter(looser_id=looser_id).count()
        winner_game_count = Game.objects.filter(winner_id=winner_id).count()

        user_models.User.objects.filter(pk=winner_id).update(winning_sum=winner_game_count+1)
        user_models.User.objects.filter(pk=looser_id).update(lost_sum=loser_game_count + 1)
        return