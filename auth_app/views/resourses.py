from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from auth_app.models import ResourcesModel
from auth_app.permissions.general import DeveleoperPermission
from auth_app.serializers.roles import ResoursesSerializer


class ResoursesAPIView(ModelViewSet):
    resource_name = 'resources'
    queryset = ResourcesModel.objects.all()
    serializer_class = ResoursesSerializer
    permission_classes = (IsAuthenticated, DeveleoperPermission)
