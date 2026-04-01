from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer, safe_related_attr

from .models import (
    JudgmentRule,
    OriginalRecord,
    RecordRevision,
    RecordTemplate,
    TestCategory,
    TestParameter,
    TestResult,
    TestTask,
)


class TestCategorySerializer(BaseModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = TestCategory
        fields = [
            'id', 'name', 'code', 'parent', 'sort_order',
            'children', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children(self, obj: TestCategory) -> list[dict]:
        children = obj.children.filter(is_deleted=False)
        return TestCategorySerializer(children, many=True).data


class TestParameterSerializer(BaseModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = TestParameter
        fields = [
            'id', 'category', 'category_name', 'standard', 'standard_no', 'standard_name',
            'name', 'code', 'unit', 'precision',
            'min_value', 'max_value', 'is_required', 'is_active', 'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_category_name(self, obj: TestParameter) -> str:
        c = safe_related_attr(obj, 'category')
        return getattr(c, 'name', '') if c else ''


class TestTaskListSerializer(BaseModelSerializer):
    sample_name = serializers.SerializerMethodField()
    sample_no = serializers.SerializerMethodField()
    parameter_name = serializers.SerializerMethodField()
    commission_no = serializers.SerializerMethodField()
    standard_no = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()
    tester_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = TestTask
        fields = [
            'id', 'task_no', 'sample', 'sample_name', 'sample_no',
            'commission', 'test_parameter', 'parameter_name',
            'assigned_tester', 'tester_name',
            'planned_date', 'actual_date', 'status', 'status_display',
            'age_days', 'is_overdue', 'commission_no', 'standard_no',
            'started_at', 'completed_at', 'created_at',
        ]
        read_only_fields = ['id', 'task_no', 'created_at']

    def get_tester_name(self, obj: TestTask) -> str:
        if obj.assigned_tester:
            return (
                obj.assigned_tester.get_full_name()
                or str(obj.assigned_tester)
            )
        return ''

    def get_sample_name(self, obj: TestTask) -> str:
        sample = safe_related_attr(obj, 'sample')
        return getattr(sample, 'name', '') if sample else ''

    def get_sample_no(self, obj: TestTask) -> str:
        sample = safe_related_attr(obj, 'sample')
        return getattr(sample, 'sample_no', '') if sample else ''

    def get_parameter_name(self, obj: TestTask) -> str:
        param = safe_related_attr(obj, 'test_parameter')
        return getattr(param, 'name', '') if param else ''

    def get_commission_no(self, obj: TestTask) -> str:
        commission = safe_related_attr(obj, 'commission')
        return getattr(commission, 'commission_no', '') if commission else ''

    def get_standard_no(self, obj: TestTask) -> str:
        param = safe_related_attr(obj, 'test_parameter')
        return getattr(param, 'standard_no', '') if param else ''

    def get_started_at(self, obj: TestTask):
        return obj.created_at

    def get_completed_at(self, obj: TestTask):
        return obj.actual_date


class TestTaskDetailSerializer(TestTaskListSerializer):
    test_parameter_detail = TestParameterSerializer(
        source='test_parameter', read_only=True,
    )

    class Meta(TestTaskListSerializer.Meta):
        fields = TestTaskListSerializer.Meta.fields + [
            'assigned_equipment',
            'test_parameter_detail', 'remark', 'updated_at', 'created_by',
        ]


class TestTaskAssignSerializer(serializers.Serializer):
    tester = serializers.IntegerField()
    equipment = serializers.IntegerField(required=False, allow_null=True)
    planned_date = serializers.DateField(required=False, allow_null=True)


class RecordTemplateSerializer(BaseModelSerializer):
    parameter_name = serializers.SerializerMethodField()
    test_parameters = serializers.PrimaryKeyRelatedField(
        queryset=TestParameter.objects.all(), many=True, required=False,
    )
    parameter_names = serializers.SerializerMethodField()
    word_template_url = serializers.SerializerMethodField()
    template_kind = serializers.SerializerMethodField()

    class Meta:
        model = RecordTemplate
        fields = [
            'id', 'name', 'code',
            'test_parameter', 'parameter_name', 'test_parameters', 'parameter_names',
            'version', 'schema', 'word_template', 'word_template_url', 'template_kind', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_parameter_name(self, obj: RecordTemplate) -> str:
        p = safe_related_attr(obj, 'test_parameter')
        return getattr(p, 'name', '') if p else ''

    def get_parameter_names(self, obj: RecordTemplate) -> list[str]:
        rows = list(obj.test_parameters.values_list('name', flat=True))
        tp = safe_related_attr(obj, 'test_parameter')
        name = getattr(tp, 'name', '') if tp else ''
        if name and name not in rows:
            rows.insert(0, name)
        return rows

    def get_template_kind(self, obj: RecordTemplate) -> str:
        return 'document' if obj.word_template else 'form'

    def get_word_template_url(self, obj: RecordTemplate) -> str:
        if not obj.word_template:
            return ''
        req = self.context.get('request')
        url = obj.word_template.url
        return req.build_absolute_uri(url) if req else url

    def validate(self, attrs: dict) -> dict:
        multi = attrs.get('test_parameters', None)
        if multi:
            attrs['test_parameter'] = None
        return attrs

    def create(self, validated_data: dict) -> RecordTemplate:
        multi = validated_data.pop('test_parameters', [])
        validated_data.pop('test_parameter', None)
        obj = super().create(validated_data)
        obj.test_parameters.set(multi)
        return obj

    def update(self, instance: RecordTemplate, validated_data: dict) -> RecordTemplate:
        multi = validated_data.pop('test_parameters', None)
        validated_data.pop('test_parameter', None)
        obj = super().update(instance, validated_data)
        if multi is not None:
            obj.test_parameters.set(multi)
        return obj


class RecordRevisionSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RecordRevision
        fields = [
            'id', 'field_path', 'old_value', 'new_value',
            'changed_by', 'changed_by_name', 'changed_at',
        ]
        read_only_fields = ['id', 'changed_by', 'changed_at']

    def get_changed_by_name(self, obj: RecordRevision) -> str:
        if obj.changed_by:
            return (
                obj.changed_by.get_full_name()
                or str(obj.changed_by)
            )
        return ''


class OriginalRecordSerializer(BaseModelSerializer):
    task_no = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    recorder_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()
    revisions = RecordRevisionSerializer(many=True, read_only=True)

    class Meta:
        model = OriginalRecord
        fields = [
            'id', 'task', 'task_no', 'template', 'template_version',
            'record_data', 'env_temperature', 'env_humidity',
            'status', 'status_display',
            'recorder', 'recorder_name',
            'reviewer', 'reviewer_name',
            'review_date', 'review_comment',
            'revisions', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'reviewer', 'review_date',
            'review_comment', 'created_at', 'updated_at',
        ]

    def get_task_no(self, obj: OriginalRecord) -> str:
        t = safe_related_attr(obj, 'task')
        return getattr(t, 'task_no', '') if t else ''

    def get_recorder_name(self, obj: OriginalRecord) -> str:
        if obj.recorder:
            return obj.recorder.get_full_name() or str(obj.recorder)
        return ''

    def get_reviewer_name(self, obj: OriginalRecord) -> str:
        if obj.reviewer:
            return obj.reviewer.get_full_name() or str(obj.reviewer)
        return ''


class OriginalRecordCreateSerializer(BaseModelSerializer):
    class Meta:
        model = OriginalRecord
        fields = [
            'id', 'task', 'template', 'template_version',
            'record_data', 'env_temperature', 'env_humidity', 'recorder',
        ]
        read_only_fields = ['id']


class TestResultSerializer(BaseModelSerializer):
    parameter_name = serializers.SerializerMethodField()
    judgment_display = serializers.CharField(
        source='get_judgment_display', read_only=True,
    )

    class Meta:
        model = TestResult
        fields = [
            'id', 'task', 'parameter', 'parameter_name',
            'raw_value', 'rounded_value', 'display_value', 'unit',
            'judgment', 'judgment_display',
            'standard_value', 'design_value', 'remark',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_parameter_name(self, obj: TestResult) -> str:
        p = safe_related_attr(obj, 'parameter')
        return getattr(p, 'name', '') if p else ''


class TestResultCreateSerializer(BaseModelSerializer):
    class Meta:
        model = TestResult
        fields = [
            'id', 'task', 'parameter',
            'raw_value', 'rounded_value', 'display_value', 'unit',
            'standard_value', 'design_value', 'remark',
        ]
        read_only_fields = ['id']


class JudgmentRuleSerializer(BaseModelSerializer):
    parameter_name = serializers.SerializerMethodField()

    class Meta:
        model = JudgmentRule
        fields = [
            'id', 'test_parameter', 'parameter_name', 'grade',
            'min_value', 'max_value', 'standard_ref',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_parameter_name(self, obj: JudgmentRule) -> str:
        p = safe_related_attr(obj, 'test_parameter')
        return getattr(p, 'name', '') if p else ''
