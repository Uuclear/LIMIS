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
    has_signature = serializers.SerializerMethodField()
    signature_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'real_name', 'email',
            'phone', 'department', 'title', 'avatar',
            'signature', 'signature_url', 'has_signature', 'signature_updated_at',
            'certificate_no', 'certificate_expiry',
            'is_active', 'roles', 'date_joined', 'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'signature_updated_at']

    def get_real_name(self, obj: User) -> str:
        full = (obj.get_full_name() or '').strip()
        if full:
            return full
        return (obj.first_name or '').strip()
    
    def get_has_signature(self, obj: User) -> bool:
        return obj.has_valid_signature()
    
    def get_signature_url(self, obj: User) -> str | None:
        if obj.signature and obj.signature.name:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.signature.url)
            return obj.signature.url
        return None


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
            'certificate_no', 'certificate_expiry',
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


class SignatureUploadSerializer(serializers.Serializer):
    """签名上传序列化器"""
    signature = serializers.ImageField(required=True)
    
    def validate_signature(self, value):
        """验证签名文件"""
        # 检查文件大小（最大2MB）
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('签名文件大小不能超过2MB')
        
        # 检查文件类型
        allowed_types = ['image/png', 'image/jpeg', 'image/jpg']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError('签名文件格式仅支持PNG/JPG')
        
        return value


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
