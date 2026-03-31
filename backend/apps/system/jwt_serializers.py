from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from .tokens import SESSION_VERSION_CLAIM, SessionVersionRefreshToken

User = get_user_model()


class SessionVersionTokenRefreshSerializer(TokenRefreshSerializer):
    """刷新前校验 refresh 中的 sv 与当前用户 session_version 一致。"""

    token_class = SessionVersionRefreshToken

    default_error_messages = {
        **TokenRefreshSerializer.default_error_messages,
        'session_invalidated': '会话已失效，请重新登录',
    }

    def validate(self, attrs):
        refresh = self.token_class(attrs['refresh'])
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        if user_id is not None:
            try:
                user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
            except User.DoesNotExist:
                raise AuthenticationFailed(
                    self.error_messages['no_active_account'],
                    'no_active_account',
                ) from None
            sv = refresh.payload.get(SESSION_VERSION_CLAIM)
            if sv is None or int(sv) != int(user.session_version):
                raise AuthenticationFailed(
                    self.error_messages['session_invalidated'],
                    'session_invalidated',
                )
        return super().validate(attrs)
