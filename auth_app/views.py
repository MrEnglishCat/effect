from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from auth_app.models import CustomUserModel
from auth_app.serializers import CustomUserSerializer
from django.contrib.auth import authenticate, login, logout

class CustomUserAPIView(ModelViewSet):
    queryset = CustomUserModel.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

