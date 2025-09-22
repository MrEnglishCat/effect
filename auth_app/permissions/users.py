from rest_framework.permissions import BasePermission

# from auth_app.models import permissions


__all__ = [
    'CanEditUserFieldsPermission',
    'DeleteUserModelPermission',
    'PostUserModelPermission',
]


class CanEditUserFieldsPermission(BasePermission):
    message = f'Редактирование полей is_staff & is_superuser доступно только админам!'

    def has_permission(self, request, view):



        if any((field in request.data for field in ('is_staff', 'is_superuser', ))):
            if request.user.is_superuser:
                return request.user.is_superuser
            elif request.user.is_staff and 'is_superuser' not in request.data:
                return request.user.is_staff
            else:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        return True


class DeleteUserModelPermission(BasePermission):
    message = f'Удаление записи пользователя из БД доступно только админам!'

    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user.is_superuser

        return True

class PostUserModelPermission(BasePermission):
    message = f'Добавление записи пользователя в БД доступно только админам или сотрудникам!'

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_superuser or request.user.is_staff

        return True

