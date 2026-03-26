from django.contrib import admin

from .models import Sample, SampleDisposal, SampleGroup


@admin.register(SampleGroup)
class SampleGroupAdmin(admin.ModelAdmin):
    list_display = ['group_no', 'name', 'sample_count', 'created_at']
    search_fields = ['group_no', 'name']
    list_filter = ['created_at']


class SampleDisposalInline(admin.TabularInline):
    model = SampleDisposal
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = [
        'sample_no', 'name', 'specification', 'status',
        'sampling_date', 'received_date', 'commission', 'created_at',
    ]
    list_filter = ['status', 'sampling_date', 'received_date']
    search_fields = ['sample_no', 'blind_no', 'name']
    readonly_fields = ['sample_no', 'blind_no', 'created_at', 'updated_at']
    raw_id_fields = ['commission', 'group', 'created_by']
    inlines = [SampleDisposalInline]


@admin.register(SampleDisposal)
class SampleDisposalAdmin(admin.ModelAdmin):
    list_display = ['sample', 'disposal_type', 'disposal_date', 'handler', 'created_at']
    list_filter = ['disposal_type', 'disposal_date']
    search_fields = ['sample__sample_no']
    raw_id_fields = ['sample', 'handler']
