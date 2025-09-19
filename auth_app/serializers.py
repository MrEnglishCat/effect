from rest_framework import serializers

from auth_app.models import CustomUserModel


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        extra_kwargs = {'email': {'read_only': True}}
        exclude = ('password',)


class RegisterCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ('email', 'password')



class LoginCustomUserSerializer(RegisterCustomUserSerializer):
    ...

