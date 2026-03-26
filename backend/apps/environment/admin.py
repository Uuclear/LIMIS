from django.contrib import admin

from .models import EnvAlarm, EnvRecord, MonitoringPoint


@admin.register(MonitoringPoint)
class MonitoringPointAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'location',
        'temp_min', 'temp_max',
        'humidity_min', 'humidity_max', 'is_active',
    ]
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(EnvRecord)
class EnvRecordAdmin(admin.ModelAdmin):
    list_display = [
        'point', 'temperature', 'humidity',
        'recorded_at', 'is_alarm',
    ]
    list_filter = ['is_alarm', 'point']
    date_hierarchy = 'recorded_at'
    raw_id_fields = ['point']


@admin.register(EnvAlarm)
class EnvAlarmAdmin(admin.ModelAdmin):
    list_display = [
        'point', 'alarm_type', 'alarm_value',
        'threshold', 'alarm_time', 'is_resolved',
    ]
    list_filter = ['alarm_type', 'is_resolved']
    raw_id_fields = ['point', 'resolved_by']
