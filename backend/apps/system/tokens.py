"""JWT 携带 session_version（claim: sv），与 User.session_version 对齐以实现会话失效/踢出。"""
from __future__ import annotations

from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken as BaseRefreshToken
from rest_framework_simplejwt.utils import datetime_from_epoch

# 短名减少 payload 体积
SESSION_VERSION_CLAIM = 'sv'


class SessionVersionAccessToken(AccessToken):
    pass


class SessionVersionRefreshToken(BaseRefreshToken):
    access_token_class = SessionVersionAccessToken

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token[SESSION_VERSION_CLAIM] = int(user.session_version)
        # BlacklistMixin 在写入 sv 之前已把 str(token) 记入 OutstandingToken，需同步最终串
        if 'rest_framework_simplejwt.token_blacklist' in settings.INSTALLED_APPS:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
            from rest_framework_simplejwt.settings import api_settings

            jti = token[api_settings.JTI_CLAIM]
            exp = token['exp']
            OutstandingToken.objects.filter(jti=jti).update(
                token=str(token),
                expires_at=datetime_from_epoch(exp),
            )
        return token
