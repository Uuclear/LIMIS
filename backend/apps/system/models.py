from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import BaseModel


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    department = models.CharField(max_length=100, blank=True, verbose_name='部门')
    title = models.CharField(max_length=100, blank=True, verbose_name='职称')
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name='头像',
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    roles = models.ManyToManyField(
        'Role', blank=True, related_name='users', verbose_name='角色',
    )

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-date_joined']

    def __str__(self) -> str:
        return self.get_full_name() or self.username


class Role(BaseModel):
    ADMIN = 'admin'
    TECH_DIRECTOR = 'tech_director'
    QUALITY_DIRECTOR = 'quality_director'
    AUTH_SIGNER = 'auth_signer'
    REVIEWER = 'reviewer'
    SUPERVISOR = 'supervisor'
    TESTER = 'tester'
    SAMPLE_CLERK = 'sample_clerk'
    EQUIP_MANAGER = 'equip_manager'
    RECEPTION = 'reception'
    CLIENT = 'client'

    ROLE_CHOICES = [
        (ADMIN, '系统管理员'),
        (TECH_DIRECTOR, '技术负责人'),
        (QUALITY_DIRECTOR, '质量负责人'),
        (AUTH_SIGNER, '授权签字人'),
        (REVIEWER, '审核人'),
        (SUPERVISOR, '监督员'),
        (TESTER, '检测人员'),
        (SAMPLE_CLERK, '样品管理员'),
        (EQUIP_MANAGER, '设备管理员'),
        (RECEPTION, '接待员'),
        (CLIENT, '委托方'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='角色名称')
    code = models.CharField(
        max_length=50, unique=True, choices=ROLE_CHOICES, verbose_name='角色编码',
    )
    description = models.TextField(blank=True, verbose_name='描述')
    permissions = models.ManyToManyField(
        'Permission', blank=True, related_name='roles', verbose_name='权限',
    )

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self) -> str:
        return self.name


class Permission(BaseModel):
    ACTION_CHOICES = [
        ('view', '查看'),
        ('create', '创建'),
        ('edit', '编辑'),
        ('delete', '删除'),
        ('approve', '审批'),
        ('export', '导出'),
    ]

    name = models.CharField(max_length=100, verbose_name='权限名称')
    code = models.CharField(max_length=100, unique=True, verbose_name='权限编码')
    module = models.CharField(max_length=50, verbose_name='所属模块')
    action = models.CharField(
        max_length=50, choices=ACTION_CHOICES, verbose_name='操作类型',
    )

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = verbose_name
        unique_together = ('module', 'action')
        ordering = ['module', 'action']

    def __str__(self) -> str:
        return f'{self.module}:{self.action}'


class AuditLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='操作用户',
        related_name='audit_logs',
    )
    username = models.CharField(max_length=150, verbose_name='用户名')
    method = models.CharField(max_length=10, verbose_name='请求方法')
    path = models.CharField(max_length=500, verbose_name='请求路径')
    body = models.TextField(blank=True, verbose_name='请求体')
    ip_address = models.GenericIPAddressField(null=True, verbose_name='IP地址')
    status_code = models.IntegerField(null=True, verbose_name='状态码')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = verbose_name
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp'], name='idx_auditlog_timestamp'),
            models.Index(fields=['user'], name='idx_auditlog_user'),
        ]

    def __str__(self) -> str:
        return f'{self.username} {self.method} {self.path}'
