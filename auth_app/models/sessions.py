import uuid
from datetime import timedelta, UTC, datetime

from django.db import models


class SessionsModel(models.Model):
    uuid = models.UUIDField('UUID сессии пользователя', unique=True, db_index=True, default=uuid.uuid4(),
                            editable=False)
    ip_address = models.GenericIPAddressField('IP-адрес пользователя', blank=False, null=False)
    created_at = models.DateTimeField('Дата создания сессии', auto_now_add=True)
    expiries_at = models.DateTimeField('Дата истечения сессии')
    user = models.ForeignKey('auth_app.CustomUserModel', related_name='sessions', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return f"Сессия {self.uuid} для {self.user.username}"

    def save(self, *args, **kwargs):

        if not self.pk and not self.expiries_at:
            if not self.created_at:
                self.created_at = datetime.now(UTC)

            self.expiries_at = self.expiries_at + timedelta(days=1)

        super().save(*args, **kwargs)
