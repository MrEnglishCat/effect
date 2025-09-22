from django.db.models import Prefetch
from rest_framework.permissions import BasePermission

from auth_app.models import CustomUserModel, RolesModel, PermissionsModel
from auth_app.utils import RequestMethods

class DynamicResourcePermission(BasePermission):

    def has_permission(self, request, view):
        resource_name = getattr(view, 'resource_name', None)
        if not resource_name:
            return False

        # print(f"🔍 Ищем разрешения для ресурса: {resource_name}")

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

            # print(f"👤 Пользователь: {user.email}")
            # print(f"🎭 Роли пользователя: {[role.name for role in user.roles.all()]}")

            # для отладки
            # for role in user.roles.all():
            #     print(f"  📋 Роль: {role.name}")
            #     permissions = role.permissions.all()
            #     print(f"    🔐 Разрешения: {permissions.count()}")
            #     for perm in permissions:
            #         print(f"      - {perm.resource.code_name} → {perm.action.name}")

            actions = set()
            for role in user.roles.all():
                for permission in role.permissions.all():
                    actions.add(permission.action.code_name)

            # print(f"✅ Доступные действия: {list(actions)}")
            # for action in actions:
            #     print(action)



            if actions:
                view.actions = list(actions)
                if 'all' in view.actions:
                    return True
                request_methods = {
                    RequestMethods.GET.name: RequestMethods.GET.value,
                    RequestMethods.POST.name: RequestMethods.POST.value,
                    RequestMethods.PUT.name: RequestMethods.PUT.value,
                    RequestMethods.PATCH.name: RequestMethods.PATCH.value,
                    RequestMethods.DELETE.name: RequestMethods.DELETE.value,
                }

                if request_methods.get(request.method, False) in view.actions:
                    return True
            return False
        except CustomUserModel.DoesNotExist:
            return False
        except Exception as e:
            return False