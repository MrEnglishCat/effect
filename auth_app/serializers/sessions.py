from rest_framework import serializers
from auth_app.models import IssueTokenModel, SessionsModel


class ActiveSessionTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueTokenModel
        exclude = ('is_revoked', 'revoked_at', 'issued_at', 'user')


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionsModel
        # exclude = ('user',)
        fields = '__all__'





