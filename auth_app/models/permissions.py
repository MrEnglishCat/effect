from django.db import models


class PermissionsModel(models.Model):

    resource = models.ForeignKey('auth_app.ResourcesModel', on_delete=models.CASCADE, help_text='Значение ресурса в транзитной таблице.')
    action = models.ForeignKey('auth_app.ActionsModel', on_delete=models.CASCADE, help_text='Значение действия в транзитной таблице.')


    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'
        unique_together = ('resource', 'action')


    def __str__(self):
        return f"Разрешение {self.action.name} для {self.resource.name}"