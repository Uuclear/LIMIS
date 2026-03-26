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
            'education', 'education_display', 'major',
            'department', 'hire_date', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_user_name(self, obj: StaffProfile) -> str:
        return obj.user.get_full_name() or obj.user.username


class StaffProfileDetailSerializer(BaseModelSerializer):
    user_name = serializers.SerializerMethodField()
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
            'education', 'education_display', 'major',
            'department', 'hire_date', 'signature_image',
            'certificates', 'authorizations', 'trainings',
            'evaluations', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_name(self, obj: StaffProfile) -> str:
        return obj.user.get_full_name() or obj.user.username
