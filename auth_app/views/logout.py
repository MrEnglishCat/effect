from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.utils import TokenService


class LogoutAPIView(APIView):
    """
    Разлогинивает пользователя и отзывает токен
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Для разлогинивания нужен refresh токен!!!
        :param request:
        :return:
        """
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {
                    'success': False,
                    'message': 'Refresh токен обязателен!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payload, jti, user_id, exp, errors = TokenService.check_jwt_token(refresh_token, request.user)

        if errors:
            message, status_code = errors[0]
            return Response(
                {
                    'success': False,
                    'message': message,
                },
                status=status_code
            )

        success, message, status_code, _ = TokenService.revoke_jwt_token(user_id, jti)

        return Response({
            'success': success,
            'message': f'Пользователь {request.user.email} успешно разлогинен!' if success else f"Пользователь уже был разлогинен! {message}",
        }, status=status_code)
