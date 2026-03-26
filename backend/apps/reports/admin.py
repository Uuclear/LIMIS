from django.contrib import admin

from .models import Report, ReportApproval, ReportDistribution


class ReportApprovalInline(admin.TabularInline):
    model = ReportApproval
    extra = 0
    readonly_fields = ['role', 'action', 'user', 'created_at']


class ReportDistributionInline(admin.TabularInline):
    model = ReportDistribution
    extra = 0


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_no', 'commission', 'report_type', 'status',
        'compiler', 'compile_date', 'has_cma', 'issue_date', 'created_at',
    ]
    list_filter = ['status', 'has_cma', 'report_type']
    search_fields = ['report_no', 'commission__commission_no']
    readonly_fields = ['report_no', 'qr_code', 'created_at', 'updated_at', 'created_by']
    inlines = [ReportApprovalInline, ReportDistributionInline]
    date_hierarchy = 'created_at'


@admin.register(ReportApproval)
class ReportApprovalAdmin(admin.ModelAdmin):
    list_display = ['report', 'role', 'action', 'user', 'created_at']
    list_filter = ['role', 'action']
    search_fields = ['report__report_no']
    readonly_fields = ['created_at']


@admin.register(ReportDistribution)
class ReportDistributionAdmin(admin.ModelAdmin):
    list_display = [
        'report', 'recipient', 'recipient_unit',
        'method', 'copies', 'distribution_date',
    ]
    list_filter = ['method', 'distribution_date']
    search_fields = ['report__report_no', 'recipient', 'recipient_unit']
