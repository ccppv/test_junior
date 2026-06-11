import uuid
from datetime import datetime, timezone

import jwt
from django.conf import settings

from users.models import BlacklistedToken, User


class JWTService:
    @staticmethod
    def create_access_token(user: User) -> str:
        payload = {
            'user_id': user.id,
            'email': user.email,
            'type': 'access',
            'jti': str(uuid.uuid4()),
            'exp': datetime.now(timezone.utc) + settings.JWT_ACCESS_TOKEN_LIFETIME,
            'iat': datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def create_refresh_token(user: User) -> str:
        payload = {
            'user_id': user.id,
            'type': 'refresh',
            'jti': str(uuid.uuid4()),
            'exp': datetime.now(timezone.utc) + settings.JWT_REFRESH_TOKEN_LIFETIME,
            'iat': datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

    @staticmethod
    def blacklist_token(jti: str, expires_at: datetime) -> None:
        BlacklistedToken.objects.get_or_create(
            jti=jti,
            defaults={'expires_at': expires_at},
        )

    @staticmethod
    def is_blacklisted(jti: str) -> bool:
        BlacklistedToken.cleanup_expired()
        return BlacklistedToken.objects.filter(jti=jti).exists()
