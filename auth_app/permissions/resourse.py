from django.db.models import Prefetch
from rest_framework.permissions import BasePermission

from auth_app.models import CustomUserModel, RolesModel, PermissionsModel


class DynamicResourcePermission(BasePermission):

    def has_permission(self, request, view):
        resource_name = getattr(view, 'resource_name', None)
        if not resource_name:
            return False

        print(f"🔍 Ищем разрешения для ресурса: {resource_name}")

        try:
            user = CustomUserModel.objects.prefetch_related(
                Prefetch(
                    'roles__permissions',
                    queryset=PermissionsModel.objects.select_related(
                        'resource',
                        'action'
                    ).filter(
                        resource__code_name=resource_name
                    )
                )
            ).get(id=request.user.id)

            print(f"👤 Пользователь: {user.email}")
            print(f"🎭 Роли пользователя: {[role.name for role in user.roles.all()]}")

            # Отладка: смотрим все роли и их разрешения
            for role in user.roles.all():
                print(f"  📋 Роль: {role.name}")
                permissions = role.permissions.all()
                print(f"    🔐 Разрешения: {permissions.count()}")
                for perm in permissions:
                    print(f"      - {perm.resource.code_name} → {perm.action.name}")

            # Собираем уникальные действия
            actions = set()
            for role in user.roles.all():
                for permission in role.permissions.all():
                    actions.add(permission.action.name)

            print(f"✅ Доступные действия: {list(actions)}")
            # for action in actions:
            #     print(action.code_name)
            return len(actions) > 0

        except CustomUserModel.DoesNotExist:
            print("❌ Пользователь не найден")
            return False
        except Exception as e:
            print(f"💥 Ошибка: {e}")
            return False