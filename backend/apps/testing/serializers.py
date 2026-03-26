from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer

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
    class Meta:
        model = TestParameter
        fields = [
            'id', 'method', 'name', 'code', 'unit', 'precision',
            'min_value', 'max_value', 'is_required',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestMethodSerializer(BaseModelSerializer):
    category_name = serializers.CharField(
        source='category.name', read_only=True,
    )

    class Meta:
        model = TestMethod
        fields = [
            'id', 'name', 'standard_no', 'standard_name',
            'category', 'category_name', 'description', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestMethodDetailSerializer(TestMethodSerializer):
    parameters = TestParameterSerializer(many=True, read_only=True)

    class Meta(TestMethodSerializer.Meta):
        fields = TestMethodSerializer.Meta.fields + ['parameters']


class TestTaskListSerializer(BaseModelSerializer):
    sample_name = serializers.CharField(source='sample.name', read_only=True)
    sample_no = serializers.CharField(source='sample.sample_no', read_only=True)
    method_name = serializers.CharField(source='test_method.name', read_only=True)
    tester_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = TestTask
        fields = [
            'id', 'task_no', 'sample', 'sample_name', 'sample_no',
            'commission', 'test_method', 'method_name',
            'assigned_tester', 'tester_name',
            'planned_date', 'actual_date', 'status', 'status_display',
            'age_days', 'is_overdue', 'created_at',
        ]
        read_only_fields = ['id', 'task_no', 'created_at']

    def get_tester_name(self, obj: TestTask) -> str:
        if obj.assigned_tester:
            return (
                obj.assigned_tester.get_full_name()
                or str(obj.assigned_tester)
            )
        return ''


class TestTaskDetailSerializer(TestTaskListSerializer):
    test_method_detail = TestMethodSerializer(
        source='test_method', read_only=True,
    )

    class Meta(TestTaskListSerializer.Meta):
        fields = TestTaskListSerializer.Meta.fields + [
            'test_parameter', 'assigned_equipment',
            'test_method_detail', 'remark', 'updated_at', 'created_by',
        ]


class TestTaskAssignSerializer(serializers.Serializer):
    tester = serializers.IntegerField()
    equipment = serializers.IntegerField(required=False, allow_null=True)
    planned_date = serializers.DateField(required=False, allow_null=True)


class RecordTemplateSerializer(BaseModelSerializer):
    method_name = serializers.CharField(
        source='test_method.name', read_only=True,
    )

    class Meta:
        model = RecordTemplate
        fields = [
            'id', 'name', 'code', 'test_method', 'method_name',
            'version', 'schema', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


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
    task_no = serializers.CharField(source='task.task_no', read_only=True)
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
    parameter_name = serializers.CharField(
        source='parameter.name', read_only=True,
    )
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
    parameter_name = serializers.CharField(
        source='test_parameter.name', read_only=True,
    )

    class Meta:
        model = JudgmentRule
        fields = [
            'id', 'test_parameter', 'parameter_name', 'grade',
            'min_value', 'max_value', 'standard_ref',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
