from django.db import models



class BlacklistToken(models.Model):

    jti = models.UUIDField("JTI токена", editable=False, db_index=True)
    user = models.ForeignKey('auth_app.CustomUserModel', on_delete=models.CASCADE, related_name='blacklist_tokens')
    blacklist_at = models.DateTimeField("Дата отзыва токена", auto_now_add=True)
    expires_at = models.DateTimeField("Срок действия токена")


    def __str__(self):
        return self.jti


    class Meta:
        verbose_name = 'Отозванный токен'
        verbose_name_plural = 'Отозванные токены'
        unique_together = (('user', 'jti'),)


