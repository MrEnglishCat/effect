from rest_framework.permissions import BasePermission


class AdminPermission(BasePermission):
    message = "Работа с таблицей полей {fields} разрешено только админам!"

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        # TODO тут добавить обработку на данные из таблицы пермишенов, с ресурсами
        return request.user.is_superuser or request.user.is_staff


class HasResourcePermission(BasePermission):
    """
    Проверяет разрешения на уровне view.
    """

    def has_permission(self, request, view):
        # Получаем ресурс и действие из view
        resource_name = getattr(view, 'resource_name', None)
        action_name = self._get_action_name(request.method)

        if not resource_name or not action_name:
            return True

        return self._check_permission(request.user.id, resource_name, action_name)

    def _get_action_name(self, method):
        mapping = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        return mapping.get(method)

    def _check_permission(self, user_id, resource_name, action_name):
        # Ваша логика проверки разрешений
        actions = get_user_permissions_for_resource(user_id, resource_name)
        return action_name in actions
