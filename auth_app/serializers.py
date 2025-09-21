from rest_framework import serializers

from auth_app.models import CustomUserModel, IssueTokenModel


class CustomUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(help_text="Поле для повтора пароля, проверка на идентичность.", write_only=True, max_length=128, required=False)

    class Meta:
        model = CustomUserModel
        exclude = ('last_login', 'date_joined', 'is_active')
        extra_kwargs = {
            'password': {'write_only': True},  # Пароль не возвращается в ответе
        }

    def validate_email(self, value):
        if self.instance and self.instance.email != value:
            raise serializers.ValidationError("Email нельзя изменить!")
        return value

    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('password2', None)

        if password and not password2:
            raise serializers.ValidationError("Повторный пароль обязателен!")
        if password and password != password2:
            raise serializers.ValidationError("Пароли не совпадают!")
        return data


    def create(self, validated_data):
        return CustomUserModel.objects.create_user(**validated_data)


    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        if password:
            instance.set_password(password)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

#
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
            raise serializers.ValidationError("Пароли не совпадают!")
        return data


class LoginCustomUserSerializer(RegisterCustomUserSerializer):
    ...

class ActiveSessionTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueTokenModel
        exclude = ('is_revoked', 'revoked_at', 'issued_at', 'user')


