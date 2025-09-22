from django.urls import path, include
from rest_framework import routers

from auth_app.views import *
from auth_app.views.roles import RolesAPIView

user_router = routers.DefaultRouter()
user_router.register(r'users', CustomUserAPIView, basename='user')

role_router = routers.DefaultRouter()
role_router.register(r'roles', RolesAPIView, basename='roles')

# TODO проверить таблицы в README.md
urlpatterns = [
    path('', include(user_router.urls), name='users'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/', RegisterAPIView.as_view(), name='register'),

    path('token/refresh/', RefreshTokenAPIView.as_view(), name='token_refresh'),
    path('token/revoke/', TokenRevokeAPIView.as_view(), name='token_revoke'),
    path('token/revoke_all/', TokenRevokeALLAPIView.as_view(), name='token_revoke_all'),
    # path('token/revoke/<int:user_id>/', AdminTokenRevokeAPIView.as_view(), name='admin_token_revoke'),  # Заморозил. Не нашел для чего применить.
    path('token/revoke_all/<int:user_id>/', AdminTokenRevokeALLAPIView.as_view(), name='admin_token_revoke_all'),

    path('me/get_sessions/', MySessionsAPIView.as_view(), name='get_my_sessions'),
    path('me/get_sessions/<int:user_id>', AdminSessionsAPIView.as_view(), name='get_my_sessions'),
    path('me/', MyProfileAPIView.as_view({'get': 'list'}), name='me'),

    path('roles/', include(role_router.urls), name='roles'),

]
