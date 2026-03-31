from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import BaseModel


class User(AbstractUser):
    # 与 JWT claim `sv` 对齐；登录或管理员踢出时 +1，使旧 access/refresh 失效
    session_version = models.PositiveIntegerField(default=0, verbose_name='会话版本')
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

    def has_lims_permission(self, module: str, action: str) -> bool:
        """与 Permission 表（module + action）对齐的权限判断。"""
        from . import services

        return services.has_permission(self, module, action)


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
    idempotency_key = models.CharField(
        max_length=128, blank=True, verbose_name='幂等键',
    )
    is_idempotent_replay = models.BooleanField(
        default=False, verbose_name='是否重放返回',
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = verbose_name
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp'], name='idx_auditlog_timestamp'),
            models.Index(fields=['user'], name='idx_auditlog_user'),
            models.Index(fields=['idempotency_key'], name='idx_auditlog_idemp'),
        ]

    def __str__(self) -> str:
        return f'{self.username} {self.method} {self.path}'

    def get_is_idempotent_replay_display(self) -> str:
        return '是' if self.is_idempotent_replay else '否'


class Notification(BaseModel):
    TYPES = [
        ('commission_review', '委托待评审'),
        ('equipment_expiring', '设备即将到检'),
        ('sample_overdue', '样品超期'),
        ('task_assigned', '任务已分配'),
        ('record_review', '记录待复核'),
        ('report_audit', '报告待审核'),
        ('report_approve', '报告待批准'),
        ('quality_audit', '质量审核'),
        ('system', '系统通知'),
    ]
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收人')
    notification_type = models.CharField(max_length=50, choices=TYPES, verbose_name='类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(blank=True, verbose_name='内容')
    link_path = models.CharField(max_length=200, blank=True, verbose_name='跳转路径')
    is_read = models.BooleanField(default=False, verbose_name='已读')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='阅读时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '通知'


class IdempotencyRecord(models.Model):
    STATE_CHOICES = [
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='idempotency_records',
        verbose_name='请求用户',
    )
    key = models.CharField(max_length=128, verbose_name='幂等键')
    method = models.CharField(max_length=10, verbose_name='请求方法')
    path = models.CharField(max_length=500, verbose_name='请求路径')
    request_hash = models.CharField(max_length=64, verbose_name='请求摘要')
    state = models.CharField(
        max_length=20, choices=STATE_CHOICES, default='processing', verbose_name='状态',
    )
    response_status = models.IntegerField(null=True, blank=True, verbose_name='响应状态码')
    response_body = models.TextField(blank=True, verbose_name='响应体')
    content_type = models.CharField(max_length=120, blank=True, verbose_name='响应类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '幂等请求记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'key', 'method', 'path'],
                name='uniq_idemp_user_key_method_path',
            ),
        ]
        indexes = [
            models.Index(fields=['key'], name='idx_idemp_key'),
            models.Index(fields=['state'], name='idx_idemp_state'),
            models.Index(fields=['-created_at'], name='idx_idemp_created'),
        ]
