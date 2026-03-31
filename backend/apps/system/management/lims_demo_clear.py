"""删除 LIMIS 演示数据（与 lims_demo_seeder 约定一致）。"""
from __future__ import annotations

from django.contrib.auth import get_user_model

P = 'LIMIS-DEMO'
_STD_NOS = ('GB/T 50081-2019', 'GB/T 228.1-2021', 'JGJ 52-2006')


def clear_lims_demo_data() -> None:
    from apps.system.models import Notification
    from apps.quality.models import (
        Complaint, CorrectiveAction, AuditFinding, InternalAudit,
        ManagementReview, NonConformity, ReviewDecision,
    )
    from apps.reports.models import Report, ReportApproval, ReportDistribution
    from apps.testing.models import (
        JudgmentRule, OriginalRecord, RecordRevision, RecordTemplate,
        TestParameter, TestMethod, TestCategory, TestResult, TestTask,
    )
    from apps.samples.models import Sample, SampleDisposal, SampleGroup
    from apps.commissions.models import Commission, CommissionItem, ContractReview
    from apps.projects.models import Project, Organization, SubProject, Witness, Contract
    from apps.consumables.models import Consumable, ConsumableIn, ConsumableOut, Supplier
    from apps.environment.models import EnvRecord, EnvAlarm, MonitoringPoint
    from apps.equipment.models import Calibration, Equipment
    from apps.staff.models import Authorization, Certificate, StaffProfile, Training
    from apps.standards.models import Standard

    User = get_user_model()
    demo_users = list(User.objects.filter(username__startswith='demo_'))

    TestResult.objects.filter(task__task_no__startswith='TT-2024-').delete()
    OriginalRecord.objects.filter(task__task_no__startswith='TT-2024-').delete()
    TestTask.objects.filter(task_no__startswith='TT-2024-').delete()
    Sample.objects.filter(sample_no__startswith='YP-2024-').delete()
    SampleGroup.objects.filter(group_no__startswith='SG-2024-').delete()
    Report.objects.filter(report_no__startswith='JC-2024-').delete()
    Commission.objects.filter(commission_no__startswith='WT-2024-').delete()
    Project.objects.filter(code='PDJC-2024-001').delete()
    RecordTemplate.objects.filter(code__startswith='TPL-').delete()
    Notification.objects.filter(recipient__in=demo_users).delete()
    ReportDistribution.objects.filter(report__report_no__startswith=f'{P}-RPT').delete()
    ReportApproval.objects.filter(report__report_no__startswith=f'{P}-RPT').delete()
    Report.objects.filter(report_no__startswith=f'{P}-RPT').delete()
    TestResult.objects.filter(task__task_no__startswith=f'{P}-TT').delete()
    RecordRevision.objects.filter(record__task__task_no__startswith=f'{P}-TT').delete()
    OriginalRecord.objects.filter(task__task_no__startswith=f'{P}-TT').delete()
    TestTask.objects.filter(task_no__startswith=f'{P}-TT').delete()
    SampleDisposal.objects.filter(sample__sample_no__startswith=f'{P}-YP').delete()
    Sample.objects.filter(sample_no__startswith=f'{P}-YP').delete()
    SampleGroup.objects.filter(group_no__startswith=f'{P}-SG').delete()
    CommissionItem.objects.filter(commission__commission_no__startswith=f'{P}-WT').delete()
    ContractReview.objects.filter(commission__commission_no__startswith=f'{P}-WT').delete()
    Commission.objects.filter(commission_no__startswith=f'{P}-WT').delete()
    Witness.objects.filter(project__code=f'{P}-PRJ-001').delete()
    Organization.objects.filter(project__code=f'{P}-PRJ-001').delete()
    SubProject.objects.filter(project__code=f'{P}-PRJ-001').delete()
    Contract.objects.filter(contract_no__startswith=f'{P}-CONT').delete()
    Project.objects.filter(code=f'{P}-PRJ-001').delete()
    ConsumableOut.objects.filter(consumable__code__startswith=f'{P}-HC').delete()
    ConsumableIn.objects.filter(consumable__code__startswith=f'{P}-HC').delete()
    Consumable.objects.filter(code__startswith=f'{P}-HC').delete()
    Supplier.objects.filter(name__startswith=f'{P}-SUP').delete()
    EnvAlarm.objects.filter(point__code__startswith=f'{P}-ENV').delete()
    EnvRecord.objects.filter(point__code__startswith=f'{P}-ENV').delete()
    MonitoringPoint.objects.filter(code__startswith=f'{P}-ENV').delete()
    Calibration.objects.filter(equipment__manage_no__startswith=f'{P}-EQ').delete()
    Equipment.objects.filter(manage_no__startswith=f'{P}-EQ').delete()
    RecordTemplate.objects.filter(code__startswith=f'{P}-TPL').delete()
    JudgmentRule.objects.filter(
        test_parameter__code__in=['fcu', 'Rel', 'Rm', 'A', 'Mx'],
        test_parameter__method__standard_no__in=list(_STD_NOS),
    ).delete()
    TestParameter.objects.filter(method__standard_no__in=list(_STD_NOS)).delete()
    TestMethod.objects.filter(standard_no__in=list(_STD_NOS)).delete()
    TestCategory.objects.filter(code__startswith=f'{P}-CAT').delete()
    for std_no in _STD_NOS:
        Standard.objects.filter(standard_no=std_no).delete()
    CorrectiveAction.objects.filter(finding__audit__audit_no__startswith=f'{P}-NB').delete()
    AuditFinding.objects.filter(audit__audit_no__startswith=f'{P}-NB').delete()
    InternalAudit.objects.filter(audit_no__startswith=f'{P}-NB').delete()
    ReviewDecision.objects.filter(review__review_no__startswith=f'{P}-PG').delete()
    ManagementReview.objects.filter(review_no__startswith=f'{P}-PG').delete()
    NonConformity.objects.filter(nc_no__startswith=f'{P}-BF').delete()
    Complaint.objects.filter(complaint_no__startswith=f'{P}-TS').delete()
    Training.objects.filter(staff__employee_no__startswith=f'{P}-EMP').delete()
    Authorization.objects.filter(staff__employee_no__startswith=f'{P}-EMP').delete()
    Certificate.objects.filter(staff__employee_no__startswith=f'{P}-EMP').delete()
    StaffProfile.objects.filter(employee_no__startswith=f'{P}-EMP').delete()
    User.objects.filter(username__startswith='demo_').delete()
