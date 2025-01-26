import base64
import hashlib
import hmac
import json
import sys

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import views
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from loguru import logger

from users.models import User
from users.serializers import AuthSerializer, UserDetailsSerializer

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level> - {extra}")

class AuthView(views.APIView):

    @staticmethod
    def parse_token_data(tg_auth_result: str):
        try:
            tg_auth_result = tg_auth_result.replace('-', '+').replace('_', '/')
            decoded_bytes = base64.b64decode(tg_auth_result + "==")
            decoded_str = decoded_bytes.decode('utf-8')
            auth_data = json.loads(decoded_str)
            return auth_data
        except (ValueError, AttributeError, base64.binascii.Error) as e:
            logger.bind(exception=e,
                        auth_data=tg_auth_result).error("Error decoding auth data")
            return None

    def post(self, request, *args, **kwargs):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.get('source') == 'telegram':

            logger.info("Trying to auth with Telegram API ...")

            auth_data = self.parse_token_data(data.get('token'))
            print(auth_data)
            if not auth_data:
                logger.bind(token=data.get('token')).error("Invalid telegram token")
                raise APIException("Invalid telegram token")

            check_hash = auth_data.pop("hash")
            auth_data_string = "\n".join(f"{k}={v}" for k, v in sorted(auth_data.items()))

            secret_key = hashlib.sha256(settings.AUTH_TELEGRAM_BOT_TOKEN.encode()).digest()
            calculated_hash = hmac.new(secret_key, auth_data_string.encode(), hashlib.sha256).hexdigest()

            if calculated_hash == check_hash:
                try:
                    user = User.objects.get(source='telegram', source_user_id=auth_data.get('id'))
                except User.DoesNotExist:
                    user = User.objects.create(source='telegram', source_user_id=auth_data.get('id'),
                                               username=User.get_telegram_username(auth_data.get('username')),
                                               first_name=auth_data.get('first_name'),
                                               last_name=auth_data.get('last_name'),
                                               photo_url=auth_data.get('photo_url'))

                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                logger.bind(telegram_user_id=auth_data.get('id')).error("Telegram token verification failed")
                raise APIException("Telegram token verification failed")

        if data.get('source') == 'django':
            user = authenticate(username=data.get('username'), password=data.get('password'))
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })

        raise APIException("Invalid auth data")


class UserMeView(views.APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(UserDetailsSerializer(request.user).data)
