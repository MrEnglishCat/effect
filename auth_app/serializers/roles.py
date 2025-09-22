from rest_framework import serializers

from auth_app.models import RolesModel


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesModel
        fields = '__all__'
        read_only_fields = ('id',)
        # extra_kwargs = {
        #     'user': {'is_requare': False},
        # }