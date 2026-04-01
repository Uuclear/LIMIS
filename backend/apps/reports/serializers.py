from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer, safe_related_attr

from .models import Report, ReportApproval, ReportDistribution, ReportTemplate


class ReportTemplateSerializer(BaseModelSerializer):
    test_parameter_name = serializers.SerializerMethodField()

    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'code', 'report_type',
            'test_parameter', 'test_parameter_name',
            'version', 'schema', 'is_active',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def get_test_parameter_name(self, obj: ReportTemplate) -> str:
        p = safe_related_attr(obj, 'test_parameter')
        return getattr(p, 'name', '') if p else ''


class ReportApprovalSerializer(BaseModelSerializer):
    user_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ReportApproval
        fields = [
            'id', 'report', 'role', 'role_display', 'action', 'action_display',
            'user', 'user_name', 'comment', 'signature',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_user_name(self, obj: ReportApproval) -> str:
        if obj.user:
            return obj.user.get_full_name() or str(obj.user)
        return ''


class ReportDistributionSerializer(BaseModelSerializer):
    method_display = serializers.CharField(
        source='get_method_display', read_only=True,
    )

    class Meta:
        model = ReportDistribution
        fields = [
            'id', 'report', 'recipient', 'recipient_unit',
            'method', 'method_display', 'copies', 'distribution_date',
            'receiver_signature', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'report': {'required': False}}


class ReportListSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    commission_no = serializers.SerializerMethodField()
    compiler_name = serializers.SerializerMethodField()
    approval_summary = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'report_no', 'commission', 'commission_no',
            'report_type', 'status', 'status_display',
            'compiler', 'compiler_name', 'compile_date',
            'has_cma', 'issue_date', 'approval_summary',
            'created_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'report_no', 'created_at', 'created_by',
        ]

    def get_commission_no(self, obj: Report) -> str:
        c = safe_related_attr(obj, 'commission')
        return getattr(c, 'commission_no', '') if c else ''

    def get_compiler_name(self, obj: Report) -> str:
        if obj.compiler:
            return obj.compiler.get_full_name() or str(obj.compiler)
        return ''

    def get_approval_summary(self, obj: Report) -> dict:
        latest = {}
        for approval in obj.approvals.order_by('-created_at')[:3]:
            if approval.role not in latest:
                latest[approval.role] = {
                    'action': approval.action,
                    'user': str(approval.user) if approval.user else '',
                    'date': approval.created_at.isoformat() if approval.created_at else None,
                }
        return latest


class ReportDetailSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    commission_no = serializers.SerializerMethodField()
    compiler_name = serializers.SerializerMethodField()
    auditor_name = serializers.SerializerMethodField()
    approver_name = serializers.SerializerMethodField()
    approvals = ReportApprovalSerializer(many=True, read_only=True)
    distributions = ReportDistributionSerializer(many=True, read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'report_no', 'commission', 'commission_no',
            'report_type', 'template_name', 'status', 'status_display',
            'compiler', 'compiler_name', 'compile_date',
            'auditor', 'auditor_name', 'audit_date',
            'approver', 'approver_name', 'approve_date',
            'conclusion', 'pdf_file', 'qr_code', 'has_cma',
            'issue_date', 'remark',
            'approvals', 'distributions',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'report_no', 'status',
            'auditor', 'audit_date', 'approver', 'approve_date',
            'pdf_file', 'qr_code',
            'created_at', 'updated_at', 'created_by',
        ]

    def get_commission_no(self, obj: Report) -> str:
        c = safe_related_attr(obj, 'commission')
        return getattr(c, 'commission_no', '') if c else ''

    def get_compiler_name(self, obj: Report) -> str:
        if obj.compiler:
            return obj.compiler.get_full_name() or str(obj.compiler)
        return ''

    def get_auditor_name(self, obj: Report) -> str:
        if obj.auditor:
            return obj.auditor.get_full_name() or str(obj.auditor)
        return ''

    def get_approver_name(self, obj: Report) -> str:
        if obj.approver:
            return obj.approver.get_full_name() or str(obj.approver)
        return ''


class ReportCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Report
        fields = [
            'id', 'commission', 'report_type', 'template_name',
            'compiler', 'conclusion', 'has_cma', 'remark',
        ]
        read_only_fields = ['id']
