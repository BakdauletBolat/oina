from django.utils import timezone

from games.models import Game
from ratings.actions import RatingCalculateAction, GameCalculateAction


class GameApproveAction:

    def __init__(self,game_id: int, result: object):
        self.game_id = game_id
        self.result = result

    def handle(self):
        game = Game.objects.get(pk=self.game_id)
        game.result = self.result

        if game.rival_approved_at is None:
            game.rival_approved_at = timezone.now()
        if game.author_approved_at is None:
            game.author_approved_at = timezone.now()

        game.finished_at = timezone.now()

        game.winner_id = game.get_winner_id()
        game.loser_id = game.get_loser_id()
        game.status = game.Status.finished

        if game.winner_id is None and game.loser_id is None:
            game.is_draw = True



        rating_calculate = RatingCalculateAction(game.id,
                                                 game.winner_id,
                                                 game.loser_id,
                                                 [game.author_id,
                                                  game.rival_id] if game.is_draw else None)

        rating_calculate.handle()

        game_calculate = GameCalculateAction()
        game_calculate.handle(game)
        game.save()
        return game


class GameOfferAction:
    def __init__(self,game_id: int, result: dict, user_id: int):
        self.game_id = game_id
        self.result = result
        self.user_id = user_id

    @staticmethod
    def result_set(result: dict | None, game: Game, offered_user_id: int,
                   to_approve_user_id: int, type_set: str = 'rival'):
        attrs = {
            'rival': {
                'to_none': 'author_approved_at',
                'to_set': 'rival_approved_at'
            },
            'author': {
                'to_none': 'rival_approved_at',
                'to_set': 'author_approved_at'
            }
        }

        game.result = result

        setattr(game, attrs[type_set].get('to_none'), None)
        setattr(game, attrs[type_set].get('to_set'), timezone.now())

        game.status = game.Status.result_awaiting
        game.result['offered_user_id'] = offered_user_id
        game.result['result']['to_approve_user_id'] = to_approve_user_id

    def handle(self):
        game = Game.objects.get(pk=self.game_id)
        if game.is_rival(self.user_id):
            self.result_set(self.result,
                            game,
                            offered_user_id=game.rival_id,
                            to_approve_user_id=game.author_id,
                            type_set='rival')
        elif game.is_author(self.user_id):
            self.result_set(self.result, game, offered_user_id=game.author_id,
                            to_approve_user_id=game.rival_id,
                            type_set='author')
        return game.save()

