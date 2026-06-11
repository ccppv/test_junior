from rest_framework import authentication, exceptions

from users.jwt_service import JWTService
from users.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith(f'{self.keyword} '):
            return None

        token = auth_header[len(self.keyword) + 1:]
        try:
            payload = JWTService.decode_token(token)
        except Exception:
            raise exceptions.AuthenticationFailed('Недействительный или просроченный токен')

        if payload.get('type') != 'access':
            raise exceptions.AuthenticationFailed('Неверный тип токена')

        jti = payload.get('jti')
        if jti and JWTService.is_blacklisted(jti):
            raise exceptions.AuthenticationFailed('Токен отозван')

        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Пользователь не найден или деактивирован')

        return user, token

    def authenticate_header(self, request):
        return self.keyword
