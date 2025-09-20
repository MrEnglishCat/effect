from django.db import models


class IssueTokenModel(models.Model):
    jti = models.UUIDField(
        'UUID токена',
        primary_key=True,
        editable=False,
        db_index=True,
        help_text='JTI идентификатор токена.'
    )
    user = models.ForeignKey(
        'auth_app.CustomUserModel',
        on_delete=models.CASCADE,
        related_name='issue_tokens',
        verbose_name='Пользователь',
        help_text='Пользователь которому был выдан токен.'
    )
    issued_at = models.DateTimeField(
        'Дата выдачи',
        auto_now_add=True,
        db_index=True,
        help_text='Дата когда токен был сформирован.'
    )
    expiries_at = models.DateTimeField(
        'Срок действия',
        db_index=True,
        help_text='Дата когда завершается срок действия токена.'
    )
    is_revoked = models.BooleanField(
        'Отозван',
        default=False,
        db_index=True,
        help_text='Статус отозван или нет.'
    )
    revoked_at = models.DateTimeField(
        'Дата отзыва',
        null=True,
        blank=True,
        help_text='Дата когда был отзыван токен'
    )
    ip_address = models.GenericIPAddressField(
        'IP-адрес',
        null=True,
        blank=True,
        help_text='IP-адрес указанный в META запроса.'
    )
    user_agent = models.TextField(
        'user-Agent',
        blank=True,
        help_text='User-Agent браузера.'
    )
    last_used_at = models.DateTimeField(
        'Последнее использование',
        null=True,
        blank=True,
        help_text='Дата последнего обращения к токену'
    )

    def __str__(self):
        return f"Refresh-токен для {self.user.email} (jti: {self.jti})"

    class Meta:
        verbose_name = 'Refresh токен'
        verbose_name_plural = 'Refresh токены'

        ordering = ['-issued_at']
