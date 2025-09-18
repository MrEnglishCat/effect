from django.db import models


class RolesModel(models.Model):
    name = models.CharField('Имя роли', max_length=100)
    description = models.TextField('Описание роли', null=True, blank=True)
