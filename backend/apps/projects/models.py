from django.db import models

from core.models import BaseModel


class Project(BaseModel):
    PROJECT_TYPE_CHOICES = [
        ('building', '房建工程'),
        ('municipal', '市政工程'),
        ('transport', '交通工程'),
        ('water', '水利工程'),
        ('airport', '机场工程'),
        ('other', '其他'),
    ]
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('completed', '已竣工'),
        ('suspended', '已暂停'),
    ]

    name = models.CharField(max_length=200, verbose_name='工程名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='项目编号')
    address = models.CharField(max_length=500, blank=True, verbose_name='工程地点')
    project_type = models.CharField(
        max_length=20, choices=PROJECT_TYPE_CHOICES, verbose_name='工程类型',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='项目状态',
    )
    start_date = models.DateField(null=True, blank=True, verbose_name='开工日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='计划竣工日期')
    description = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '工程项目'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name


class Organization(BaseModel):
    ROLE_CHOICES = [
        ('builder', '建设单位'),
        ('contractor', '施工单位'),
        ('supervisor', '监理单位'),
        ('designer', '设计单位'),
        ('inspector', '检测单位'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='organizations', verbose_name='所属项目',
    )
    name = models.CharField(max_length=200, verbose_name='单位名称')
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, verbose_name='单位角色',
    )
    contact_person = models.CharField(max_length=50, blank=True, verbose_name='联系人')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')

    class Meta:
        verbose_name = '参建单位'
        verbose_name_plural = verbose_name
        unique_together = ('project', 'name', 'role')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name} ({self.get_role_display()})'


class SubProject(BaseModel):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='sub_projects', verbose_name='所属项目',
    )
    name = models.CharField(max_length=200, verbose_name='分部分项工程名称')
    code = models.CharField(max_length=50, blank=True, verbose_name='编号')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,
        related_name='children', verbose_name='上级工程',
    )
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = '分部分项工程'
        verbose_name_plural = verbose_name
        ordering = ['code', '-created_at']

    def __str__(self) -> str:
        return self.name


class Contract(BaseModel):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='contracts', verbose_name='所属项目',
    )
    contract_no = models.CharField(max_length=100, unique=True, verbose_name='合同编号')
    title = models.CharField(max_length=200, verbose_name='合同名称')
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='合同金额',
    )
    sign_date = models.DateField(null=True, blank=True, verbose_name='签订日期')
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    scope = models.TextField(blank=True, verbose_name='检测范围')
    attachment = models.FileField(
        upload_to='contracts/', blank=True, null=True, verbose_name='合同附件',
    )

    class Meta:
        verbose_name = '合同'
        verbose_name_plural = verbose_name
        ordering = ['-sign_date', '-created_at']

    def __str__(self) -> str:
        return self.title


class Witness(BaseModel):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='witnesses', verbose_name='所属项目',
    )
    name = models.CharField(max_length=50, verbose_name='见证人姓名')
    id_number = models.CharField(max_length=50, blank=True, verbose_name='证件号')
    organization = models.ForeignKey(
        Organization, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='所属单位',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    certificate_no = models.CharField(max_length=100, blank=True, verbose_name='见证员证书号')
    is_active = models.BooleanField(default=True, verbose_name='是否在岗')

    class Meta:
        verbose_name = '见证人'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name
