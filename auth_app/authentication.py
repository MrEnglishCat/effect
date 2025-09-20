from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from auth_app.models import CustomUserModel
from auth_app.utils import TokenService



class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        if not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('Невалидный JWT токен!', status.HTTP_401_UNAUTHORIZED)

        token = auth_header.replace('Bearer ', '')
        payload = TokenService.decode_jwt_token(token)
        if not payload:
            raise AuthenticationFailed('Невалидный или истёкший токен!', status.HTTP_401_UNAUTHORIZED)

        if payload.get('type') == 'refresh':
            raise AuthenticationFailed('Передан неверный тип токена!', status.HTTP_401_UNAUTHORIZED)

        try:
            user = CustomUserModel.objects.get(pk=payload['user_id'], is_active=True)
        except CustomUserModel.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден!', status.HTTP_401_UNAUTHORIZED)
        else:
            return user, token



    def authenticate_header(self, request):
        return f'Bearer realm="api"'
