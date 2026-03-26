from django.contrib import admin

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


class AuditFindingInline(admin.TabularInline):
    model = AuditFinding
    extra = 0


@admin.register(InternalAudit)
class InternalAuditAdmin(admin.ModelAdmin):
    list_display = [
        'audit_no', 'title', 'audit_type',
        'planned_date', 'status',
    ]
    list_filter = ['audit_type', 'status']
    search_fields = ['audit_no', 'title']
    raw_id_fields = ['lead_auditor']
    inlines = [AuditFindingInline]


@admin.register(AuditFinding)
class AuditFindingAdmin(admin.ModelAdmin):
    list_display = ['audit', 'finding_type', 'clause', 'department']
    list_filter = ['finding_type']
    raw_id_fields = ['audit']


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = [
        'finding', 'responsible_person',
        'deadline', 'status',
    ]
    list_filter = ['status']
    raw_id_fields = ['finding', 'responsible_person']


# ───────────────────── Review ─────────────────────


class ReviewDecisionInline(admin.TabularInline):
    model = ReviewDecision
    extra = 0


@admin.register(ManagementReview)
class ManagementReviewAdmin(admin.ModelAdmin):
    list_display = [
        'review_no', 'title', 'review_date',
        'chairperson', 'status',
    ]
    list_filter = ['status']
    search_fields = ['review_no', 'title']
    raw_id_fields = ['chairperson']
    inlines = [ReviewDecisionInline]


@admin.register(ReviewDecision)
class ReviewDecisionAdmin(admin.ModelAdmin):
    list_display = ['review', 'deadline', 'status']
    list_filter = ['status']
    raw_id_fields = ['review', 'responsible_person']


# ───────────────────── NonConformity ─────────────────────


@admin.register(NonConformity)
class NonConformityAdmin(admin.ModelAdmin):
    list_display = ['nc_no', 'source', 'status', 'close_date']
    list_filter = ['source', 'status']
    search_fields = ['nc_no', 'description']
    raw_id_fields = ['responsible_person']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = [
        'complaint_no', 'complainant',
        'complaint_date', 'status',
    ]
    list_filter = ['status']
    search_fields = ['complaint_no', 'complainant']
    raw_id_fields = ['handler']


# ───────────────────── Proficiency ─────────────────────


@admin.register(ProficiencyTest)
class ProficiencyTestAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'organizer', 'test_item',
        'participation_date', 'result',
    ]
    list_filter = ['result']
    search_fields = ['name', 'test_item']


@admin.register(QualitySupervision)
class QualitySupervisionAdmin(admin.ModelAdmin):
    list_display = [
        'plan_no', 'supervisor', 'supervision_date', 'conclusion',
    ]
    list_filter = ['conclusion']
    search_fields = ['plan_no']
    raw_id_fields = ['supervisor']
