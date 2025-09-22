from idlelib.query import Query

from django.contrib.auth.models import Permission
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from auth_app.models import CustomUserModel, RolesModel, PermissionsModel
from auth_app.utils import TokenService



class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):

        auth_header = request.headers.get('Authorization')
        refresh_token = request.data.get('refresh_token')
        if not auth_header:
            return None

        if not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('Невалидный JWT токен!', status.HTTP_401_UNAUTHORIZED)

        token = auth_header.replace('Bearer ', '')
        payload = TokenService.decode_jwt_token(token)

        if not payload:
            raise AuthenticationFailed('Невалидный или истёкший токен!', status.HTTP_401_UNAUTHORIZED)

        # убрал что бы можно было авторизацию пройти по рефреш токену, при обновлении аксесс
        # if payload and  payload.get('type') == 'refresh':
        #     raise AuthenticationFailed('Передан неверный тип токена!', status.HTTP_401_UNAUTHORIZED)

        # roles = CustomUserModel.objects.get(pk=payload['user_id']).roles.prefetch_related('permissions__action_id__code_name', 'permissions__resource_id__code_name')
        # print(roles)

        # Получение пользователя со всеми ролями и их разрешениями
        user = CustomUserModel.objects.prefetch_related(
            'roles__permissions__resource_id',
            'roles__permissions__action_id'
        ).get(id=payload['user_id'])

        print(user.roles.all())



        roles = RolesModel.objects.prefetch_related(
            Prefetch(
                'permissions',
                queryset=PermissionsModel.objects.select_related('resource_id', 'action_id')
            )
        ).all()

        print(roles.query)

        for role in roles:
            print(f"Роль: {role.name}", role.users.select_related().all())

            for perm in role.permissions.all():
                print(f"  - {perm.resource_id.name} → {perm.action_id.name}")

        # Получить разрешения для конкретного ресурса
        user = CustomUserModel.objects.prefetch_related(
            Prefetch(
                'roles__permissions',
                queryset=PermissionsModel.objects.select_related('resource_id', 'action_id').filter(
                    resource_id__name='tests'
                )
            )
        ).get(id=payload['user_id'])
        print('='*100)
        print(user)
        try:
            user = CustomUserModel.objects.get(pk=payload['user_id'], is_active=True)
        except CustomUserModel.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден!', status.HTTP_401_UNAUTHORIZED)
        else:
            return user, token



    def authenticate_header(self, request):
        return f'Bearer realm="api"'
