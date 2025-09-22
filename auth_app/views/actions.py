from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from auth_app.models import ActionsModel
from auth_app.permissions.general import DeveleoperPermission
from auth_app.serializers import ActionsSerializer

class ActionsViewSet(viewsets.ModelViewSet):
    resource_name = 'actions'
    queryset = ActionsModel.objects.all()
    serializer_class = ActionsSerializer
    permission_classes = (IsAuthenticated, DeveleoperPermission)