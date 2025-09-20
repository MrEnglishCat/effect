from datetime import UTC, datetime

from django.db import transaction, IntegrityError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from auth_app.models import CustomUserModel, IssueTokenModel, BlacklistToken
from auth_app.utils import TokenService


@receiver(pre_save, sender=CustomUserModel)
def get_old_is_active(sender, instance, **kwargs):
    '''
    Сигнал для сохранения старого значения is_active у instance.
    Дальше это значение используется в
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    '''
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_is_active = old.is_active
        except sender.DoesNotExist:
            instance._old_is_active = None

# TODO related_name - blacklist_tokens, issue_tokens


@receiver(post_save, sender=CustomUserModel)
def check_new_is_active(sender, instance, created, **kwargs):
    if created:
        return


    _old_is_active = getattr(instance, '_old_is_active', None)
    if not instance.is_active and _old_is_active is not None and instance.is_active != _old_is_active:
        __time_now = datetime.now(UTC)
        try:
            with transaction.atomic():
                tokens_to_revoke = instance.issue_tokens.filter(is_revoked=False).select_for_update()
                blacklist_tokens = (
                    BlacklistToken(
                        jti=token.jti,
                        user_id=token.user_id,
                        expires_at=token.expiries_at,
                        blacklist_at=__time_now
                    )
                    for token in tokens_to_revoke
                )

                BlacklistToken.objects.bulk_create(
                    blacklist_tokens
                )

                tokens_to_revoke.update(
                    is_revoked=True,
                    revoked_at=__time_now,
                    last_used_at=__time_now
                )
        except IntegrityError:
            pass