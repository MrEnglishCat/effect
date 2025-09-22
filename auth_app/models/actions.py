from django.db import models

from auth_app.models.permissions import PermissionsModel


class ActionsModel(models.Model):
    name = models.CharField(
        'Название действия',
        max_length=100,
        unique=True,
        help_text='Название действия, которое можно делать с ресурсом.'
    )
    description = models.TextField(
        'Описание действия',
        null=True,
        blank=True,
        help_text='Описание действия.')
    code_name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Кодовое название действия, на английском. Используется в коде'
    )
    resource = models.ManyToManyField(
        'auth_app.ResourcesModel',
        related_name='actions',
        through=PermissionsModel,
        help_text='Ресурс с которым связано действие.'
    )

    class Meta:
        verbose_name = 'Действие'
        verbose_name_plural = 'Действия'

    def __str__(self):
        return self.name
