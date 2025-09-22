from rest_framework import serializers

from auth_app.models import CustomUserModel, IssueTokenModel, RolesModel

__all__ = [
    'CustomUserSerializer',
    'MyProfileSerializer',
    'RegisterCustomUserSerializer',
    'LoginCustomUserSerializer',
]

class CustomUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(help_text="Поле для повтора пароля, проверка на идентичность.", write_only=True, max_length=128, required=False)
    remove_roles = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Список ID ролей для удаления"
    )
    add_roles = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Список ID ролей для добавления"
    )

    class Meta:
        model = CustomUserModel
        exclude = ('last_login', 'date_joined', 'is_active')
        extra_kwargs = {
            'password': {'write_only': True},  # Пароль не возвращается в ответе
        }

    def validate_add_roles(self, value):
        if value:
            existing_roles = RolesModel.objects.filter(id__in=value).count()
            if existing_roles != len(value):
                raise serializers.ValidationError("Некоторые роли не существуют!")
        return value

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
        """
        При создании нужно передавать нужные роли в атрибут roles
        в виде списка
        :param validated_data:
        :return:
        """
        validated_data.pop('remove_roles', None)
        validated_data.pop('add_roles', None)
        validated_data.pop('remove_roles', None)

        roles = validated_data.pop('roles', [])

        user = CustomUserModel.objects.create_user(**validated_data)

        if roles:
            user.roles.set(roles)
            user.save()

        return user


    def update(self, instance, validated_data):
        """
        При редактировании записи, если нужно изменить роли пользователя(добавить, удалить)

        нужно передавать атрибуты add_roles - для добавления, remove_roles - для удаления
        Данные в них передаются в виде списка целых индексов ролей. Можно передавать как один из этих
        атрибутов так и оба.


        :param instance:
        :param validated_data:
        :return:
        """

        password = validated_data.pop('password', None)
        add_roles = validated_data.pop('add_roles', None)
        remove_roles = validated_data.pop('remove_roles', None)
        roles = validated_data.pop('add_roles', None)

        if password:
            instance.set_password(password)

        if add_roles:
            instance.roles.add(roles)

        if remove_roles:
            instance.roles.remove(roles)

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
