from __future__ import annotations

from datetime import date

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.serializers import BaseModelSerializer

from .models import (
    Calibration,
    Equipment,
    EquipUsageLog,
    Maintenance,
    PeriodCheck,
)


class CalibrationSerializer(BaseModelSerializer):
    conclusion_display = serializers.CharField(
        source='get_conclusion_display', read_only=True,
    )

    class Meta:
        model = Calibration
        fields = [
            'id', 'equipment', 'certificate_no', 'calibration_date',
            'valid_until', 'calibration_org', 'conclusion',
            'conclusion_display', 'attachment', 'remark',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'equipment': {'required': False}}


class PeriodCheckSerializer(BaseModelSerializer):
    conclusion_display = serializers.CharField(
        source='get_conclusion_display', read_only=True,
    )
    checker_name = serializers.SerializerMethodField()

    class Meta:
        model = PeriodCheck
        fields = [
            'id', 'equipment', 'check_date', 'check_method',
            'check_result', 'conclusion', 'conclusion_display',
            'checker', 'checker_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'equipment': {'required': False}}

    def get_checker_name(self, obj: PeriodCheck) -> str:
        if obj.checker:
            return obj.checker.get_full_name() or str(obj.checker)
        return ''


class MaintenanceSerializer(BaseModelSerializer):
    type_display = serializers.CharField(
        source='get_maintenance_type_display', read_only=True,
    )
    handler_name = serializers.SerializerMethodField()

    class Meta:
        model = Maintenance
        fields = [
            'id', 'equipment', 'maintenance_type', 'type_display',
            'maintenance_date', 'description', 'result', 'cost',
            'handler', 'handler_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'equipment': {'required': False}}

    def get_handler_name(self, obj: Maintenance) -> str:
        if obj.handler:
            return obj.handler.get_full_name() or str(obj.handler)
        return ''


class EquipUsageLogSerializer(BaseModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = EquipUsageLog
        fields = [
            'id', 'equipment', 'task', 'user', 'user_name',
            'start_time', 'end_time', 'condition_before',
            'condition_after', 'remark', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'equipment': {'required': False}}

    def get_user_name(self, obj: EquipUsageLog) -> str:
        if obj.user:
            return obj.user.get_full_name() or str(obj.user)
        return ''


class EquipmentListSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    category_display = serializers.CharField(
        source='get_category_display', read_only=True,
    )
    calibration_status = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'model_no', 'serial_no', 'manage_no',
            'manufacturer', 'category', 'category_display',
            'status', 'status_display', 'location',
            'next_calibration_date', 'calibration_status',
            'days_until_expiry',
            'created_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'created_at', 'created_by',
        ]

    def get_calibration_status(self, obj: Equipment) -> str:
        if not obj.next_calibration_date:
            return 'unknown'
        delta = (obj.next_calibration_date - date.today()).days
        if delta < 0:
            return 'expired'
        if delta <= 30:
            return 'expiring'
        return 'valid'

    def get_days_until_expiry(self, obj: Equipment) -> int | None:
        if not obj.next_calibration_date:
            return None
        return (obj.next_calibration_date - date.today()).days


class EquipmentDetailSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    category_display = serializers.CharField(
        source='get_category_display', read_only=True,
    )
    calibrations = CalibrationSerializer(many=True, read_only=True)
    period_checks = PeriodCheckSerializer(many=True, read_only=True)
    maintenances = MaintenanceSerializer(many=True, read_only=True)
    recent_usage_logs = serializers.SerializerMethodField()
    calibration_status = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'model_no', 'serial_no', 'manage_no',
            'manufacturer', 'category', 'category_display',
            'accuracy', 'measure_range', 'purchase_date',
            'status', 'status_display', 'location',
            'calibration_cycle', 'next_calibration_date',
            'calibration_status', 'days_until_expiry', 'remark',
            'calibrations', 'period_checks', 'maintenances',
            'recent_usage_logs',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by',
        ]

    def get_recent_usage_logs(self, obj: Equipment) -> list:
        logs = obj.usage_logs.select_related('user')[:10]
        return EquipUsageLogSerializer(logs, many=True).data

    def get_calibration_status(self, obj: Equipment) -> str:
        if not obj.next_calibration_date:
            return 'unknown'
        delta = (obj.next_calibration_date - date.today()).days
        if delta < 0:
            return 'expired'
        if delta <= 30:
            return 'expiring'
        return 'valid'

    def get_days_until_expiry(self, obj: Equipment) -> int | None:
        if not obj.next_calibration_date:
            return None
        return (obj.next_calibration_date - date.today()).days


class EquipmentCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'model_no', 'serial_no', 'manage_no',
            'manufacturer', 'category', 'accuracy', 'measure_range',
            'purchase_date', 'status', 'location',
            'calibration_cycle', 'next_calibration_date', 'remark',
        ]
        read_only_fields = ['id']

    def validate_manage_no(self, value: str) -> str:
        v = (value or '').strip()
        if not v:
            raise ValidationError('管理编号不能为空')
        return v

    def validate(self, attrs: dict) -> dict:
        manage_no = attrs.get('manage_no')
        if manage_no is None and self.instance is not None:
            return attrs
        if manage_no is not None:
            mn = str(manage_no).strip()
            qs = Equipment.objects.filter(manage_no=mn)
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    {'manage_no': '已存在相同管理编号的设备，请更换编号或编辑该设备。'},
                )
        return attrs
