from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.utils import TokenService


class BaseTokenRevokeAPIView(APIView):
    """
    Базовый класс для отзыва токенов.
    Параметр `revoke_all` определяет, отзывать один токен или все.
    """

    revoke_all = False
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        target_user_id = self.get_target_user_id(request, *args, **kwargs)

        if not self.can_revoke(request, target_user_id):
            return Response({
                'success': False,
                'message': f'Недостаточно прав для отзыва токенов пользователя ID#{target_user_id}'
            }, status=status.HTTP_403_FORBIDDEN)

        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {
                    'success': False,
                    'message': 'Refresh токен обязателен!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payload, jti, user_id, exp, errors = TokenService.check_jwt_token(refresh_token)

        if errors:
            message, status_code = errors[0]
            return Response(
                {
                    'success': False,
                    'message': message,
                },
                status=status_code
            )

        if self.revoke_all:
            success, message, status_code, count_revoked_tokens = TokenService.revoke_jwt_token(user_id)
        else:
            success, message, status_code, count_revoked_tokens = TokenService.revoke_jwt_token(user_id, jti)
        return Response({
            'success': success,
            'message': message,
            'count_revoked_tokens': count_revoked_tokens
        }, status=status_code)

    def get_target_user_id(self, request, *args, **kwargs):
        """
        Возвращает ID пользователя, чьи токены нужно отозвать.
        :param request:
        :param args:
        :param kwargs: используется для отзыва токенов любых пользователей админами
        :return:
        """
        return request.user.id

    def can_revoke(self, request, target_user_id):
        """
        Проверяет, может ли текущий пользователь отозвать токены target_user_id.
        :param request:
        :param target_user_id: нужен для сравнения с
        :return:
        """
        return request.user.id == target_user_id