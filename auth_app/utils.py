import uuid
from copy import deepcopy
from datetime import datetime, timedelta, UTC
from os import access
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
        expiret_at = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRATION)
        # expiret_at = datetime.now(UTC) + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRATION)
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
    def decode_jwt_token(cls, token: str, options: dict = None) -> dict | None:
        """
        Декодирует токен в paylod(для получения полезных данных из токена)
        :param token: сам токен
        :param options: опции для метода decode в jwt (основное назначение
                        подавление исключения ExpiredSignatureError -
                        связанного с истекшим токеном)
        :return: словарь с payload - токена. или None в случае ошибки
        """

        kwargs = {
            'key': settings.JWT_SECRET_KEY,
            'algorithms': settings.JWT_ALGORITHM,
        }

        if options:
            kwargs.update(
                {
                    'options': options,
                }
            )
        try:
            payload = jwt.decode(
                token,
                **kwargs,
            )
            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError as e:
            return None

    @classmethod
    def revoke_jwt_token(cls, user_id: int, jti: Optional[str] = None, is_revoke_all: bool = False):
        """
        Отзывает один токен по jti или все токены пользователя.
        True в success возвращает только при успешном отзыве токена. Во всех остальных случаях False

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
            revoked_at=datetime.now(UTC),
            last_used_at=datetime.now(UTC)
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

    @staticmethod
    def _is_expired_token(token_expires_at: int) -> bool:
        """
        Пока что нужен только в методе reset_jwt_refresh_token - для обновления даты отзыва
        в таблицах и добавления токена в balcklist
        :param token_expires_at:
        :return:
        """
        if datetime.fromtimestamp(token_expires_at, UTC) < datetime.now(UTC):
            return True
        return False

    @classmethod
    def reset_jwt_refresh_token(cls, request_token: str, user):
        """

        :param request_token:
        :param user:
        :return:
        """
        payload, jti, user_id, exp, errors = cls.check_jwt_token(request_token, user,
                                                                 options=settings.JWT_DECODE_OPTIONS)
        if errors:
            return None, None, errors

        if cls._is_expired_token(exp):
            success, message, status_code, count_revoked_tokens = cls.revoke_jwt_token(user_id, jti)
            message = f"{message} Refresh-токен невалиден(TTL)! Токен: {jti}  отозван! Пройдите повторно авторизацию(логин и пароль)!'"
            return None, None, ((success, message, status_code),)

        IssueTokenModel.objects.filter(jti=jti, user_id=user_id).update(
            last_used_at=datetime.now(UTC),
        )

        access_token = cls.generate_access_token(user)
        return access_token, request_token, None

    @classmethod
    def revoke_if_expired(cls, *update_date, **base_filter):
        """
        ПОПЫТКА ЗАМЕНИТЬ ЧАСТЬ ПОВТОРЯЮЩЕГОСЯ КОДА ДЛЯ ОТЗЫВА ТОКЕНОВ
        Используется в reset_jwt_refresh_token
        141 - 162 строки кода
        :param update_date:
        :param base_filter:
        :return:
        """
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
            revoked_at=datetime.now(UTC),
            last_used_at=datetime.now(UTC)
        )

    @classmethod
    def check_jwt_token(cls, request_token, request_user=None, **kwargs):
        """
        Проверяет refresh-токен и возвращает payload, jti и ошибки.
        Если request_user передан — проверяет, что токен принадлежит пользователю.
        :param request_token:
        :param request_user: применяется при проверках токена НЕ админами(is_staff, is_superuser)
        :param **kwargs: использую для получения options для метода decode_jwt_token
        :return: payload, jti, user_id, exp, errors
        """
        errors = []

        payload = cls.decode_jwt_token(request_token, options=kwargs.pop('options', None) if kwargs else None)
        if not payload:
            errors.append(
                (
                    'Невалидный или истёкший токен!',
                    status.HTTP_400_BAD_REQUEST
                )
            )
            return None, None, None, None, errors

        # Т. к. пока что метод используется только для валидации refresh токенов
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

        if request_user and user_id != request_user.id:
            errors.append(
                (
                    f'Попытка отзыва токена(USER_ID#{request_user.id}) другого пользователя: ID#{user_id}!',
                    status.HTTP_403_FORBIDDEN
                )
            )
            return None, None, None, None, errors

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

    @classmethod
    def check_and_revoke_jwt_token(cls, refresh_token: str) -> tuple[dict, str, int, int, list | tuple]:
        """
        Часть кода начала повторяться в нескольких местах
        Метод для проверки refresh токена и его последующего отзыва, если время действия токена истекло

        :param refresh_token:
        :return: is_revoked, token_data, revoke_data
                data - (payload, jti, user_id, exp, errors)
                revoke_data - (success, message, status_code, count_revoked_tokens)
        """
        is_revoked = False
        payload, jti, user_id, exp, errors = cls.check_jwt_token(refresh_token,
                                                                 options=settings.JWT_DECODE_OPTIONS)
        if errors:
            return is_revoked, (payload, jti, user_id, exp, errors), None

        if cls._is_expired_token(exp) or IssueTokenModel.objects.filter(jti=jti, user_id=user_id, is_revoked=True).exists():
            success, message, status_code, count_revoked_tokens = cls.revoke_jwt_token(user_id, jti=jti)

            is_revoked = True
            return is_revoked, (payload, jti, user_id, exp, None), (success, message, status_code, count_revoked_tokens)

        return is_revoked, (payload, jti, user_id, exp, None), None
