from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer

from .models import (
    Authorization,
    Certificate,
    CompetencyEval,
    StaffProfile,
    Training,
)

from apps.system.models import User


class CertificateSerializer(BaseModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            'id', 'staff', 'cert_type', 'cert_no',
            'issuing_authority', 'issue_date', 'expiry_date',
            'attachment', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuthorizationSerializer(BaseModelSerializer):
    test_category_name = serializers.CharField(
        source='test_category.name', read_only=True,
    )

    class Meta:
        model = Authorization
        fields = [
            'id', 'staff', 'test_category', 'test_category_name',
            'test_methods', 'authorized_date', 'authorized_by',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrainingSerializer(BaseModelSerializer):
    assessment_result_display = serializers.CharField(
        source='get_assessment_result_display', read_only=True,
    )

    class Meta:
        model = Training
        fields = [
            'id', 'staff', 'title', 'training_date', 'hours',
            'trainer', 'assessment_result', 'assessment_result_display',
            'attachment', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompetencyEvalSerializer(BaseModelSerializer):
    conclusion_display = serializers.CharField(
        source='get_conclusion_display', read_only=True,
    )
    evaluator_name = serializers.SerializerMethodField()

    class Meta:
        model = CompetencyEval
        fields = [
            'id', 'staff', 'eval_date', 'eval_type', 'score',
            'conclusion', 'conclusion_display', 'evaluator',
            'evaluator_name', 'comment', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_evaluator_name(self, obj: CompetencyEval) -> str:
        if obj.evaluator:
            return obj.evaluator.get_full_name() or str(obj.evaluator)
        return ''


class StaffProfileListSerializer(BaseModelSerializer):
    user_name = serializers.SerializerMethodField()
    # 为前端兼容：人员管理列表/详情页面使用 staff_no/name/title 字段命名
    staff_no = serializers.CharField(source='employee_no', read_only=True)
    name = serializers.SerializerMethodField()
    title = serializers.CharField(source='user.title', read_only=True)
    department = serializers.CharField(
        source='user.department', read_only=True,
    )
    education_display = serializers.CharField(
        source='get_education_display', read_only=True,
    )

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'user_name', 'employee_no',
            'staff_no', 'name', 'title',
            'education', 'education_display', 'major',
            'department', 'hire_date', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_user_name(self, obj: StaffProfile) -> str:
        return obj.user.get_full_name() or obj.user.username

    def get_name(self, obj: StaffProfile) -> str:
        # 与 user_name 同语义
        return self.get_user_name(obj)


class StaffProfileDetailSerializer(BaseModelSerializer):
    user_name = serializers.SerializerMethodField()
    staff_no = serializers.CharField(source='employee_no', read_only=True)
    name = serializers.SerializerMethodField()
    title = serializers.CharField(source='user.title', read_only=True)
    department = serializers.CharField(
        source='user.department', read_only=True,
    )
    education_display = serializers.CharField(
        source='get_education_display', read_only=True,
    )
    certificates = CertificateSerializer(many=True, read_only=True)
    authorizations = AuthorizationSerializer(many=True, read_only=True)
    trainings = TrainingSerializer(many=True, read_only=True)
    evaluations = CompetencyEvalSerializer(many=True, read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'user_name', 'employee_no',
            'staff_no', 'name', 'title',
            'education', 'education_display', 'major',
            'department', 'hire_date', 'signature_image',
            'certificates', 'authorizations', 'trainings',
            'evaluations', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_name(self, obj: StaffProfile) -> str:
        return obj.user.get_full_name() or obj.user.username

    def get_name(self, obj: StaffProfile) -> str:
        return self.get_user_name(obj)


class StaffProfileCreateSerializer(serializers.Serializer):
    """
    兼容前端当前“新增人员”表单字段（staff_no/name/department/title/education/phone/email/entry_date 等）。
    后端真正的数据结构是 User + StaffProfile，这里做自动映射与创建。
    """

    # 前端会带上 id，这里允许忽略
    id = serializers.IntegerField(required=False)

    # 可选：绑定已有系统用户（user 管理模块）
    user_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True,
    )

    # 这些字段只用于写入/创建；响应里不需要序列化到 StaffProfile 实例上
    staff_no = serializers.CharField(required=True, write_only=True)
    name = serializers.CharField(required=True, write_only=True)
    gender = serializers.CharField(required=False, allow_blank=True, write_only=True)
    department = serializers.CharField(required=False, allow_blank=True, write_only=True)
    title = serializers.CharField(required=False, allow_blank=True, write_only=True)
    education = serializers.CharField(required=False, allow_blank=True, write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True, write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, write_only=True)
    entry_date = serializers.DateField(required=False, allow_null=True, write_only=True)

    def create(self, validated_data: dict) -> StaffProfile:
        staff_no = validated_data['staff_no'].strip()
        full_name = validated_data['name'].strip()

        bound_user_id = validated_data.get('user_id')
        if bound_user_id:
            user = User.objects.get(pk=bound_user_id)
            # 强约束：绑定模式下，工号应与用户 username 一致，避免后续难以对齐权限/账号。
            if user.username != staff_no:
                raise serializers.ValidationError({
                    'staff_no': '该系统用户的用户名与工号不一致，请先在用户管理中调整或选择正确用户。',
                })
        else:
            # 默认密码：仅用于演示/可登录；生产环境建议改为可配置或让用户先设定密码
            default_password = 'Limis@123456'
            user, _created = User.objects.get_or_create(
                username=staff_no,
                defaults={
                    'first_name': full_name,
                    'last_name': '',
                    'department': validated_data.get('department', ''),
                    'title': validated_data.get('title', ''),
                    'phone': validated_data.get('phone', ''),
                    'email': validated_data.get('email', ''),
                    'is_active': True,
                },
            )
            # 若已存在则也同步一份基础信息（演示用）
            user.first_name = full_name
            user.department = validated_data.get('department', '') or user.department
            user.title = validated_data.get('title', '') or user.title
            user.phone = validated_data.get('phone', '') or user.phone
            user.email = validated_data.get('email', '') or user.email
            user.set_password(default_password)

        # 绑定/非绑定：都同步更新展示字段
        if not bound_user_id:
            # 非绑定模式：上面已 set_password 并 save
            user.save()
        else:
            user.first_name = full_name
            user.department = validated_data.get('department', '') or user.department
            user.title = validated_data.get('title', '') or user.title
            user.phone = validated_data.get('phone', '') or user.phone
            user.email = validated_data.get('email', '') or user.email
            user.save()

        profile, _ = StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'employee_no': staff_no,
                'education': validated_data.get('education', ''),
                'hire_date': validated_data.get('entry_date', None),
                'major': '',
            },
        )
        profile.employee_no = staff_no
        profile.education = validated_data.get('education', '') or profile.education
        profile.hire_date = validated_data.get('entry_date', None)
        profile.save()
        return profile

    def update(self, instance: StaffProfile, validated_data: dict) -> StaffProfile:
        """
        兼容前端“编辑人员”PUT：同一套字段映射到 User + StaffProfile。
        """
        staff_no = validated_data['staff_no'].strip()
        full_name = validated_data['name'].strip()

        bound_user_id = validated_data.get('user_id')
        user = instance.user

        if bound_user_id:
            if bound_user_id != instance.user_id:
                user = User.objects.get(pk=bound_user_id)
                if user.username != staff_no:
                    raise serializers.ValidationError({
                        'staff_no': '该系统用户的用户名与工号不一致，请选择正确用户。',
                    })
                instance.user = user
            # 绑定模式下：不改 username，只同步 first_name/部门/电话等字段
            user.first_name = full_name
            user.department = validated_data.get('department', '') or user.department
            user.title = validated_data.get('title', '') or user.title
            user.phone = validated_data.get('phone', '') or user.phone
            user.email = validated_data.get('email', '') or user.email
            user.save()
        else:
            # 非绑定模式：兼容旧逻辑：staff_no 变更会同步到 user.username
            user.username = staff_no
            user.first_name = full_name
            user.department = validated_data.get('department', '') or user.department
            user.title = validated_data.get('title', '') or user.title
            user.phone = validated_data.get('phone', '') or user.phone
            user.email = validated_data.get('email', '') or user.email
            user.save()

        instance.employee_no = staff_no
        instance.education = validated_data.get('education', '') or instance.education
        instance.hire_date = validated_data.get('entry_date', None)
        instance.save()
        return instance
