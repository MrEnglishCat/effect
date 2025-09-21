from django.db import models


class RolesModel(models.Model):
    name = models.CharField('Название роли', max_length=100, unique=True, help_text='Название роли.')
    code_name = models.CharField('Код роли', max_length=100, unique=True, help_text='Кодовое название на английском, используется для определения прав в коде.')
    description = models.TextField('Описание роли', null=True, blank=True, help_text='Описание роли, к примеру что делает или для кого.')
    permissions = models.ManyToManyField('auth_app.PermissionsModel', related_name='roles', blank=True,
                                         verbose_name='Список ролей', help_text='Связь со списком ролей и ресурсами.')
    users = models.ManyToManyField('auth_app.CustomUserModel', related_name='roles', help_text='Поле для связи роли с пользователями и конкретным пользователем.')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name
