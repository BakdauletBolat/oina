from rest_framework import serializers


class GameRequestSerializer(serializers.Serializer):

    game_type = serializers.CharField()
    rival_id = serializers.IntegerField()


class GameResultApproveSerializer(serializers.Serializer):
    ACTION_TYPE_CHOICES = (
        ('offer', 'Offer'),
        ('approve', 'approve'),
    )
    result = serializers.JSONField(allow_null=True, required=False)
    action_type = serializers.ChoiceField(choices=ACTION_TYPE_CHOICES)


class AuthorSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    photo_url = serializers.CharField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class RatingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    point = serializers.FloatField()
    user = AuthorSerializer()
    created_at = serializers.DateTimeField()


class GameSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    author = AuthorSerializer()
    rival = AuthorSerializer()
    created_at = serializers.DateTimeField()
    started_at = serializers.DateTimeField(allow_null=True)
    author_approved_at = serializers.DateTimeField(allow_null=True)
    rival_approved_at = serializers.DateTimeField(allow_null=True)
    finished_at = serializers.DateTimeField(allow_null=True)
    game_type = serializers.CharField()
    result = serializers.JSONField(default=None, allow_null=True)
    winner = AuthorSerializer(allow_null=True)
    loser = AuthorSerializer(allow_null=True)
    status = serializers.IntegerField()
    is_draw = serializers.BooleanField()
    ordering = serializers.IntegerField()


class GameDetailSerializer(GameSerializer):
    ratings = RatingSerializer(many=True)