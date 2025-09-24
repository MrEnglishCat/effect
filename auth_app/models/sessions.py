import uuid
from datetime import timedelta, UTC, datetime

from django.db import models


class SessionsModel(models.Model):
    """
    Хотел еще добавить возможность использовать сессии. Не успел. Добавил частично только в логин
    """
    uuid = models.UUIDField('UUID сессии пользователя',  db_index=True, default=uuid.uuid4(), editable=False, help_text='uuid сессии пользователя.')
    # ip_address = models.GenericIPAddressField('IP-адрес пользователя', blank=False, null=False, help_text='IP-адрес пользователя из META запроса.')
    # user_agent = models.TextField('User-Agent', default='', null=False, blank=False, help_text='User-Agent поступивший от запроса.')
    created_at = models.DateTimeField('Дата создания сессии', auto_now_add=True, help_text='Дата создания учётной записи пользователя.')
    expires_at = models.DateTimeField('Дата истечения сессии', help_text='Дата истечения срока сессии.')
    is_active = models.BooleanField('Активна ли сессия', default=True, help_text='Определяет была ли отозвана текущая сессия')
    # user = models.ForeignKey('auth_app.CustomUserModel', related_name='sessions', on_delete=models.CASCADE, help_text='Поле для связи с пользователем.')

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return f"Сессия {self.uuid} для {self.user.email}"

    def save(self, *args, **kwargs):

        if not self.pk and not self.expires_at:
            if not self.created_at:
                self.created_at = datetime.now(UTC)

            self.expires_at = self.expires_at + timedelta(days=1)

        super().save(*args, **kwargs)
