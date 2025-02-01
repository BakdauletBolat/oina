from django.db import transaction
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from games.models import Game
from games.serializers import GameSerializer
from oina.serializers import ErrorSerializer
from tournament.actions import CreateTournamentAction, TournamentResultRecordAction, TournamentFinishAction
from tournament.models import Tournament, TournamentUserStat
from tournament.serializers import TournamentSerializer, TournamentCreateSerializer, ResultSerializer, \
    TournamentDetailSerializer
from users import permissions




class TournamentCreateView(APIView):

    permission_classes = (permissions.IsOrganizerPermission,)
    serializer_class = TournamentCreateSerializer

    @extend_schema(responses={
        200: TournamentSerializer(),
        500: ErrorSerializer()
    })
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        tournament_create_action = CreateTournamentAction(
            users_ids=data.get('users_ids'),
            name=data.get('name'),
            organizer_id=request.user.id,
            game_type=data.get('game_type')
        )

        tournament = tournament_create_action.handle()

        return Response({
            'id': tournament.id
        })


class TournamentRecordResultsView(APIView):
    permission_classes = (permissions.IsOrganizerPermission,)
    serializer_class = ResultSerializer

    @extend_schema(responses={
        200: GameSerializer(),
        500: ErrorSerializer()
    })
    @transaction.atomic
    def post(self, request, pk: int, tournament_id: int, *args, **kwargs):
        serializer = ResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        tournament_result_record_action = TournamentResultRecordAction(
            game_id=pk,
            result=data,
            tournament_id=tournament_id
        )

        game = tournament_result_record_action.handle()

        return Response(GameSerializer(game).data)

class TournamentFinishView(APIView):
    permission_classes = (permissions.IsOrganizerPermission,)

    @transaction.atomic
    def post(self,request, pk: int, *args, **kwargs):
        tournament_finish_action = TournamentFinishAction(pk)
        tournament = tournament_finish_action.handle()
        return Response(TournamentDetailSerializer(tournament).data)


class TournamentDetailView(APIView):

    @extend_schema(responses={
        200: TournamentDetailSerializer(),
    })
    def get(self, request, pk: int, *args, **kwargs):
        tournament = Tournament.objects.filter(pk=pk).prefetch_related(
            Prefetch("tournament_games",
                     queryset=Game.objects.select_related("author",
                                                                              "rival",
                                                                              "winner",
                                                                              "loser").order_by('ordering')),
            Prefetch(
                "stats",
                queryset=TournamentUserStat.objects.select_related("user").order_by("-points", "-diff_goals")
            )
        ).first()



        return Response(TournamentDetailSerializer(tournament).data)


class TournamentListView(ListAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
