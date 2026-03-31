from __future__ import annotations

from django.db.models import Count
from django.utils import timezone
from rest_framework import serializers

from core.serializers import BaseModelSerializer

from .models import Contract, Organization, Project, SubProject, Witness


# ───────────────────── Organization ─────────────────────


class OrganizationSerializer(BaseModelSerializer):
    role_display = serializers.CharField(
        source='get_role_display', read_only=True,
    )

    class Meta:
        model = Organization
        fields = [
            'id', 'project', 'name', 'role', 'role_display',
            'contact_person', 'contact_phone',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        # project 由 URL 的 project_pk 注入；前端无需提交
        read_only_fields = (
            'id', 'project', 'created_at', 'updated_at', 'created_by',
        )


# ───────────────────── SubProject ─────────────────────


class SubProjectSerializer(BaseModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = SubProject
        fields = [
            'id', 'project', 'name', 'code', 'parent', 'description',
            'children',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        # project 由 URL 的 project_pk 注入；前端无需提交
        read_only_fields = (
            'id', 'project', 'created_at', 'updated_at', 'created_by',
        )

    def get_children(self, obj) -> list[dict]:
        children = obj.children.filter(is_deleted=False)
        return SubProjectSerializer(children, many=True, context=self.context).data


# ───────────────────── Contract ─────────────────────


class ContractSerializer(BaseModelSerializer):
    class Meta:
        model = Contract
        fields = [
            'id', 'project', 'contract_no', 'title', 'amount',
            'sign_date', 'start_date', 'end_date', 'scope', 'attachment',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        # project 由 URL 的 project_pk 注入；前端无需提交
        read_only_fields = (
            'id', 'project', 'created_at', 'updated_at', 'created_by',
        )


# ───────────────────── Witness ─────────────────────


class WitnessSerializer(BaseModelSerializer):
    organization_name = serializers.CharField(
        source='organization.name', read_only=True, default='',
    )

    id_type_display = serializers.CharField(
        source='get_id_type_display', read_only=True,
    )

    class Meta:
        model = Witness
        fields = [
            'id', 'project', 'name', 'id_type', 'id_type_display', 'id_number', 'organization',
            'organization_name', 'phone', 'certificate_no', 'is_active',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        # project 由 URL 的 project_pk 注入；前端无需提交
        read_only_fields = (
            'id', 'project', 'created_at', 'updated_at', 'created_by',
        )


# ───────────────────── Project ─────────────────────


class ProjectListSerializer(BaseModelSerializer):
    project_type_display = serializers.CharField(
        source='get_project_type_display', read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    organization_count = serializers.IntegerField(read_only=True)
    commission_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'address',
            'project_type', 'project_type_display',
            'status', 'status_display',
            'start_date', 'end_date',
            'organization_count', 'commission_count',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')


class ProjectDetailSerializer(BaseModelSerializer):
    project_type_display = serializers.CharField(
        source='get_project_type_display', read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    organizations = OrganizationSerializer(many=True, read_only=True)
    sub_projects = serializers.SerializerMethodField()
    contracts = ContractSerializer(many=True, read_only=True)
    witnesses = WitnessSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'address',
            'project_type', 'project_type_display',
            'status', 'status_display',
            'start_date', 'end_date', 'description',
            'organizations', 'sub_projects', 'contracts', 'witnesses',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')

    def get_sub_projects(self, obj) -> list[dict]:
        roots = obj.sub_projects.filter(parent__isnull=True, is_deleted=False)
        return SubProjectSerializer(roots, many=True, context=self.context).data


class ProjectCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'address', 'project_type',
            'status', 'start_date', 'end_date', 'description',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
        extra_kwargs = {
            'code': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data: dict) -> Project:
        code = (validated_data.get('code') or '').strip()
        if not code:
            validated_data['code'] = (
                f"PRJ-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            )
        else:
            validated_data['code'] = code
        return super().create(validated_data)

    def update(self, instance: Project, validated_data: dict) -> Project:
        if 'code' in validated_data:
            c = (validated_data.get('code') or '').strip()
            validated_data['code'] = c or instance.code
        return super().update(instance, validated_data)
