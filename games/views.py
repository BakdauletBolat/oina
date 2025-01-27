from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from games.models import Game
from games.serializers import GameDetailSerializer, GameRequestSerializer, GameResultApproveSerializer
from oina.serializers import ErrorSerializer
from ratings.actions import RatingCalculateAction, GameCalculateAction


class GameRequestView(APIView):

    permission_classes = (IsAuthenticated, )
    serializer_class = GameRequestSerializer

    @extend_schema(responses={
        200: GameDetailSerializer(),
        500: ErrorSerializer()
    })
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        rival_id = data.get('rival_id')
        game_type = data.get('game_type')

        game = Game.objects.create(author_id=request.user.id,
                            rival_id=rival_id,
                            game_type=game_type)

        return Response(GameDetailSerializer(game).data)


class GameStartView(APIView):

    permission_classes = (IsAuthenticated, )

    @extend_schema(responses={
        200: GameDetailSerializer(),
        500: ErrorSerializer()
    })
    @transaction.atomic
    def get(self, request, pk: int,  *args, **kwargs):

        game = Game.objects.get(pk=pk)

        if game.status == game.Status.requested:
            if game.rival_id != request.user.id:
                return Response({'message': 'Your arent start game'})

            game.started_at = timezone.now()
            game.status = game.Status.started
            game.save()

            return Response(GameDetailSerializer(game).data)

        raise APIException('Status doesn\'t change')


class GameResultApproveView(APIView):

    permission_classes = (IsAuthenticated, )
    serializer_class = GameResultApproveSerializer

    @staticmethod
    def result_set(data: dict, game: Game, type_set: str = 'rival'):
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

        if data.get('result'):
            game.result = data.get('result')

        if game.result and data.get('result'):
            setattr(game, attrs[type_set].get('to_none'), None)

        setattr(game, attrs[type_set].get('to_set'), timezone.now())

        game.status = game.Status.result_awaiting

    @extend_schema(responses={
        200: GameDetailSerializer(),
        500: ErrorSerializer()
    })
    @transaction.atomic
    def post(self, request, pk: int, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        game = Game.objects.get(pk=pk)

        if game.status == game.Status.finished:
            raise APIException('Game already finished')

        if game.rival_id == request.user.id and game.rival_approved_at is None:
            self.result_set(data, game, type_set='rival')
        elif game.author_id == request.user.id and game.author_approved_at is None:
            self.result_set(data, game, type_set='author')

        if game.rival_approved_at and game.author_approved_at:
            game.finished_at = timezone.now()
            game.winner_id = game.get_winner_id()
            game.loser_id = game.get_loser_id()
            game.status = game.Status.finished
            RatingCalculateAction.handle(game.winner_id, game.loser_id)
            GameCalculateAction.handle(game.winner_id, game.loser_id)

        game.save()

        return Response(GameDetailSerializer(game).data)


class GameDetailView(APIView):

    @extend_schema(responses={
        200: GameDetailSerializer(),
        500: ErrorSerializer()
    })
    def get(self, request, pk: int, *args, **kwargs):
        game = get_object_or_404(Game, pk=pk)
        return Response(GameDetailSerializer(game).data)


class GameListView(ListAPIView):

    serializer_class = GameDetailSerializer
    queryset = Game.objects.all()





