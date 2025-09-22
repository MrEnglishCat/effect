from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, \
    CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from auth_app.models import CustomUserModel
# from auth_app.permissions import CanEditUserFieldsPermission, DeleteUserModelPermission, PostUserModelPermission
from auth_app.permissions import *
from auth_app.serializers import CustomUserSerializer, MyProfileSerializer


# TODO  ему выдается запрашиваемый ресурс.
#  (ПЕРЕПРОВЕРИТЬ)Если пользователь определен, но запрашиваемый ресурс ему не доступен 403 ошибка — Forbidden.
#  *
#  2. Система разграничения прав доступа.
#   	Вы должны продумать и в текстовом файле или в REAME.md описать схему вашей структуры управления ограничениями доступа.
#   	Реализованы соответствующие таблицы в БД.
#   	Таблицы заполнены тестовыми данными для минимальной отработки приложения для демонстрации работающей системы.
#   	Если пользователь имеет доступ к ресурсу по вышеописанным правилам, ему выдается запрашиваемый ресурс. Если по входящему запросу не удается определить залогиненного пользователя, выдается ошибка 401. Если пользователь определен, но запрашиваемый ресурс ему не доступен 403 ошибка — Forbidden.
#   	Реализовать API с возможностью получения и изменения этих правил пользователю, имеющему роль администратора.
#   3. Минимальные вымышленные объекты бизнес-приложения, к которым могла бы применяться созданная система.
#   Таблицы в БД создавать не требуется. Можно просто написать Mock-View, которые по обращениям будут выдавать список потенциальных объектов или описанные выше ошибки.

# TODO Добавить ограничение количества запросов к АПИ

class MyProfileAPIView(ReadOnlyModelViewSet):
    serializer_class = MyProfileSerializer
    permission_classes = (IsAuthenticated, DynamicResourcePermission)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return CustomUserModel.objects.filter(id=self.request.user.id)


class CustomUserAPIView(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
):
    """
    endpoint Для работы с пользователем
    В зависимости от статуса is_staff=True or is_superuser=True - есть доступ ко всем учетным записям
    если False - то доступ только к своей.
    """
    resource_name = 'users'
    queryset = CustomUserModel.objects.all()
    serializer_class = CustomUserSerializer

    permission_classes = (
        IsAuthenticated,
        # CanEditUserFieldsPermission,
        # DeleteUserModelPermission,
        # PostUserModelPermission,
        DynamicResourcePermission

    )

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
