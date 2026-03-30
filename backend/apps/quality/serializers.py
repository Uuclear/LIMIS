from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer

from .models import (
    AuditFinding,
    Complaint,
    CorrectiveAction,
    InternalAudit,
    ManagementReview,
    NonConformity,
    ProficiencyTest,
    QualitySupervision,
    ReviewDecision,
)


# ───────────────────── Audit ─────────────────────


class CorrectiveActionSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    responsible_person_name = serializers.SerializerMethodField()

    class Meta:
        model = CorrectiveAction
        fields = [
            'id', 'finding', 'root_cause', 'action_plan',
            'responsible_person', 'responsible_person_name',
            'deadline', 'status', 'status_display',
            'completion_date', 'verification_result',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_responsible_person_name(self, obj: CorrectiveAction) -> str:
        if obj.responsible_person:
            return obj.responsible_person.get_full_name() or str(obj.responsible_person)
        return ''


class AuditFindingSerializer(BaseModelSerializer):
    finding_type_display = serializers.CharField(
        source='get_finding_type_display', read_only=True,
    )
    actions = CorrectiveActionSerializer(many=True, read_only=True)

    class Meta:
        model = AuditFinding
        fields = [
            'id', 'audit', 'finding_type', 'finding_type_display',
            'clause', 'description', 'department',
            'actions', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InternalAuditListSerializer(BaseModelSerializer):
    audit_type_display = serializers.CharField(
        source='get_audit_type_display', read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    lead_auditor_name = serializers.SerializerMethodField()

    class Meta:
        model = InternalAudit
        fields = [
            'id', 'audit_no', 'title', 'audit_type',
            'audit_type_display', 'planned_date', 'actual_date',
            'lead_auditor', 'lead_auditor_name',
            'status', 'status_display', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'audit_no': {'required': False, 'allow_blank': True},
        }

    def get_lead_auditor_name(self, obj: InternalAudit) -> str:
        if obj.lead_auditor:
            return obj.lead_auditor.get_full_name() or str(obj.lead_auditor)
        return ''


class InternalAuditDetailSerializer(InternalAuditListSerializer):
    findings = AuditFindingSerializer(many=True, read_only=True)

    class Meta(InternalAuditListSerializer.Meta):
        fields = InternalAuditListSerializer.Meta.fields + [
            'scope', 'findings', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ───────────────────── Review ─────────────────────


class ReviewDecisionSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    responsible_person_name = serializers.SerializerMethodField()

    class Meta:
        model = ReviewDecision
        fields = [
            'id', 'review', 'content', 'responsible_person',
            'responsible_person_name', 'deadline',
            'status', 'status_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_responsible_person_name(self, obj: ReviewDecision) -> str:
        if obj.responsible_person:
            return obj.responsible_person.get_full_name() or str(obj.responsible_person)
        return ''


class ManagementReviewListSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    chairperson_name = serializers.SerializerMethodField()

    class Meta:
        model = ManagementReview
        fields = [
            'id', 'review_no', 'title', 'review_date',
            'chairperson', 'chairperson_name',
            'status', 'status_display', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'review_no': {'required': False, 'allow_blank': True},
        }

    def get_chairperson_name(self, obj: ManagementReview) -> str:
        if obj.chairperson:
            return obj.chairperson.get_full_name() or str(obj.chairperson)
        return ''


class ManagementReviewDetailSerializer(ManagementReviewListSerializer):
    decisions = ReviewDecisionSerializer(many=True, read_only=True)

    class Meta(ManagementReviewListSerializer.Meta):
        fields = ManagementReviewListSerializer.Meta.fields + [
            'participants', 'input_materials', 'minutes',
            'decisions', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ───────────────────── NonConformity ─────────────────────


class NonConformitySerializer(BaseModelSerializer):
    source_display = serializers.CharField(
        source='get_source_display', read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    responsible_person_name = serializers.SerializerMethodField()

    class Meta:
        model = NonConformity
        fields = [
            'id', 'nc_no', 'source', 'source_display',
            'description', 'impact_assessment', 'corrective_action',
            'responsible_person', 'responsible_person_name',
            'status', 'status_display', 'close_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_responsible_person_name(self, obj: NonConformity) -> str:
        if obj.responsible_person:
            return obj.responsible_person.get_full_name() or str(obj.responsible_person)
        return ''


class ComplaintSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    handler_name = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            'id', 'complaint_no', 'complainant', 'complaint_date',
            'content', 'investigation', 'handling_result',
            'handler', 'handler_name',
            'status', 'status_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_handler_name(self, obj: Complaint) -> str:
        if obj.handler:
            return obj.handler.get_full_name() or str(obj.handler)
        return ''


# ───────────────────── Proficiency ─────────────────────


class ProficiencyTestSerializer(BaseModelSerializer):
    result_display = serializers.CharField(
        source='get_result_display', read_only=True,
    )

    class Meta:
        model = ProficiencyTest
        fields = [
            'id', 'name', 'organizer', 'test_item',
            'participation_date', 'result', 'result_display',
            'report', 'attachment', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QualitySupervisionSerializer(BaseModelSerializer):
    conclusion_display = serializers.CharField(
        source='get_conclusion_display', read_only=True,
    )
    supervisor_name = serializers.SerializerMethodField()

    class Meta:
        model = QualitySupervision
        fields = [
            'id', 'plan_no', 'supervisor', 'supervisor_name',
            'supervision_date', 'scope', 'findings',
            'conclusion', 'conclusion_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_supervisor_name(self, obj: QualitySupervision) -> str:
        if obj.supervisor:
            return obj.supervisor.get_full_name() or str(obj.supervisor)
        return ''
