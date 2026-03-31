from __future__ import annotations

from django.utils import timezone

from core.views import BaseModelViewSet

from .filters import (
    ComplaintFilter,
    InternalAuditFilter,
    ManagementReviewFilter,
    NonConformityFilter,
    ProficiencyTestFilter,
    QualitySupervisionFilter,
)
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
    QualificationProfile,
)
from .serializers import (
    AuditFindingSerializer,
    ComplaintSerializer,
    CorrectiveActionSerializer,
    InternalAuditDetailSerializer,
    InternalAuditListSerializer,
    ManagementReviewDetailSerializer,
    ManagementReviewListSerializer,
    NonConformitySerializer,
    ProficiencyTestSerializer,
    QualitySupervisionSerializer,
    ReviewDecisionSerializer,
    QualificationProfileSerializer,
)


# ───────────────────── Audit ─────────────────────


class InternalAuditViewSet(BaseModelViewSet):
    queryset = InternalAudit.objects.select_related('lead_auditor').all()
    lims_module = 'quality'
    filterset_class = InternalAuditFilter
    search_fields = ['audit_no', 'title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InternalAuditDetailSerializer
        return InternalAuditListSerializer

    def perform_create(self, serializer):
        audit_no = (serializer.validated_data.get('audit_no') or '').strip()
        if not audit_no:
            audit_no = f"IA-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        serializer.save(audit_no=audit_no)


class AuditFindingViewSet(BaseModelViewSet):
    queryset = AuditFinding.objects.select_related('audit').all()
    serializer_class = AuditFindingSerializer
    lims_module = 'quality'
    filterset_fields = ['audit', 'finding_type', 'department']


class CorrectiveActionViewSet(BaseModelViewSet):
    queryset = CorrectiveAction.objects.select_related(
        'finding', 'responsible_person',
    ).all()
    serializer_class = CorrectiveActionSerializer
    lims_module = 'quality'
    filterset_fields = ['finding', 'status']


# ───────────────────── Review ─────────────────────


class ManagementReviewViewSet(BaseModelViewSet):
    queryset = ManagementReview.objects.select_related('chairperson').all()
    lims_module = 'quality'
    filterset_class = ManagementReviewFilter
    search_fields = ['review_no', 'title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ManagementReviewDetailSerializer
        return ManagementReviewListSerializer

    def perform_create(self, serializer):
        review_no = (serializer.validated_data.get('review_no') or '').strip()
        if not review_no:
            review_no = f"MR-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        serializer.save(review_no=review_no)


class ReviewDecisionViewSet(BaseModelViewSet):
    queryset = ReviewDecision.objects.select_related(
        'review', 'responsible_person',
    ).all()
    serializer_class = ReviewDecisionSerializer
    lims_module = 'quality'
    filterset_fields = ['review', 'status']


# ───────────────────── NonConformity ─────────────────────


class NonConformityViewSet(BaseModelViewSet):
    queryset = NonConformity.objects.select_related(
        'responsible_person',
    ).all()
    serializer_class = NonConformitySerializer
    lims_module = 'quality'
    filterset_class = NonConformityFilter
    search_fields = ['nc_no', 'description']


class ComplaintViewSet(BaseModelViewSet):
    queryset = Complaint.objects.select_related('handler').all()
    serializer_class = ComplaintSerializer
    lims_module = 'quality'
    filterset_class = ComplaintFilter
    search_fields = ['complaint_no', 'complainant', 'content']


# ───────────────────── Proficiency ─────────────────────


class ProficiencyTestViewSet(BaseModelViewSet):
    queryset = ProficiencyTest.objects.all()
    serializer_class = ProficiencyTestSerializer
    lims_module = 'quality'
    filterset_class = ProficiencyTestFilter
    search_fields = ['name', 'test_item', 'organizer']


class QualitySupervisionViewSet(BaseModelViewSet):
    queryset = QualitySupervision.objects.select_related('supervisor').all()
    serializer_class = QualitySupervisionSerializer
    lims_module = 'quality'
    filterset_class = QualitySupervisionFilter
    search_fields = ['plan_no']


# ───────────────────── Qualification ─────────────────────


class QualificationProfileViewSet(BaseModelViewSet):
    queryset = QualificationProfile.objects.all()
    serializer_class = QualificationProfileSerializer
    lims_module = 'quality'
    search_fields = ['name']
    filterset_fields = ['is_active']
