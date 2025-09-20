from django.urls import path, include
from rest_framework import routers

from auth_app.views import *

user_router = routers.DefaultRouter()
user_router.register(r'users', CustomUserAPIView, basename='user')

token_router = routers.DefaultRouter()

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/', RegisterAPIView.as_view(), name='register'), # rabotaet

    path('token/refresh/', RefreshTokenAPIView.as_view(), name='token_refresh'),  # TODO сделать рефреш апи

    path('token/revoke/', TokenRevokeAPIView.as_view(), name='token_revoke'),
    path('token/revoke_all/', TokenRevokeALLAPIView.as_view(), name='token_revoke_all'),

    # path('token/revoke/<int:user_id>/', AdminTokenRevokeAPIView.as_view(), name='admin_token_revoke'),  # Заморозил. Не нашел для чего применить.
    path('token/revoke_all/<int:user_id>/', AdminTokenRevokeALLAPIView.as_view(), name='admin_token_revoke_all'),

    # TODO нужен эндпоинт для получения списка активных сессий(одна сессия одна запись в issueJWT
    # TODO нужен эндпоинт для АДМИНОВ, ЧТО БЫ ПОСМОТРЕТЬ СЕССИИ ВСЕХ ПОЛЬЗОВАТЕЛЕЙполучения списка активных сессий(одна сессия одна запись в issueJWT
    path('me/get_sessions/', MySessionsAPIView.as_view(), name='get_my_sessions'),
    path('me/get_sessions/<int:user_id>', AdminSessionsAPIView.as_view(), name='get_my_sessions'),
    path('me/', MyProfileAPIView.as_view({'get': 'list'}), name='me'),

    path('', include(user_router.urls), name='users'),

]
