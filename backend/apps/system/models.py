from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    department = models.CharField(max_length=100, blank=True, verbose_name='部门')
    title = models.CharField(max_length=100, blank=True, verbose_name='职称')
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name='头像',
    )
    # 电子签名
    signature = models.ImageField(
        upload_to='signatures/', blank=True, null=True, verbose_name='电子签名',
    )
    signature_updated_at = models.DateTimeField(
        null=True, blank=True, verbose_name='签名更新时间',
    )
    # 资质证书
    certificate_no = models.CharField(
        max_length=100, blank=True, verbose_name='资质证书编号',
    )
    certificate_expiry = models.DateField(
        null=True, blank=True, verbose_name='证书有效期',
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
    
    def has_valid_signature(self) -> bool:
        """检查用户是否有有效的电子签名"""
        return bool(self.signature and self.signature.name)
    
    def is_certificate_valid(self) -> bool:
        """检查资质证书是否有效"""
        if not self.certificate_expiry:
            return True  # 无有效期视为永久有效
        return self.certificate_expiry >= timezone.now().date()
    
    def can_sign_report(self) -> bool:
        """检查用户是否可以签署报告"""
        # 需要有有效签名
        if not self.has_valid_signature():
            return False
        # 需要有授权签字人角色
        if hasattr(self, 'roles'):
            role_codes = self.roles.values_list('code', flat=True)
            if 'auth_signer' in role_codes or 'admin' in role_codes:
                return True
        return self.is_superuser


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
