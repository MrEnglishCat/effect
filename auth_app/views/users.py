from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from auth_app.models import CustomUserModel
from auth_app.serializers import CustomUserSerializer, MyProfileSerializer


class MyProfileAPIView(ReadOnlyModelViewSet):
    serializer_class = MyProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return CustomUserModel.objects.filter(id=self.request.user.id)


class CustomUserAPIView(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):
    """
    endpoint Для работы с пользователем
    В зависимости от статуса is_staff=True or is_superuser=True - есть доступ ко всем учетным записям
    если False - то доступ только к своей.
    """
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)


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
