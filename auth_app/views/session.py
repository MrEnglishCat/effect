from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from auth_app.models import SessionsModel
from auth_app.permissions import IsSupervisor
from auth_app.serializers.sessions import SessionSerializer


class SessionsViewSet(viewsets.ModelViewSet):
    queryset = SessionsModel.objects.all()
    serializer_class = SessionSerializer
    permission_classes = (IsAuthenticated, IsSupervisor)



