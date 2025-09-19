import uuid
from copy import deepcopy
from datetime import datetime, timedelta, UTC
from typing import Optional

import jwt
from django.conf import settings
from rest_framework import status

from auth_app.models import IssueTokenModel, BlacklistToken


class TokenService:

    @classmethod
    def generate_access_token(cls, user, **kwargs):
        jti = str(uuid.uuid4())
        payload = {
            'user_id': user.id,
            'iat': int(datetime.now(UTC).timestamp()),
            'exp': int((datetime.now(UTC) + timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRATION)).timestamp()),
            'jti': jti,
            'type': 'access',

        }

        if kwargs:
            payload.update(kwargs)
        return jwt.encode(
            payload,
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @classmethod
    def generate_refresh_token(cls, user, ip_address=None, user_agent=None, **kwargs):
        jti = str(uuid.uuid4())
        expiret_at = datetime.now(UTC) + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRATION)
        payload = {
            'user_id': user.id,
            'iat': int(datetime.now(UTC).timestamp()),
            'exp': int(expiret_at.timestamp()),
            'jti': jti,
            'type': 'refresh',
        }

        IssueTokenModel.objects.create(
            jti=jti,
            user=user,
            expiries_at=expiret_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if kwargs:
            payload.update(kwargs)

        return jwt.encode(
            payload,
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,

        )

    @classmethod
    def generate_jwt_tokens(cls, user, **kwargs) -> tuple:
        ip_address = kwargs.pop('ip_address', None)
        user_agent = kwargs.pop('user_agent', None)
        return (
            cls.generate_access_token(user, **kwargs),
            cls.generate_refresh_token(user, ip_address=ip_address, user_agent=user_agent, **kwargs)
        )

    @classmethod
    def decode_jwt_token(cls, token):
        try:
            payload = jwt.decode(token, key=settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError as e:
            return None

    @classmethod
    def revoke_jwt_token(cls,  user_id: int, jti: Optional[str] = None, is_revoke_all: bool = False):
        """
        Отзывает один токен по jti или все токены пользователя.

        :param user_id: ID пользователя (обязательно)
        :param jti: UUID токена (опционально). Если None — отзываем все токены пользователя.
        :return: (успешно: bool, сообщение: str, статус: int, количество_отозванных: int)
        """
        if not isinstance(user_id, int) or user_id <= 0:
            return False, 'Невалидный user_id!', status.HTTP_400_BAD_REQUEST, 0

        base_filter = {
            'user_id': user_id,
            'is_revoked': False,
        }

        if jti is not None and not is_revoke_all:
            try:
                base_filter['jti'] = jti
                jti_uuid = uuid.UUID(jti, version=4) if not isinstance(jti, uuid.UUID) else jti
                base_filter['jti'] = jti_uuid
            except (ValueError, TypeError):
                return False, 'Невалидный формат jti!', status.HTTP_400_BAD_REQUEST, 0


        tokens_to_revoke = IssueTokenModel.objects.filter(**base_filter).select_for_update()
        if tokens_to_revoke.count() == 0:
            return False, 'Нет активных токенов для отзыва.', status.HTTP_200_OK, 0

        count_error_revoke_tokens = 0



        for token in tokens_to_revoke:
            try:
                BlacklistToken.objects.create(
                    jti=token.jti,
                    user_id=token.user_id,
                    expires_at=token.expiries_at,
                )
            except Exception as e:
                count_error_revoke_tokens += 1
                print(f"Ошибка при создании BlacklistToken для jti={token.jti}: {e}!")

        count_revoked_tokens = tokens_to_revoke.update(
            is_revoked=True,
            revoked_at=datetime.now(UTC)
        )


        if jti is not None:
            if count_revoked_tokens > 0:
                success = True
                message = f"Токен {jti} успешно отозван!"
                status_code = status.HTTP_200_OK
            else:
                success = False
                message = 'Токен уже был отозван. Повторная попытка отозвать ОТОЗВАННЫЙ токен!'
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            success = True
            message = f"Было отозвано токенов:{count_revoked_tokens - count_error_revoke_tokens}, пользователя: ID#{user_id}"
            status_code = status.HTTP_200_OK

        return success, message, status_code, count_revoked_tokens


    @classmethod
    def reset_jwt_tokens(cls, user_id: int, is_revoke_all: bool = False):
        ...


    @classmethod
    def check_jwt_token(cls, request_token, request_user=None):
        """
        Проверяет refresh-токен и возвращает payload, jti и ошибки.
        Если request_user передан — проверяет, что токен принадлежит пользователю.
        :param token:
        :return: payload, jti, errors
        """
        errors = []

        payload = cls.decode_jwt_token(request_token)

        if not payload:
            errors.append(
                (
                    'Невалидный или истёкший токен!',
                    status.HTTP_400_BAD_REQUEST
                )
            )
            return None, None, None, None, errors

        if payload.get('type') != 'refresh':
            errors.append(
                (
                    'Передан неверный тип токена!',
                    status.HTTP_400_BAD_REQUEST
                )
            )
            return None, None, None, None, errors

        jti_str = payload.get('jti')
        user_id = payload.get('user_id')
        exp = payload.get('exp')

        if not all([jti_str, user_id, exp]):
            # if not all(((key in ('jti', 'exp', 'user_id') for key in payload))):  # альтернативный вариант
            errors.append(
                (
                    'Нет необходимых данных в токене!',
                    status.HTTP_400_BAD_REQUEST
                )
            )
            return None, None, None, None, errors

        # TODO эта часть кода мешает если админы будут отзывать токены
        # if request_user and user_id != request_user.id:
        #     errors.append(
        #         (
        #             f'Попытка отзыва токена(USER_ID#{request_user.id}) другого пользователя: ID#{user_id}!',
        #             status.HTTP_403_FORBIDDEN
        #         )
        #     )
        #     return None, None, None, None, errors

        try:
            jti = uuid.UUID(jti_str)
        except ValueError:
            errors.append(
                (
                    'Невалидный формат jti!',
                    status.HTTP_400_BAD_REQUEST
                )
            )
            return None, None, None, None, errors


        return payload, jti, user_id, exp, None
