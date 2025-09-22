from rest_framework import serializers

from auth_app.models import RolesModel, PermissionsModel, ResourcesModel, ActionsModel


# Цепочка сериализаторов ниже, помогает обработать запрос на получение всей информации по юзеру

class ResoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourcesModel
        fields = '__all__'
        read_only_fields = ('id',)


class ActionsSerializer(serializers.ModelSerializer):
    resource = ResoursesSerializer(many=True, read_only=True)
    class Meta:
        model = ActionsModel
        fields = '__all__'
        read_only_fields = ('id',)

class PermissionSerializer(serializers.ModelSerializer):
    action = ActionsSerializer()

    class Meta:
        model = PermissionsModel
        fields = '__all__'

class RolesSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = RolesModel
        fields = '__all__'
