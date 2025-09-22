from rest_framework import serializers

from auth_app.models import ResourcesModel


class ResoursesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourcesModel
        fields = '__all__'
        read_only_fields = ('id',)