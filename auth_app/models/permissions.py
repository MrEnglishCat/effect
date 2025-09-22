from django.db import models


class PermissionsModel(models.Model):

    resource_id = models.ForeignKey('auth_app.ResourcesModel', on_delete=models.CASCADE, help_text='Значение ресурса в транзитной таблице.')
    action_id = models.ForeignKey('auth_app.ActionsModel', on_delete=models.CASCADE, help_text='Значение действия в транзитной таблице.')


    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'
        unique_together = ('resource_id', 'action_id')


    def __str__(self):
        return f"Разрешение {self.action_id.name} для {self.resource_id.name}"