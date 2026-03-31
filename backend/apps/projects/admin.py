from django.contrib import admin

from .models import Contract, Organization, Project, SubProject, Witness


class OrganizationInline(admin.TabularInline):
    model = Organization
    extra = 0


class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0
    fields = ['contract_no', 'title', 'amount', 'sign_date']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'project_type', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'project_type']
    search_fields = ['name', 'code']
    inlines = [OrganizationInline, ContractInline]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'role', 'contact_person', 'contact_phone']
    list_filter = ['role']
    search_fields = ['name', 'contact_person']


@admin.register(SubProject)
class SubProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'project', 'parent']
    list_filter = ['project']
    search_fields = ['name', 'code']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_no', 'title', 'project', 'amount', 'sign_date']
    list_filter = ['project']
    search_fields = ['contract_no', 'title']


@admin.register(Witness)
class WitnessAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_type', 'project', 'organization', 'phone', 'is_active']
    list_filter = ['is_active', 'id_type', 'project']
    search_fields = ['name', 'certificate_no', 'id_number']
