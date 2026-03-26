from django.contrib import admin

from .models import (
    JudgmentRule,
    OriginalRecord,
    RecordRevision,
    RecordTemplate,
    TestCategory,
    TestMethod,
    TestParameter,
    TestResult,
    TestTask,
)


class TestParameterInline(admin.TabularInline):
    model = TestParameter
    extra = 0
    fields = ['name', 'code', 'unit', 'precision', 'is_required']


@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'sort_order']
    list_filter = ['parent']
    search_fields = ['name', 'code']
    ordering = ['sort_order', 'code']


@admin.register(TestMethod)
class TestMethodAdmin(admin.ModelAdmin):
    list_display = ['standard_no', 'name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'standard_no', 'standard_name']
    inlines = [TestParameterInline]


@admin.register(TestParameter)
class TestParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'method', 'unit', 'precision', 'is_required']
    list_filter = ['method', 'is_required']
    search_fields = ['name', 'code']


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin):
    list_display = [
        'task_no', 'sample', 'test_method',
        'assigned_tester', 'planned_date', 'status', 'created_at',
    ]
    list_filter = ['status', 'planned_date']
    search_fields = ['task_no', 'sample__sample_no']
    readonly_fields = ['task_no', 'created_at', 'updated_at', 'created_by']
    date_hierarchy = 'planned_date'


class RecordRevisionInline(admin.TabularInline):
    model = RecordRevision
    extra = 0
    readonly_fields = ['field_path', 'old_value', 'new_value', 'changed_by', 'changed_at']


@admin.register(RecordTemplate)
class RecordTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'test_method', 'version', 'is_active']
    list_filter = ['is_active', 'test_method']
    search_fields = ['name', 'code']


@admin.register(OriginalRecord)
class OriginalRecordAdmin(admin.ModelAdmin):
    list_display = [
        'task', 'template', 'status',
        'recorder', 'reviewer', 'review_date',
    ]
    list_filter = ['status']
    search_fields = ['task__task_no']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [RecordRevisionInline]


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = [
        'task', 'parameter', 'raw_value', 'rounded_value',
        'display_value', 'judgment',
    ]
    list_filter = ['judgment']
    search_fields = ['task__task_no', 'parameter__name']


@admin.register(JudgmentRule)
class JudgmentRuleAdmin(admin.ModelAdmin):
    list_display = ['test_parameter', 'grade', 'min_value', 'max_value', 'standard_ref']
    list_filter = ['test_parameter']
    search_fields = ['grade', 'standard_ref']
