from django.contrib import admin

from .models import MethodValidation, Standard


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = [
        'standard_no', 'name', 'category', 'status',
        'publish_date', 'implement_date',
    ]
    list_filter = ['status', 'category']
    search_fields = ['standard_no', 'name']
    raw_id_fields = ['replaced_by']


@admin.register(MethodValidation)
class MethodValidationAdmin(admin.ModelAdmin):
    list_display = [
        'standard', 'validation_date', 'validator', 'conclusion',
    ]
    list_filter = ['conclusion']
    raw_id_fields = ['standard', 'validator']
