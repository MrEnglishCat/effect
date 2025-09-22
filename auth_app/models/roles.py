from django.db import models


class RolesModel(models.Model):
    name = models.CharField('Название роли', max_length=100, unique=True, help_text='Название роли.')
    code_name = models.CharField('Код роли',  max_length=100, unique=True, help_text='Кодовое название на английском, используется для определения прав в коде.')
    description = models.TextField('Описание роли', null=True, blank=True, help_text='Описание роли, к примеру что делает или для кого.')
    permissions = models.ManyToManyField('auth_app.PermissionsModel', related_name='roles',
                                         verbose_name='Список ролей', help_text='Связь со списком ролей и ресурсами.')



    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        unique_together = ('name', 'code_name',)

    def __str__(self):
        return self.name
