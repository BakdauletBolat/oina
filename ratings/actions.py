from django.db.models import Sum, Q

from games.models import Game
from ratings import models
from users import models as user_models

MINIMAL_POINT = 100
MINIMAL_LOOSER_POINT = 10
COEFFICIENT = 0.10
DRAW_COEFFICIENT = 0.01

class RatingCreateAction:

    @staticmethod
    def handle(user_id: int, point: float):
        models.Rating.objects.create(user_id=user_id, point=point)
        points_sum = models.Rating.objects.filter(user_id=user_id).aggregate(Sum('point')).get('point__sum', 0)
        user_models.User.objects.filter(pk=user_id).update(rating_sum=float(points_sum))
        return


class RatingCalculateAction:

    def __init__(self,
                 game_id: int,
                 winner_id: int,
                 loser_id: int,
                 draw_user_ids: list[int] | None = None):
        self.draw_user_ids = draw_user_ids
        self.game_id = game_id
        self.winner_id = winner_id
        self.loser_id = loser_id

    def calculate_when_draw(self):
        points_sum = models.Rating.objects.filter(user_id__in=self.draw_user_ids).aggregate(Sum('point'))['point__sum']
        draw_point = float(points_sum) * DRAW_COEFFICIENT
        for user_id in self.draw_user_ids:
            u_point = models.Rating.objects.filter(user_id=user_id).aggregate(Sum('point')).get('point__sum', 0)
            models.Rating.objects.create(user_id=user_id,
                                         point=draw_point,
                                         game_id=self.game_id)
            user_models.User.objects.filter(pk=user_id).update(rating_sum=float(u_point) + draw_point)


    def calculate(self):
        looser_point = models.Rating.objects.filter(user_id=self.loser_id).aggregate(Sum('point')).get('point__sum', 0)
        winner_point = models.Rating.objects.filter(user_id=self.winner_id).aggregate(Sum('point')).get('point__sum', 0)

        max_get_point = looser_point / 2

        point = float(looser_point) * COEFFICIENT

        if point > max_get_point:
            point = max_get_point

        models.Rating.objects.create(user_id=self.winner_id,
                                     point=point,
                                     game_id=self.game_id)
        user_models.User.objects.filter(pk=self.winner_id).update(rating_sum=float(winner_point) + point)


        models.Rating.objects.create(user_id=self.loser_id,
                                     point=-point,
                                     game_id=self.game_id)
        user_models.User.objects.filter(pk=self.loser_id).update(rating_sum=float(looser_point) - point)

    def handle(self):
        if self.draw_user_ids:
            self.calculate_when_draw()
        else:
            self.calculate()
        return

class GameCalculateAction:

    @staticmethod
    def handle_draw(game: Game):
        author_games_count = Game.objects.filter(author_id=game.author_id, is_draw=True).count()
        rival_games_count = Game.objects.filter(rival_id=game.rival_id, is_draw=True).count()
        user_models.User.objects.filter(pk=game.author_id).update(draw_sum=author_games_count + 1)
        user_models.User.objects.filter(pk=game.rival_id).update(draw_sum=rival_games_count + 1)

    @staticmethod
    def handle_result(game: Game):
        loser_game_count = Game.objects.filter(loser_id=game.loser_id).count()
        winner_game_count = Game.objects.filter(winner_id=game.winner_id).count()
        user_models.User.objects.filter(pk=game.winner_id).update(winning_sum=winner_game_count + 1)
        user_models.User.objects.filter(pk=game.loser_id).update(lost_sum=loser_game_count + 1)
        return

    def handle(self, game: Game):
        if game.is_draw:
            self.handle_draw(game)
        else:
            self.handle_result(game)
        return