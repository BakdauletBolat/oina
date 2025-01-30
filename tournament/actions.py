import random
import sys

from django.db.models import Q
from django.utils import timezone
from loguru import logger

from games.actions import GameApproveAction
from games.models import Game
from tournament.models import TournamentUserStat, Tournament

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level> - {extra}")


class CreateTournamentAction:

    def __init__(self, users_ids: list[int], name: str, organizer_id: int,
                 game_type: str = "FIFA") -> None:
        self.users_ids = users_ids
        self.name = name
        self.tournament_user_stats = []
        self.organizer_id = organizer_id
        self.tournament = None
        self.game_type = game_type

    def create_tournament_user_stats(self, tournament_id: int):
        for user_id in self.users_ids:
            self.tournament_user_stats.append(TournamentUserStat(
                user_id=user_id,
                tournament_id=tournament_id
            ))

        TournamentUserStat.objects.bulk_create(self.tournament_user_stats)
        return self.tournament_user_stats

    def create_tournament_object(self):
        self.tournament = Tournament.objects.create(name=self.name,
                                         game_type=self.game_type,
                                         organizer_id=self.organizer_id)
        return self.tournament

    @staticmethod
    def get_number_of_match(len_of_users: int) -> int:
        return (len_of_users * (len_of_users - 1)) // 2

    def generate_games(self):
        games = []
        len_of_users = len(self.users_ids)
        number_of_match = self.get_number_of_match(len_of_users)

        random_ordering = random.sample(range(number_of_match), number_of_match)
        counter_of_ordering = 0

        logger.bind(
            random_ordering=random_ordering,
            users_ids=self.users_ids,
            number_of_match=number_of_match,
        ).info("Created random ordering")

        for i in range(len_of_users):
            for j in range(i+1, len_of_users):
                games.append(Game.objects.create(
                    tournament_id=self.tournament.id,
                    author_id=self.users_ids[i],
                    rival_id=self.users_ids[j],
                    status=Game.Status.started,
                    started_at=timezone.now(),
                    game_type=self.tournament.game_type,
                    ordering=random_ordering[counter_of_ordering],
                ))
                counter_of_ordering += 1

        return games


    def handle(self):
        self.create_tournament_object()
        self.create_tournament_user_stats(self.tournament.id)
        self.generate_games()
        return self.tournament


class TournamentResultRecordAction:
    def __init__(self, game_id: int, result: dict, tournament_id: int):
        self.game_id = game_id
        self.result = result
        self.tournament_id = tournament_id
        logger.bind(
            game_id=self.game_id,
            result=self.result,
            tournament_id=self.tournament_id
        ).info("Trying create tournament result record ...")

    def handle(self):
        game_approve_action = GameApproveAction(game_id=self.game_id,
                                                result=self.result)

        game = game_approve_action.handle()

        logger.bind(
            winner_id=game.winner_id,
            loser_id=game.loser_id,
            author_id=game.author_id,
            rival_id=game.rival_id,
            game_id=game.id,
        ).info(
            "Successfully approved result record")

        tournament_user_action = TournamentUserAction(
            game=game,
            tournament_id=self.tournament_id
        )

        tournament_user_action.handle()

        return game


class TournamentUserAction:

    def __init__(self, game: Game, tournament_id: int):
        self.game = game
        self.tournament_id = tournament_id
        self.WINN_POINT = 3

    def get_points(self, winn_games_count: int, draw_games_count: int):
        return winn_games_count * self.WINN_POINT + draw_games_count

    def handle_user_stats(self, user_id: int):
        user_games = Game.objects.filter(
            Q(author_id=user_id) | Q(rival_id=user_id),
            tournament_id=self.tournament_id)

        winn_games = 0
        lose_games = 0
        draw_games = 0
        goals_scored = 0
        goals_conceded = 0
        for game in user_games:
            if game.winner_id == user_id:
                winn_games += 1
                if game.author_id == user_id:
                    goals_scored += game.result.get('game').get('author_score')
                    goals_conceded += game.result.get('game').get('rival_score')
                elif game.rival_id == user_id:
                    goals_scored += game.result.get('game').get('rival_score')
                    goals_conceded += game.result.get('game').get('author_score')

            if game.loser_id == user_id:
                lose_games += 1
                if game.author_id == user_id:
                    goals_scored += game.result.get('game').get('author_score')
                    goals_conceded += game.result.get('game').get('rival_score')
                elif game.rival_id == user_id:
                    goals_scored += game.result.get('game').get('rival_score')
                    goals_conceded += game.result.get('game').get('author_score')

            if game.is_draw:
                draw_games += 1
                goals_scored += game.result.get('game').get('rival_score')
                goals_conceded += game.result.get('game').get('rival_score')

        TournamentUserStat.objects.filter(
            tournament_id=self.tournament_id,
            user_id=user_id).update(
            points=self.get_points(winn_games, draw_games),
            draws=draw_games,
            losses=lose_games,
            wins=winn_games,
            goals_scored=goals_scored,
            goals_conceded=goals_conceded,
            diff_goals=goals_scored - goals_conceded,
        )
    def handle(self):
        self.handle_user_stats(self.game.author_id)
        self.handle_user_stats(self.game.rival_id)





