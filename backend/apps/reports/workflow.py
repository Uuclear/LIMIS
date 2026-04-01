from __future__ import annotations

import logging
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Report, ReportApproval

logger = logging.getLogger(__name__)


def _check_permission(user, required_role: str) -> None:
    """
    检查用户是否有指定的审批权限
    使用LIMS权限系统而非Django原生权限
    """
    # 角色到LIMS权限模块的映射
    role_module_map = {
        'compile': ('report', 'edit'),
        'audit': ('report', 'approve'),
        'approve': ('report', 'approve'),
    }
    
    module, action = role_module_map.get(required_role, ('report', 'view'))
    
    # 检查用户是否有LIMS权限
    if hasattr(user, 'has_lims_permission'):
        if not user.has_lims_permission(module, action):
            raise PermissionDenied(f'没有{required_role}权限')
    else:
        # 回退到Django权限系统
        role_perm_map = {
            'compile': 'reports.change_report',
            'audit': 'reports.audit_report',
            'approve': 'reports.approve_report',
        }
        perm = role_perm_map.get(required_role)
        if perm and not user.has_perm(perm):
            raise PermissionDenied(f'没有{required_role}权限')


def _check_authorized_signer(user, report: Report) -> None:
    """
    检查用户是否是授权签字人
    批准报告时需要验证签字人资质
    """
    # 检查用户是否有授权签字人角色
    if hasattr(user, 'roles'):
        user_roles = user.roles.values_list('code', flat=True)
        if 'authorized_signer' not in user_roles:
            # 如果没有授权签字人角色，检查是否有管理员权限
            if not user.is_superuser:
                raise PermissionDenied('只有授权签字人才能批准报告')
    
    # TODO: 检查签字人的授权范围是否覆盖报告中的检测项目
    # 这需要在用户模型中添加授权范围字段


def _create_approval(
    report: Report,
    role: str,
    action: str,
    user,
    comment: str = '',
    signature=None,
) -> ReportApproval:
    """创建审批记录"""
    approval = ReportApproval.objects.create(
        report=report,
        role=role,
        action=action,
        user=user,
        comment=comment,
        signature=signature,
        created_by=user,
    )
    logger.info(f'报告审批记录已创建: 报告{report.report_no}, 角色{role}, 动作{action}, 用户{user}')
    return approval


def _send_notification(report: Report, action: str, user) -> None:
    """
    发送审批通知
    当报告状态变更时通知相关人员
    """
    from django.contrib.auth import get_user_model
    from apps.system.models import Notification
    
    User = get_user_model()
    
    # 根据不同动作确定通知接收人
    notification_config = {
        'submitted': {
            'title': '报告待审核',
            'content': f'报告 {report.report_no} 已提交，请及时审核。',
            'recipients': User.objects.filter(roles__code='auditor'),
        },
        'audit_passed': {
            'title': '报告待批准',
            'content': f'报告 {report.report_no} 审核通过，请及时批准。',
            'recipients': User.objects.filter(roles__code='authorized_signer'),
        },
        'audit_rejected': {
            'title': '报告审核退回',
            'content': f'报告 {report.report_no} 审核退回，请修改后重新提交。',
            'recipients': User.objects.filter(id=report.compiler_id) if report.compiler else User.objects.none(),
        },
        'approved': {
            'title': '报告已批准',
            'content': f'报告 {report.report_no} 已批准，可以发放。',
            'recipients': User.objects.filter(roles__code='report_manager'),
        },
        'approval_rejected': {
            'title': '报告批准退回',
            'content': f'报告 {report.report_no} 批准退回，请重新审核。',
            'recipients': User.objects.filter(id=report.auditor_id) if report.auditor else User.objects.none(),
        },
        'issued': {
            'title': '报告已发放',
            'content': f'报告 {report.report_no} 已发放。',
            'recipients': User.objects.filter(id=report.compiler_id) if report.compiler else User.objects.none(),
        },
        'voided': {
            'title': '报告已作废',
            'content': f'报告 {report.report_no} 已作废。',
            'recipients': User.objects.filter(roles__code='report_manager'),
        },
    }
    
    config = notification_config.get(action)
    if config:
        recipients = config['recipients']
        for recipient in recipients:
            if recipient and recipient != user:  # 不通知操作人自己
                Notification.objects.create(
                    recipient=recipient,
                    title=config['title'],
                    content=config['content'],
                    notification_type='report',
                    related_object_id=report.id,
                )


@transaction.atomic
def submit_for_audit(report_id: int, user) -> Report:
    """
    提交报告审核
    """
    report = Report.objects.select_for_update().get(pk=report_id)
    
    # 使用模型的状态转换方法
    try:
        report.submit_for_audit(user)
    except DjangoValidationError as e:
        raise ValidationError(str(e))
    
    # 创建审批记录
    _create_approval(report, 'compile', 'submit', user)
    
    # 发送通知
    _send_notification(report, 'submitted', user)
    
    logger.info(f'报告已提交审核: {report.report_no}, 用户: {user}')
    return report


@transaction.atomic
def audit_report(
    report_id: int,
    user,
    approved: bool,
    comment: str = '',
    signature=None,
) -> Report:
    """
    审核报告
    """
    report = Report.objects.select_for_update().get(pk=report_id)
    
    _check_permission(user, 'audit')
    
    try:
        if approved:
            report.pass_audit(user, comment)
            action = 'pass'
            notification_action = 'audit_passed'
        else:
            if not comment:
                raise ValidationError('审核退回必须填写退回原因')
            report.reject_audit(user, comment)
            action = 'reject'
            notification_action = 'audit_rejected'
    except DjangoValidationError as e:
        raise ValidationError(str(e))
    
    # 创建审批记录
    _create_approval(report, 'audit', action, user, comment, signature)
    
    # 发送通知
    _send_notification(report, notification_action, user)
    
    logger.info(f'报告审核{"通过" if approved else "退回"}: {report.report_no}, 用户: {user}')
    return report


@transaction.atomic
def approve_report(
    report_id: int,
    user,
    approved: bool,
    comment: str = '',
    signature=None,
) -> Report:
    """
    批准报告
    """
    report = Report.objects.select_for_update().get(pk=report_id)
    
    _check_permission(user, 'approve')
    _check_authorized_signer(user, report)
    
    try:
        if approved:
            report.pass_approval(user, comment)
            action = 'pass'
            notification_action = 'approved'
        else:
            if not comment:
                raise ValidationError('批准退回必须填写退回原因')
            report.reject_approval(user, comment)
            action = 'reject'
            notification_action = 'approval_rejected'
    except DjangoValidationError as e:
        raise ValidationError(str(e))
    
    # 创建审批记录
    _create_approval(report, 'approve', action, user, comment, signature)
    
    # 发送通知
    _send_notification(report, notification_action, user)
    
    logger.info(f'报告批准{"通过" if approved else "退回"}: {report.report_no}, 用户: {user}')
    return report


@transaction.atomic
def issue_report(report_id: int, user) -> Report:
    """
    发放报告
    """
    report = Report.objects.select_for_update().get(pk=report_id)
    
    try:
        report.issue(user)
    except DjangoValidationError as e:
        raise ValidationError(str(e))
    
    # 发送通知
    _send_notification(report, 'issued', user)
    
    logger.info(f'报告已发放: {report.report_no}, 用户: {user}')
    return report


@transaction.atomic
def archive_report(report_id: int, user) -> Report:
    """
    归档报告
    """
    report = Report.objects.select_for_update().get(pk=report_id)
    
    try:
        report.archive(user)
    except DjangoValidationError as e:
        raise ValidationError(str(e))
    
    logger.info(f'报告已归档: {report.report_no}, 用户: {user}')
    return report


@transaction.atomic
def void_report(report_id: int, user, reason: str = '') -> Report:
    """
    作废报告
    """
    report = Report.objects.select_for_update().get(pk=report_id)
    
    if not reason:
        raise ValidationError('作废报告必须填写作废原因')
    
    try:
        report.void(user, reason)
    except DjangoValidationError as e:
        raise ValidationError(str(e))
    
    # 创建审批记录
    _create_approval(report, 'approve', 'reject', user, comment=reason)
    
    # 发送通知
    _send_notification(report, 'voided', user)
    
    logger.info(f'报告已作废: {report.report_no}, 用户: {user}, 原因: {reason}')
    return report


def get_report_workflow_status(report: Report) -> dict:
    """
    获取报告工作流状态信息
    用于前端展示当前状态和可执行的操作
    """
    status_info = {
        'current_status': report.status,
        'current_status_display': report.get_status_display(),
        'is_editable': report.is_editable,
        'is_final': report.is_final,
        'available_actions': [],
        'approval_history': [],
    }
    
    # 根据当前状态确定可执行的操作
    actions_map = {
        'draft': ['submit', 'void'],
        'pending_audit': ['audit_pass', 'audit_reject', 'void'],
        'pending_approve': ['approve_pass', 'approve_reject', 'void'],
        'approved': ['issue', 'void'],
        'issued': ['archive', 'void'],
        'archived': [],
        'voided': [],
    }
    
    status_info['available_actions'] = actions_map.get(report.status, [])
    
    # 获取审批历史
    approvals = report.approvals.select_related('user').order_by('created_at')
    status_info['approval_history'] = [
        {
            'role': approval.get_role_display(),
            'action': approval.get_action_display(),
            'user': str(approval.user) if approval.user else '',
            'comment': approval.comment,
            'signature': approval.signature.url if approval.signature else None,
            'created_at': approval.created_at,
        }
        for approval in approvals
    ]
    
    return status_info
