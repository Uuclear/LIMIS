from django.contrib import admin

from .models import (
    Calibration,
    Equipment,
    EquipUsageLog,
    Maintenance,
    PeriodCheck,
)


class CalibrationInline(admin.TabularInline):
    model = Calibration
    extra = 0
    fields = [
        'certificate_no', 'calibration_date', 'valid_until',
        'calibration_org', 'conclusion',
    ]


class PeriodCheckInline(admin.TabularInline):
    model = PeriodCheck
    extra = 0
    fields = ['check_date', 'check_method', 'conclusion', 'checker']


class MaintenanceInline(admin.TabularInline):
    model = Maintenance
    extra = 0
    fields = [
        'maintenance_type', 'maintenance_date',
        'description', 'result', 'cost', 'handler',
    ]


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        'manage_no', 'name', 'model_no', 'category',
        'status', 'location', 'next_calibration_date', 'created_at',
    ]
    list_filter = ['status', 'category', 'location']
    search_fields = ['manage_no', 'name', 'model_no', 'serial_no']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [CalibrationInline, PeriodCheckInline, MaintenanceInline]


@admin.register(Calibration)
class CalibrationAdmin(admin.ModelAdmin):
    list_display = [
        'equipment', 'certificate_no', 'calibration_date',
        'valid_until', 'calibration_org', 'conclusion',
    ]
    list_filter = ['conclusion', 'calibration_date']
    search_fields = [
        'certificate_no', 'equipment__manage_no', 'equipment__name',
    ]
    date_hierarchy = 'calibration_date'


@admin.register(PeriodCheck)
class PeriodCheckAdmin(admin.ModelAdmin):
    list_display = [
        'equipment', 'check_date', 'conclusion', 'checker',
    ]
    list_filter = ['conclusion', 'check_date']
    search_fields = ['equipment__manage_no', 'equipment__name']


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = [
        'equipment', 'maintenance_type', 'maintenance_date',
        'cost', 'handler',
    ]
    list_filter = ['maintenance_type', 'maintenance_date']
    search_fields = ['equipment__manage_no', 'equipment__name']


@admin.register(EquipUsageLog)
class EquipUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'equipment', 'user', 'start_time', 'end_time',
    ]
    list_filter = ['start_time']
    search_fields = ['equipment__manage_no', 'equipment__name']
    readonly_fields = ['created_at']
