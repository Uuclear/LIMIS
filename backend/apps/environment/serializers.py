from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer

from .models import EnvAlarm, EnvRecord, MonitoringPoint


class MonitoringPointSerializer(BaseModelSerializer):
    class Meta:
        model = MonitoringPoint
        fields = [
            'id', 'name', 'code', 'location',
            'temp_min', 'temp_max', 'humidity_min', 'humidity_max',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnvRecordSerializer(serializers.ModelSerializer):
    point_name = serializers.CharField(
        source='point.name', read_only=True,
    )

    class Meta:
        model = EnvRecord
        fields = [
            'id', 'point', 'point_name', 'temperature',
            'humidity', 'recorded_at', 'is_alarm',
        ]
        read_only_fields = ['id', 'is_alarm']


class EnvAlarmSerializer(BaseModelSerializer):
    point_name = serializers.CharField(
        source='point.name', read_only=True,
    )
    alarm_type_display = serializers.CharField(
        source='get_alarm_type_display', read_only=True,
    )
    resolved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = EnvAlarm
        fields = [
            'id', 'point', 'point_name', 'alarm_type',
            'alarm_type_display', 'alarm_value', 'threshold',
            'alarm_time', 'is_resolved', 'resolved_by',
            'resolved_by_name', 'resolved_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
        ]

    def get_resolved_by_name(self, obj: EnvAlarm) -> str:
        if obj.resolved_by:
            return obj.resolved_by.get_full_name() or str(obj.resolved_by)
        return ''
