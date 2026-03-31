from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import AuditLog, Notification, Permission, Role, User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'module', 'action']
        read_only_fields = fields


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description',
            'permissions', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), required=False,
        source='permissions',
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permission_ids']

    def create(self, validated_data: dict) -> Role:
        permissions = validated_data.pop('permissions', [])
        role = Role.objects.create(**validated_data)
        if permissions:
            role.permissions.set(permissions)
        return role

    def update(self, instance: Role, validated_data: dict) -> Role:
        permissions = validated_data.pop('permissions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance


class RoleBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'code']


class UserSerializer(serializers.ModelSerializer):
    roles = RoleBriefSerializer(many=True, read_only=True)
    real_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'real_name', 'email',
            'phone', 'department', 'title', 'avatar',
            'is_active', 'roles', 'date_joined', 'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_real_name(self, obj: User) -> str:
        full = (obj.get_full_name() or '').strip()
        if full:
            return full
        return (obj.first_name or '').strip()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Role.objects.all(), required=False,
        source='roles',
    )
    real_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name', 'real_name',
            'email', 'phone', 'department', 'title', 'is_active', 'role_ids',
        ]

    def create(self, validated_data: dict) -> User:
        roles = validated_data.pop('roles', [])
        real_name = validated_data.pop('real_name', None)
        password = validated_data.pop('password')
        if real_name is not None:
            validated_data['first_name'] = str(real_name).strip()
            validated_data['last_name'] = ''
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if roles:
            user.roles.set(roles)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Role.objects.all(), required=False,
        source='roles',
    )
    real_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'real_name', 'email', 'phone',
            'department', 'title', 'avatar', 'is_active', 'role_ids',
        ]

    def update(self, instance: User, validated_data: dict) -> User:
        roles = validated_data.pop('roles', None)
        real_name = validated_data.pop('real_name', serializers.empty)
        if real_name is not serializers.empty:
            instance.first_name = str(real_name or '').strip()
            instance.last_name = ''
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if roles is not None:
            instance.roles.set(roles)
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, label='旧密码')
    new_password = serializers.CharField(
        required=True, validators=[validate_password], label='新密码',
    )

    def validate_old_password(self, value: str) -> str:
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('旧密码不正确')
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError('新密码不能与旧密码相同')
        return attrs


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'username', 'method', 'path',
            'body', 'ip_address', 'status_code', 'timestamp',
        ]
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label='用户名')
    password = serializers.CharField(label='密码')


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField(label='访问令牌')
    refresh = serializers.CharField(label='刷新令牌')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'content', 'link_path', 'is_read', 'read_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'read_at']
