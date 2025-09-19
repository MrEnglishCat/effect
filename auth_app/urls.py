from django.urls import path, include
from rest_framework import routers

from auth_app.views import CustomUserAPIView, TokenAPIView, LoginAPIView, LogoutAPIView, RegisterAPIView, TokenRevokeAPIView

user_router = routers.DefaultRouter()
user_router.register(r'users', CustomUserAPIView, basename='user')

token_router = routers.DefaultRouter()

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/', RegisterAPIView.as_view(), name='register'), # rabotaet
    path('tokens/', TokenAPIView.as_view(), name='tokens'), # пока что под вопросом, т к токены выдаются в login, а обновление в refresh
    path('token/refresh/', TokenAPIView.as_view(), name='token_refresh'),
    path('token/revoke/', TokenRevokeAPIView.as_view(), name='token_revoke'),
    path('token/revoke/all/<int:user_id>/', TokenRevokeAPIView.as_view(), name='token_revoke'),
    path('', include(user_router.urls), name='users'),

]
