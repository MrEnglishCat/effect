from django.db import models


class ActionModel(models.Model):
    name = models.CharField('Название действия', max_length=100)
    description = models.TextField('Описание действия', null=True, blank=True)