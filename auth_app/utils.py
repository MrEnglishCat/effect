import uuid
from datetime import datetime, timedelta

import jwt
from django.conf import settings


def generate_access_token(user_id):
    jti = str(uuid.uuid4())
    payload = {
        'user_id': user_id,
        'iat': int(datetime.now().timestamp()),
        'expires': int((datetime.now() + timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRATION)).timestamp()),
        'jti': jti,
        'type': 'access'
    }
    return jwt.encode(
        payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )



def generate_refresh_token(user_id):
    jti = str(uuid.uuid4())
    payload = {
        'user_id': user_id,
        'iat': int(datetime.now().timestamp()),
        'expires': int((datetime.now() + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRATION)).timestamp()),
        'jti':jti,
        'type': 'refresh'
    }
    return jwt.encode(
        payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,

    )



def generate_tokens(user_id):
    return generate_access_token(user_id), generate_refresh_token(user_id)


def decode_token(token):
    clear_token = jwt.decode(token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    # TODO доделать декодирование токена
    return clear_token


