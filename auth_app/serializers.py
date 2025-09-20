from rest_framework import serializers

from auth_app.models import CustomUserModel, IssueTokenModel


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        extra_kwargs = {'email': {'read_only': True}}
        exclude = ('password', 'last_login', 'date_joined')

    # TODO посмотреть как разрешить админам добавлять пользователей



class MyProfileSerializer(CustomUserSerializer):
    ...

class RegisterCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ('email', 'password', 'first_name', 'last_name', 'middle_name')
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True},

        }



class LoginCustomUserSerializer(RegisterCustomUserSerializer):
    ...

class ActiveSessionTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueTokenModel
        exclude = ('is_revoked', 'revoked_at', 'issued_at', 'user')


