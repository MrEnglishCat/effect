from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.utils import TokenService

from .base import BaseTokenRevokeAPIView, BaseSessionAPIView

__all__ = [
    'TokenRevokeAPIView',
    'TokenRevokeALLAPIView',
    'AdminTokenRevokeALLAPIView',
    'RefreshTokenAPIView',
    'MySessionsAPIView',
    'AdminSessionsAPIView',
]


class TokenRevokeAPIView(BaseTokenRevokeAPIView):
    """
    Отзывает один refresh-токен (указанный в теле запроса).
    """
    ...


class TokenRevokeALLAPIView(BaseTokenRevokeAPIView):
    """
    Отзывает ВСЕ refresh-токены текущего пользователя.
    """
    revoke_all = True


class AdminTokenRevokeALLAPIView(BaseTokenRevokeAPIView):
    """
    Админ может отозвать все токены любого пользователя.
    """
    revoke_all = True

    def get_target_user_id(self, request, *args, **kwargs):
        """
        Возвращает ID пользователя, чьи токены нужно отозвать.
        :param request:
        :param args:
        :param kwargs: используется для отзыва токенов любых пользователей админами
        :return:
        """
        return kwargs.get('user_id')

    def can_revoke(self, request, target_user_id):
        """
        Проверяет, может ли текущий пользователь отозвать токены target_user_id.
        :param request:
        :param target_user_id: нужен для сравнения с
        :return:
        """
        return request.user.is_staff or request.user.is_superuser


class RefreshTokenAPIView(APIView):

    def post(self, request):

        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {
                    'success': False,
                    'message': 'Refresh токен обязателен!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        access_token, refresh_token, errors = TokenService.reset_jwt_refresh_token(refresh_token, request.user)
        if errors:
            success, message, status_code = errors[0]
            return Response(
                {
                    'success': False,
                    'message': message,
                },
                status=status_code
            )

        return Response(
            {
                'success': True,
                'message': 'Токены обновлены!',
                'data': {
                    'access': access_token,
                    'refresh': refresh_token,
                }
            },
            status=status.HTTP_201_CREATED
        )

class MySessionsAPIView(BaseSessionAPIView):
    """
        Позволяет посмотреть сессии текущего пользователя.
    """
    ...

class AdminSessionsAPIView(BaseSessionAPIView):
    """
        Позволяет посмотреть сессии любого указанного пользователя.
        Для админов.
    """

    def get_target_user_id(self, request, *args, **kwargs):
        """
        Возвращает ID пользователя, чьи сессии нужно посмотреть.
        Можно получить сессии любых пользователей
        Для пользователей с is_staff=True, is_superuser=True.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return kwargs.get('user_id')

    def can_view_sessions(self, request, target_user_id):
        """
        Проверяет, может ли текущий пользователь посмотреть сессии target_user_id.
        :param request:
        :param target_user_id: пользователь сессии которого нужно просмотреть
        :return:
        """
        return request.user.is_staff or request.user.is_superuser
