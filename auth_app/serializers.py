from rest_framework import serializers

from auth_app.models import CustomUserModel, IssueTokenModel


class CustomUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, max_length=128, required=False)

    class Meta:
        model = CustomUserModel
        exclude = ('last_login', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True},  # Пароль не возвращается в ответе
        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('password2', None)
        if password != password2:
            raise serializers.ValidationError("Пароли не совпадают")
        return data


class MyProfileSerializer(CustomUserSerializer):
    ...

class RegisterCustomUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField( max_length=128, required=True)
    class Meta:
        model = CustomUserModel
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'middle_name')
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True},
            'password2': {'required': True},

        }


    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('password2', None)
        if password != password2:
            raise serializers.ValidationError("Пароли не совпадают")
        return data


class LoginCustomUserSerializer(RegisterCustomUserSerializer):
    ...

class ActiveSessionTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueTokenModel
        exclude = ('is_revoked', 'revoked_at', 'issued_at', 'user')


