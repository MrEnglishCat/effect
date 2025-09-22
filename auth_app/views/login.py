from datetime import datetime, UTC

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from auth_app.utils import TokenService, SessionService

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class LoginAPIView(APIView):
    """
    endpoint для аутентификации пользователя POST
    """
    permission_classes = (AllowAny,)
    resource_name = 'users'

    @swagger_auto_schema(
        operation_description="Вход по email и паролю. Получение токенов",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            },
            required=['email', 'password']
        ),
        responses={
            200: "Успешный вход",
            401: "Неверные учетные данные"
        }
    )
    def post(self, request):

        if request.user.is_authenticated:
            return Response({
                'success': True,
                'message': 'Вы уже авторизованы',
                'data': {
                    'user': {
                        'id': request.user.id,
                        'email': request.user.email,
                    },
                    'redirect_url': '/dashboard/'  # к примеру. можно указать url по которому фронт сделает редирект
                }
            }, status=status.HTTP_200_OK)

        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            return Response(
                {
                    'success': False,
                    'message': 'Неверный email или пароль!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        _time_now = datetime.now(UTC)
        user.last_login = _time_now
        user.save(update_fields=['last_login'])
        access_token, refresh_token = TokenService.generate_jwt_tokens(user, ip_address=request.META.get("REMOTE_ADDR"),
                                                                       user_agent=request.META.get("HTTP_USER_AGENT"))
        SessionService.create_session(request, user, _time_now)

        return Response(
            {
                'success': True,
                'message': 'Авторизация пройдена успешно!',
                'data': {
                    'access': access_token,
                    'refresh': refresh_token,
                }
            },
            status=status.HTTP_201_CREATED
        )
