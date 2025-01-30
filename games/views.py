import django_filters
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from games.actions import GameApproveAction, GameOfferAction
from games.models import Game
from games.serializers import GameSerializer, GameRequestSerializer, GameResultApproveSerializer, GameDetailSerializer
from oina.serializers import ErrorSerializer
from ratings.actions import RatingCalculateAction, GameCalculateAction



class GameFilter(django_filters.FilterSet):
    status = django_filters.NumberFilter(field_name="status")

    class Meta:
        model = Game
        fields = ['status']

class GameRequestView(APIView):

    permission_classes = (IsAuthenticated, )
    serializer_class = GameRequestSerializer

    @extend_schema(responses={
        200: GameSerializer(),
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

        return Response(GameSerializer(game).data)


class GameStartView(APIView):

    permission_classes = (IsAuthenticated, )

    @extend_schema(responses={
        200: GameSerializer(),
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

            return Response(GameSerializer(game).data)

        raise APIException('Status doesn\'t change')


class GameCancelView(APIView):

    permission_classes = (IsAuthenticated, )

    @extend_schema(responses={
        200: GameSerializer(),
        500: ErrorSerializer()
    })
    @transaction.atomic
    def get(self, request, pk: int,  *args, **kwargs):

        game = Game.objects.get(pk=pk)

        if game.status == game.Status.finished:
            raise APIException('Game already finished')

        if game.is_author(request.user.id) or game.is_rival(request.user.id):
            game.status = game.Status.cancelled
            game.save()
            return Response(GameSerializer(game).data)

        raise APIException('You doesnt change status')





class GameResultApproveView(APIView):

    permission_classes = (IsAuthenticated, )
    serializer_class = GameResultApproveSerializer


    @extend_schema(responses={
        200: GameSerializer(),
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

        if data.get('action_type') == 'offer':
            game_offer_action = GameOfferAction(game_id=game.id,
                                                result=data.get('result'),
                                                user_id=request.user.id)
            game_offer_action.handle()
        if data.get('action_type') == 'approve':
            game_approve_action = GameApproveAction(game_id=game.id,
                                                    result=data.get('result'))
            game_approve_action.handle()

        return Response(GameSerializer(game).data)


class GameDetailView(APIView):

    @extend_schema(responses={
        200: GameDetailSerializer(),
        500: ErrorSerializer()
    })
    def get(self, request, pk: int, *args, **kwargs):
        game = get_object_or_404(Game, pk=pk)
        return Response(GameDetailSerializer(game).data)


class GameListView(ListAPIView):

    serializer_class = GameSerializer
    queryset = Game.objects.all()
    filterset_class = GameFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            if self.kwargs.get('action') == 'user-games':
                return queryset.filter(Q(author=self.request.user) | Q(rival=self.request.user), status__in=[0,1,2])
            if self.kwargs.get('action') == 'winning-user-games':
                return queryset.filter(winner=self.request.user)
            if self.kwargs.get('action') == 'lose-user-games':
                return queryset.filter(loser=self.request.user)

        return queryset



