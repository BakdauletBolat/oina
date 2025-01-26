from rest_framework import serializers

from users.models import User


class AuthSerializer(serializers.Serializer):
    TOKEN_CHOICES = [
        ('django', 'Django'),
        ('telegram', 'Telegram'),
    ]

    token = serializers.CharField(required=False)
    source = serializers.ChoiceField(required=False, choices=TOKEN_CHOICES, default='django')
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)


class UserDetailsSerializer(serializers.Serializer):

    username = serializers.CharField()
    last_name = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    photo_url = serializers.CharField(required=False)
    rating_sum = serializers.FloatField()
    winning_sum = serializers.IntegerField()
    lost_sum = serializers.IntegerField()

