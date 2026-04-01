from django.conf import settings
from django.db import models

from core.models import BaseModel


class StaffProfile(BaseModel):
    EDUCATION_CHOICES = [
        ('high_school', '高中/中专'),
        ('college', '大专'),
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('doctor', '博士'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户',
    )
    employee_no = models.CharField(
        max_length=50, unique=True, verbose_name='工号',
    )
    education = models.CharField(
        max_length=20, choices=EDUCATION_CHOICES,
        blank=True, verbose_name='学历',
    )
    major = models.CharField(max_length=100, blank=True, verbose_name='专业')
    hire_date = models.DateField(
        null=True, blank=True, verbose_name='入职日期',
    )
    signature_image = models.ImageField(
        upload_to='signatures/staff/', blank=True, null=True,
        verbose_name='签名样本',
    )

    class Meta:
        verbose_name = '人员档案'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.employee_no} - {self.user.get_full_name() or self.user.username}'


class Certificate(BaseModel):
    staff = models.ForeignKey(
        StaffProfile, on_delete=models.CASCADE,
        related_name='certificates', verbose_name='人员',
    )
    cert_type = models.CharField(max_length=100, verbose_name='证书类型')
    cert_no = models.CharField(max_length=100, verbose_name='证书编号')
    issuing_authority = models.CharField(
        max_length=200, verbose_name='发证机关',
    )
    issue_date = models.DateField(verbose_name='发证日期')
    expiry_date = models.DateField(
        null=True, blank=True, verbose_name='有效期至',
    )
    attachment = models.FileField(
        upload_to='certificates/', blank=True, null=True,
        verbose_name='证书附件',
    )

    class Meta:
        verbose_name = '证书'
        verbose_name_plural = verbose_name
        ordering = ['-issue_date']

    def __str__(self) -> str:
        return f'{self.cert_type} - {self.cert_no}'


class Authorization(BaseModel):
    staff = models.ForeignKey(
        StaffProfile, on_delete=models.CASCADE,
        related_name='authorizations', verbose_name='人员',
    )
    test_category = models.ForeignKey(
        'testing.TestCategory', on_delete=models.CASCADE,
        verbose_name='授权检测类别',
    )
    parameters = models.ManyToManyField(
        'testing.TestParameter', blank=True, verbose_name='授权检测参数',
    )
    authorized_date = models.DateField(verbose_name='授权日期')
    authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='授权人',
    )
    is_active = models.BooleanField(default=True, verbose_name='是否有效')

    class Meta:
        verbose_name = '人员授权'
        verbose_name_plural = verbose_name
        ordering = ['-authorized_date']

    def __str__(self) -> str:
        return f'{self.staff} - {self.test_category}'


class Training(BaseModel):
    ASSESSMENT_CHOICES = [
        ('pass', '合格'),
        ('fail', '不合格'),
        ('na', '未考核'),
    ]

    staff = models.ForeignKey(
        StaffProfile, on_delete=models.CASCADE,
        related_name='trainings', verbose_name='人员',
    )
    title = models.CharField(max_length=200, verbose_name='培训内容')
    training_date = models.DateField(verbose_name='培训日期')
    hours = models.DecimalField(
        max_digits=5, decimal_places=1,
        null=True, blank=True, verbose_name='培训学时',
    )
    trainer = models.CharField(
        max_length=100, blank=True, verbose_name='培训讲师',
    )
    assessment_result = models.CharField(
        max_length=10, choices=ASSESSMENT_CHOICES,
        default='na', verbose_name='考核结果',
    )
    attachment = models.FileField(
        upload_to='trainings/', blank=True, null=True,
        verbose_name='培训记录附件',
    )

    class Meta:
        verbose_name = '培训记录'
        verbose_name_plural = verbose_name
        ordering = ['-training_date']

    def __str__(self) -> str:
        return f'{self.staff} - {self.title}'


class CompetencyEval(BaseModel):
    CONCLUSION_CHOICES = [
        ('competent', '胜任'),
        ('need_training', '需培训'),
        ('incompetent', '不胜任'),
    ]

    staff = models.ForeignKey(
        StaffProfile, on_delete=models.CASCADE,
        related_name='evaluations', verbose_name='人员',
    )
    eval_date = models.DateField(verbose_name='评价日期')
    eval_type = models.CharField(max_length=100, verbose_name='评价类型')
    score = models.DecimalField(
        max_digits=5, decimal_places=1,
        null=True, blank=True, verbose_name='评分',
    )
    conclusion = models.CharField(
        max_length=20, choices=CONCLUSION_CHOICES,
        verbose_name='结论',
    )
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='评价人',
    )
    comment = models.TextField(blank=True, verbose_name='评价意见')

    class Meta:
        verbose_name = '能力评价'
        verbose_name_plural = verbose_name
        ordering = ['-eval_date']

    def __str__(self) -> str:
        return f'{self.staff} - {self.eval_type} ({self.eval_date})'
