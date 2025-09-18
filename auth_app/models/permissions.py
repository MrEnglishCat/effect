from importlib import resources

from django.db import models


class PermissionsModel(models.Model):

    resource_id = models.ForeignKey('auth_app.ResoursesModel', on_delete=models.CASCADE)
    action_id = models.ForeignKey('auth_app.ActionsModel', on_delete=models.CASCADE)


    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'
        unique_together = ('resource_id', 'action_id')


    def __str__(self):
        return f"Разрешение {self.action_id.name} для {self.resource_id.name}"