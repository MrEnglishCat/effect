from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from auth_app.models import ResourcesModel
from auth_app.permissions import AdminPermission
from auth_app.serializers.resourses import ResoursesModelSerializer


class ResoursesAPIView(ModelViewSet):
    resource_name = 'resourses'
    queryset = ResourcesModel.objects.all()
    serializer_class = ResoursesModelSerializer
    permission_classes = (IsAuthenticated, AdminPermission)
