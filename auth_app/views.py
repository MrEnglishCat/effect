# from django.contrib.redirects.models import Redirect
import email
import uuid
from datetime import datetime, UTC
from pprint import pprint

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from auth_app.models import CustomUserModel, BlacklistToken, IssueTokenModel
from auth_app.serializers import CustomUserSerializer, RegisterCustomUserSerializer, LoginCustomUserSerializer
from django.contrib.auth import authenticate

from auth_app.utils import TokenService


class CustomUserAPIView(ModelViewSet):
    """
    endpoint Для работы с пользователем
    В зависимости от статуса is_staff=True or is_superuser=True - есть доступ ко всем учетным записям
    если False - то доступ только к своей.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        if self.request.user.is_staff or self.request.user.is_superuser:
            queryset = self.get_queryset()
            obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
            return obj
        return self.request.user

    def get_queryset(self):
        """
        is_staff - могут получить всех пользователей кроме супервайзеров (is_superuser=True)
        is_superuser - могут получить абсолютно всех пользователей без исключения.
        :return:
        """
        if self.request.user.is_superuser:
            return CustomUserModel.objects.all()
        elif self.request.user.is_staff:
            return CustomUserModel.objects.all().exclude(is_superuser=True)
        return CustomUserModel.objects.filter(id=self.request.user.id)


class TokenAPIView(APIView):
    ...


class RegisterAPIView(APIView):
    """
    endpoint для регистрации пользователя POST
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterCustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUserModel.objects.create_user(**serializer.validated_data)
            access_token, refresh_token = TokenService.generate_jwt_tokens(user,
                                                                           ip_address=request.META.get("REMOTE_ADDR"),
                                                                           user_agent=request.META.get(
                                                                               "HTTP_USER_AGENT"))
            user.last_login = datetime.now(UTC)
            user.save()
            # user = serializer.save()  # TODO будет время переопределить в сериализаторе что бы хэшировался пароль
            return Response(
                {
                    'success': True,
                    'access': access_token,
                    'refresh': refresh_token,
                    'message': 'Регистрация прошла успешно!'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response({
                'success': False,
                'error': serializer.errors,
                'message': 'Невалидные данные для регистрации!'
            }, status=status.HTTP_400_BAD_REQUEST)


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class LoginAPIView(APIView):
    """
    endpoint для аутентификации пользователя POST
    """
    permission_classes = [AllowAny]

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
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                },
                'redirect_url': '/dashboard/'  # к примеру. можно указать url по которому фронт сделает редирект
            }, status=status.HTTP_200_OK)

        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)  # TODO попробовать переделать на свою

        if not user:
            return Response(
                {
                    'success': False,
                    'error': 'Неверный email или пароль!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user.last_login = datetime.now(UTC)
        user.save(update_fields=['last_login'])
        access_token, refresh_token = TokenService.generate_jwt_tokens(user, ip_address=request.META.get("REMOTE_ADDR"),
                                                                       user_agent=request.META.get("HTTP_USER_AGENT"))

        return Response(
            {
                'success': True,
                'access': access_token,
                'refresh': refresh_token,
                'message': 'Авторизация пройдена успешно!'
            },
            status=status.HTTP_201_CREATED
        )


class LogoutAPIView(APIView):
    """
    endpoint для разлогинивания пользователя и отзыва токена
    """
    permission_classes = [IsAuthenticated]

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


class BaseTokenRevokeAPIView(APIView):
    """
    Базовый класс для отзыва токенов.
    Параметр `revoke_all` определяет, отзывать один токен или все.
    """

    revoke_all = False
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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

        if self.revoke_all:
            success, message, status_code, count_revoked_tokens = TokenService.revoke_jwt_token(user_id)
        else:
            success, message, status_code, count_revoked_tokens = TokenService.revoke_jwt_token(user_id, jti)
        return Response({
            'success': success,
            'message': message,
            'count_revoked_tokens': count_revoked_tokens
        }, status=status_code)


class TokenRevokeAPIView(BaseTokenRevokeAPIView):
    """
    endpoint для отзыва одного токена пользователя(текущего известного)
    """
    ...


class TokenRevokeALLAPIView(BaseTokenRevokeAPIView):
    """
    endpoint для отзыва всех токенов для текущего пользователя
    """
    revoke_all = True

