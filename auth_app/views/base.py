from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import IssueTokenModel, CustomUserModel
from auth_app.serializers import ActiveSessionTokenSerializer, CustomUserSerializer
from auth_app.utils import TokenService


class BaseTokenRevokeAPIView(APIView):
    """
    Базовый класс для отзыва токенов.
    Параметр `revoke_all` определяет, отзывать один токен или все.

    """

    revoke_all = False
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Нужно передать в API refresh токен в параметрах data запроса(теле запроса)
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

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
        # is_revoked, token_data, revoke_data = TokenService.check_and_revoke_jwt_token(refresh_token)
        # payload, jti, user_id, exp, errors = token_data
        #
        # if is_revoked and revoke_data:
        #     success, message, status_code, count_revoked_tokens = revoke_data
        #     return Response(
        #         {
        #             'success': success,
        #             'message': f"Refresh-токен невалиден(TTL)! {message} Пройдите повторно авторизацию(логин и пароль)!'",
        #
        #         },
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

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
            'data': {
                'count_revoked_tokens': count_revoked_tokens
            }

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


class BaseSessionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
            Нужно передать в API refresh токен в параметрах data запроса(теле запроса)
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        target_user_id = self.get_target_user_id(request, *args, **kwargs)
        base_filter = {
            'user_id': target_user_id,
            'is_revoked': False,
        }
        if not self.can_view_sessions(request, target_user_id):
            return Response(
                {
                    'success': False,
                    'message': f'Недостаточно прав для просмотра сессий пользователя ID#{target_user_id}'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {
                    'success': False,
                    'message': 'Refresh токен обязателен!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        is_revoked, token_data, revoke_data = TokenService.check_and_revoke_jwt_token(refresh_token)
        payload, jti, user_id, exp, errors = token_data
        if is_revoked and revoke_data:
            success, message, status_code, count_revoked_tokens = revoke_data
            return Response(
                {
                    'success': success,
                    'message': f"Refresh-токен невалиден(TTL)! {message} Пройдите повторно авторизацию(логин и пароль)!'",

                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if errors:
            message, status_code = errors[0]
            return Response(
                {
                    'success': False,
                    'message': message,
                },
                status=status_code
            )

        # base_filter.setdefault('jti', jti)  # если добавить, то выдаст текущую сессиию


        sessions = IssueTokenModel.objects.filter(**base_filter)

        return Response(
            {
                'success': True,
                'message': f'Запрос упешен! Сессии получены!',
                'data': {
                    'user': CustomUserSerializer(request.user).data,
                    'sessions': ActiveSessionTokenSerializer(sessions, many=True).data
                },
            },
            status=status.HTTP_200_OK
        )


        sessions = IssueTokenModel.objects.filter(target_user_id=target_user_id)

    def get_target_user_id(self, request, *args, **kwargs):
        """
        Возвращает ID пользователя, чьи сессии нужно посмотреть. Текущий пользователь
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return request.user.id

    def can_view_sessions(self, request, target_user_id):
        """
        Проверяет, может ли текущий пользователь посмотреть сессии target_user_id.
        :param request:
        :param target_user_id: пользователь сессии которого нужно просмотреть
        :return:
        """
        return request.user.id == target_user_id
