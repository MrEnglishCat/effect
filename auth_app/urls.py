from django.urls import path, include
from rest_framework import routers

from auth_app.views import CustomUserAPIView, TokenAPIView, LoginAPIView, LogoutAPIView

user_router = routers.DefaultRouter()
user_router.register(r'users', CustomUserAPIView)

token_router = routers.DefaultRouter()

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/', LogoutAPIView.as_view(), name='register'),
    path('tokens/', TokenAPIView.as_view(), name='tokens'), # пока что под вопросом, т к токены выдаются в login, а обновление в refresh
    path('token/refresh/', TokenAPIView.as_view(), name='token_refresh'),
    path('', include(user_router.urls), name='users'),

]
