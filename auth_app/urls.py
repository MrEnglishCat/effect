from django.urls import path, include
from rest_framework import routers

from auth_app.views import CustomUserAPIView


user_router = routers.DefaultRouter()
user_router.register(r'users', CustomUserAPIView)

urlpatterns = [
    path('', include(user_router.urls)),
]