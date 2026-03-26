from django.contrib import admin

from .models import Commission, CommissionItem, ContractReview


class CommissionItemInline(admin.TabularInline):
    model = CommissionItem
    extra = 0
    fields = [
        'test_object', 'test_item', 'test_standard',
        'specification', 'grade', 'quantity', 'unit',
    ]


class ContractReviewInline(admin.StackedInline):
    model = ContractReview
    extra = 0
    max_num = 1


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [
        'commission_no', 'project', 'construction_part',
        'commission_date', 'client_unit', 'status', 'created_at',
    ]
    list_filter = ['status', 'is_witnessed', 'commission_date']
    search_fields = ['commission_no', 'construction_part', 'client_unit']
    readonly_fields = ['commission_no', 'created_at', 'updated_at', 'created_by']
    inlines = [CommissionItemInline, ContractReviewInline]
    date_hierarchy = 'commission_date'


@admin.register(CommissionItem)
class CommissionItemAdmin(admin.ModelAdmin):
    list_display = [
        'commission', 'test_object', 'test_item',
        'specification', 'quantity', 'unit',
    ]
    list_filter = ['test_object']
    search_fields = ['test_object', 'test_item', 'commission__commission_no']


@admin.register(ContractReview)
class ContractReviewAdmin(admin.ModelAdmin):
    list_display = [
        'commission', 'conclusion', 'reviewer', 'review_date',
    ]
    list_filter = ['conclusion']
    search_fields = ['commission__commission_no']
    readonly_fields = ['review_date']
