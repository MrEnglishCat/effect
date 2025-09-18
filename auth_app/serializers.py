from rest_framework import serializers

from auth_app.models import CustomUserModel


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ('id', 'email')
        extra_kwargs = {'email': {'read_only': True}}
