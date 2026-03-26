from __future__ import annotations

from rest_framework import permissions

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
)


# ───────────────────── Audit ─────────────────────


class InternalAuditViewSet(BaseModelViewSet):
    queryset = InternalAudit.objects.select_related('lead_auditor').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = InternalAuditFilter
    search_fields = ['audit_no', 'title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InternalAuditDetailSerializer
        return InternalAuditListSerializer


class AuditFindingViewSet(BaseModelViewSet):
    queryset = AuditFinding.objects.select_related('audit').all()
    serializer_class = AuditFindingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['audit', 'finding_type', 'department']


class CorrectiveActionViewSet(BaseModelViewSet):
    queryset = CorrectiveAction.objects.select_related(
        'finding', 'responsible_person',
    ).all()
    serializer_class = CorrectiveActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['finding', 'status']


# ───────────────────── Review ─────────────────────


class ManagementReviewViewSet(BaseModelViewSet):
    queryset = ManagementReview.objects.select_related('chairperson').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ManagementReviewFilter
    search_fields = ['review_no', 'title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ManagementReviewDetailSerializer
        return ManagementReviewListSerializer


class ReviewDecisionViewSet(BaseModelViewSet):
    queryset = ReviewDecision.objects.select_related(
        'review', 'responsible_person',
    ).all()
    serializer_class = ReviewDecisionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['review', 'status']


# ───────────────────── NonConformity ─────────────────────


class NonConformityViewSet(BaseModelViewSet):
    queryset = NonConformity.objects.select_related(
        'responsible_person',
    ).all()
    serializer_class = NonConformitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = NonConformityFilter
    search_fields = ['nc_no', 'description']


class ComplaintViewSet(BaseModelViewSet):
    queryset = Complaint.objects.select_related('handler').all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ComplaintFilter
    search_fields = ['complaint_no', 'complainant', 'content']


# ───────────────────── Proficiency ─────────────────────


class ProficiencyTestViewSet(BaseModelViewSet):
    queryset = ProficiencyTest.objects.all()
    serializer_class = ProficiencyTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ProficiencyTestFilter
    search_fields = ['name', 'test_item', 'organizer']


class QualitySupervisionViewSet(BaseModelViewSet):
    queryset = QualitySupervision.objects.select_related('supervisor').all()
    serializer_class = QualitySupervisionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = QualitySupervisionFilter
    search_fields = ['plan_no']
