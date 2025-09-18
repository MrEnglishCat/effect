from django.db import models


class RolesModel(models.Model):
    name = models.CharField('Имя роли', max_length=100, unique=True)
    description = models.TextField('Описание роли', null=True, blank=True)
    permissions = models.ManyToManyField('auth_app.PermissionsModel', related_name='roles', blank=True,
                                         verbose_name='Список ролей')
    user = models.ManyToManyField('auth_app.CustomUserModel', related_name='users')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name
