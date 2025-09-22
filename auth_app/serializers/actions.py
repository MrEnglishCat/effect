from rest_framework import serializers

from auth_app.models import ActionsModel


class ActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionsModel
        fields = '__all__'
        read_only_fields = ('id',)