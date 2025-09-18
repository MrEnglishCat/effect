from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from auth_app.models import CustomUserModel
from auth_app.utils import decode_token



class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        if not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('Невалидный JWT токен!')

        token = auth_header.split()[-1]

        payload = decode_token(token)

        if not payload:
            raise AuthenticationFailed('Невалидный или истёкший токен!')


        try:
            user = CustomUserModel.objects.get(pk=payload, is_active=True)
        except CustomUserModel.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден!')
        else:
            return user, token



    def authenticate_header(self, request):
        return f'Bearer realm="api"'
