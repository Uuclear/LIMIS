from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.audit import log_business_event

from .models import Report, ReportApproval


def _check_permission(user, required_role: str) -> None:
    role_perm_map = {
        'compile': 'reports.compile_report',
        'audit': 'reports.audit_report',
        'approve': 'reports.approve_report',
    }
    perm = role_perm_map.get(required_role)
    if perm and not user.has_perm(perm):
        raise PermissionDenied(f'没有{required_role}权限')


def _create_approval(
    report: Report,
    role: str,
    action: str,
    user,
    comment: str = '',
    signature=None,
) -> ReportApproval:
    """
    Persist one approval row for the transition just applied on ``report``.

    Callers must hold a row lock on ``report`` (``select_for_update``) so that
    concurrent requests cannot apply the same transition twice; idempotent
    early returns in submit/audit/approve/void must skip calling this helper.
    """
    return ReportApproval.objects.create(
        report=report,
        role=role,
        action=action,
        user=user,
        comment=comment,
        signature=signature,
        created_by=user,
    )


@transaction.atomic
def submit_for_audit(report_id: int, user) -> Report:
    report = Report.objects.select_for_update().get(pk=report_id)
    if report.status == 'pending_audit':
        return report
    if report.status != 'draft':
        raise ValidationError('只有草稿状态可以提交审核')

    _check_permission(user, 'compile')
    report.status = 'pending_audit'
    report.compiler = user
    report.compile_date = timezone.now()
    report.save(update_fields=[
        'status', 'compiler', 'compile_date', 'updated_at',
    ])
    _create_approval(report, 'compile', 'submit', user)
    log_business_event(
        user=user,
        module='report',
        action='submit_audit',
        entity='report',
        entity_id=report.pk,
        path=f'/api/v1/reports/reports/{report.pk}/submit_audit/',
        payload={'report_no': report.report_no, 'status': report.status},
    )
    from apps.system.services import notify_users_by_permission_code

    notify_users_by_permission_code(
        'report:approve',
        'report_audit',
        f'报告待审核：{report.report_no}',
        '',
        f'/reports/{report.pk}',
    )
    return report


@transaction.atomic
def audit_report(
    report_id: int,
    user,
    approved: bool,
    comment: str = '',
    signature=None,
) -> Report:
    report = Report.objects.select_for_update().get(pk=report_id)
    target_status = 'pending_approve' if approved else 'draft'
    if report.status == target_status:
        return report
    if report.status != 'pending_audit':
        raise ValidationError('只有待审核状态可以审核')

    _check_permission(user, 'audit')
    action = 'pass' if approved else 'reject'
    report.auditor = user
    report.audit_date = timezone.now()
    report.status = 'pending_approve' if approved else 'draft'
    report.save(update_fields=[
        'status', 'auditor', 'audit_date', 'updated_at',
    ])
    _create_approval(report, 'audit', action, user, comment, signature)
    log_business_event(
        user=user,
        module='report',
        action='audit',
        entity='report',
        entity_id=report.pk,
        path=f'/api/v1/reports/reports/{report.pk}/audit/',
        payload={
            'report_no': report.report_no,
            'approved': approved,
            'status': report.status,
        },
    )
    if approved:
        from apps.system.services import notify_users_by_permission_code

        notify_users_by_permission_code(
            'report:approve',
            'report_approve',
            f'报告待批准：{report.report_no}',
            '',
            f'/reports/{report.pk}',
        )
    return report


@transaction.atomic
def approve_report(
    report_id: int,
    user,
    approved: bool,
    comment: str = '',
    signature=None,
) -> Report:
    report = Report.objects.select_for_update().get(pk=report_id)
    target_status = 'approved' if approved else 'pending_audit'
    if report.status == target_status:
        return report
    if report.status != 'pending_approve':
        raise ValidationError('只有待批准状态可以批准')

    _check_permission(user, 'approve')
    action = 'pass' if approved else 'reject'
    report.approver = user
    report.approve_date = timezone.now()
    report.status = 'approved' if approved else 'pending_audit'
    report.save(update_fields=[
        'status', 'approver', 'approve_date', 'updated_at',
    ])
    _create_approval(report, 'approve', action, user, comment, signature)
    log_business_event(
        user=user,
        module='report',
        action='approve',
        entity='report',
        entity_id=report.pk,
        path=f'/api/v1/reports/reports/{report.pk}/approve/',
        payload={
            'report_no': report.report_no,
            'approved': approved,
            'status': report.status,
        },
    )
    return report


@transaction.atomic
def issue_report(report_id: int, user) -> Report:
    report = Report.objects.select_for_update().get(pk=report_id)
    if report.status == 'issued':
        return report
    if report.status != 'approved':
        raise ValidationError('只有已批准的报告可以发放')

    report.status = 'issued'
    report.issue_date = timezone.now().date()
    report.save(update_fields=['status', 'issue_date', 'updated_at'])
    log_business_event(
        user=user,
        module='report',
        action='issue',
        entity='report',
        entity_id=report.pk,
        path=f'/api/v1/reports/reports/{report.pk}/issue/',
        payload={'report_no': report.report_no, 'issue_date': str(report.issue_date)},
    )
    if report.compiler_id:
        from apps.system.services import notify_user

        notify_user(
            report.compiler_id,
            'system',
            f'报告已发放：{report.report_no}',
            '',
            f'/reports/{report.pk}',
        )
    return report


@transaction.atomic
def void_report(report_id: int, user, reason: str = '') -> Report:
    report = Report.objects.select_for_update().get(pk=report_id)
    if report.status == 'voided':
        return report

    report.status = 'voided'
    report.save(update_fields=['status', 'updated_at'])
    _create_approval(report, 'approve', 'reject', user, comment=reason)
    log_business_event(
        user=user,
        module='report',
        action='void',
        entity='report',
        entity_id=report.pk,
        path=f'/api/v1/reports/reports/{report.pk}/void/',
        payload={'report_no': report.report_no, 'reason': reason},
    )
    return report
