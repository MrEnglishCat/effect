import uuid
from datetime import datetime, timedelta, UTC

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
    def revoke_jwt_token(cls, jti, user_id, expires_at):
        revoked = IssueTokenModel.objects.filter(
            jti=jti,
            user_id=user_id,
            is_revoked=False
        ).update(
            is_revoked=True,
            revoke_at=datetime.now(UTC)
        )

        if revoked > 0:
            BlacklistToken.objects.create(
                jti=jti,
                user_id=user_id,
                expires_at=datetime.fromtimestamp(expires_at),
            )

            return True, f"Токен {jti} успешно отозван!", status.HTTP_200_OK
        else:
            return False, 'Токен уже был отозван. Повторная попытка отозвать ОТОЗВАННЫЙ токен!', status.HTTP_400_BAD_REQUEST

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

        if request_user and user_id != request_user.id:
            errors.append(
                (
                    'Токен не принадлежит текущему пользователю!',
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
