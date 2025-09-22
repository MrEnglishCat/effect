from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from auth_app.models import RolesModel
from auth_app.permissions.users import AdminRolesPermission
from auth_app.serializers.roles import RolesSerializer


class RolesAPIView(ModelViewSet):
    model = RolesModel
    queryset = RolesModel.objects.all()
    serializer_class = RolesSerializer
    permission_classes = (IsAuthenticated, AdminRolesPermission)