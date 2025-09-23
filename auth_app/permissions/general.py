from rest_framework.permissions import BasePermission


class DeveleoperPermission(BasePermission):
    message = "Работа с таблицей полей {fields} разрешено только админам!"

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        return request.user.is_superuser

class AdminPermission(BasePermission):
    message = "Работа с таблицей полей {fields} разрешено только админам!"

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        return request.user.is_superuser or request.user.is_staff


