from datetime import datetime, timezone

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.jwt_service import JWTService
from users.models import User
from users.permissions import IsAuthenticated
from users.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {'detail': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = JWTService.create_access_token(user)
        refresh_token = JWTService.create_refresh_token(user)

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'user': UserSerializer(user).data,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({'detail': 'Токен не передан'}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header[7:]
        try:
            payload = JWTService.decode_token(token)
            jti = payload.get('jti')
            exp = payload.get('exp')
            if jti and exp:
                expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
                JWTService.blacklist_token(jti, expires_at)
        except Exception:
            pass

        return Response({'detail': 'Вы успешно вышли из системы'})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active', 'updated_at'])

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                payload = JWTService.decode_token(token)
                jti = payload.get('jti')
                exp = payload.get('exp')
                if jti and exp:
                    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
                    JWTService.blacklist_token(jti, expires_at)
            except Exception:
                pass

        return Response({'detail': 'Аккаунт деактивирован'})
