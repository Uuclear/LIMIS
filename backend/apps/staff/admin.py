from django.contrib import admin

from .models import (
    Authorization,
    Certificate,
    CompetencyEval,
    StaffProfile,
    Training,
)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_no', 'user', 'education', 'major', 'hire_date']
    list_filter = ['education']
    search_fields = ['employee_no', 'user__username', 'user__first_name']
    raw_id_fields = ['user']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'cert_type', 'cert_no',
        'issue_date', 'expiry_date',
    ]
    list_filter = ['cert_type']
    search_fields = ['cert_no', 'cert_type']
    raw_id_fields = ['staff']


@admin.register(Authorization)
class AuthorizationAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'test_category', 'authorized_date',
        'authorized_by', 'is_active',
    ]
    list_filter = ['is_active']
    raw_id_fields = ['staff', 'authorized_by']
    filter_horizontal = ['test_methods']


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'title', 'training_date',
        'hours', 'assessment_result',
    ]
    list_filter = ['assessment_result']
    search_fields = ['title', 'trainer']
    raw_id_fields = ['staff']


@admin.register(CompetencyEval)
class CompetencyEvalAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'eval_type', 'eval_date',
        'score', 'conclusion',
    ]
    list_filter = ['conclusion', 'eval_type']
    raw_id_fields = ['staff', 'evaluator']
