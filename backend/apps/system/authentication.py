from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

from .tokens import SESSION_VERSION_CLAIM


class SessionVersionJWTAuthentication(JWTAuthentication):
    """校验 access token 中的 sv 与数据库中 User.session_version 一致。"""

    def get_user(self, validated_token) -> AbstractBaseUser:
        user = super().get_user(validated_token)
        sv = validated_token.get(SESSION_VERSION_CLAIM)
        if sv is None:
            raise InvalidToken('缺少会话版本信息，请重新登录')
        if int(sv) != int(user.session_version):
            raise InvalidToken('会话已失效，请重新登录')
        return user
