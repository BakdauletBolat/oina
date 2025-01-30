from rest_framework import serializers

from games.serializers import GameSerializer, AuthorSerializer


class GameResultSerializer(serializers.Serializer):
    author_score = serializers.IntegerField()
    rival_score = serializers.IntegerField()


class ResultSerializer(serializers.Serializer):
    game = GameResultSerializer()

class TournamentCreateSerializer(serializers.Serializer):

    users_ids = serializers.ListField(child=serializers.IntegerField())
    name = serializers.CharField(max_length=100)
    game_type = serializers.CharField(max_length=100, default="FIFA")


class TournamentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    game_type = serializers.CharField(max_length=100, default="FIFA")
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)
    status = serializers.IntegerField(required=False)
    organizer = AuthorSerializer()


class TournamentUserStatSerializer(serializers.Serializer):
    points = serializers.IntegerField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    draws = serializers.IntegerField()
    goals_scored = serializers.IntegerField()
    goals_conceded = serializers.IntegerField()
    user = AuthorSerializer()
    diff_goals = serializers.IntegerField()


class TournamentDetailSerializer(TournamentSerializer):
    tournament_games = GameSerializer(many=True)
    stats = TournamentUserStatSerializer(many=True)
