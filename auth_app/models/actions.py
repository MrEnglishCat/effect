from django.db import models

from auth_app.models.permissions import PermissionsModel


class ActionsModel(models.Model):
    name = models.CharField('Название действия', max_length=100, unique=True)
    description = models.TextField('Описание действия', null=True, blank=True)
    resource = models.ManyToManyField('auth_app.ResoursesModel', related_name='actions', through=PermissionsModel)


    class Meta:
        verbose_name = 'Действие'
        verbose_name_plural = 'Действия'


    def __str__(self):
        return self.name