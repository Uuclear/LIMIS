from __future__ import annotations

from django.http import FileResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from . import generator, workflow
from .filters import ReportFilter
from .models import Report, ReportDistribution, ReportTemplate
from .serializers import (
    ReportCreateSerializer,
    ReportDetailSerializer,
    ReportDistributionSerializer,
    ReportListSerializer,
    ReportTemplateSerializer,
)


class ReportViewSet(BaseModelViewSet):
    queryset = Report.objects.select_related(
        'commission', 'compiler', 'auditor', 'approver', 'created_by',
    ).prefetch_related('approvals', 'distributions')
    lims_module = 'report'
    lims_action_map = {
        'generate': 'edit',
        'submit_audit': 'edit',
        'audit': 'approve',
        'approve': 'approve',
        'issue': 'approve',
        'void': 'delete',
        'preview': 'view',
        'download': 'export',
        'distribute': 'edit',
        'verify': 'view',
    }
    filterset_class = ReportFilter
    search_fields = ['report_no', 'commission__commission_no']
    ordering_fields = ['created_at', 'compile_date', 'issue_date']

    def get_serializer_class(self) -> type:
        if self.action == 'list':
            return ReportListSerializer
        if self.action == 'create':
            return ReportCreateSerializer
        return ReportDetailSerializer

    def perform_create(self, serializer) -> None:
        commission = serializer.validated_data['commission']
        report_no = generator.generate_report_no(commission)
        qr_code = ''
        kwargs = {
            'report_no': report_no,
            'qr_code': qr_code,
        }
        if self.request.user.is_authenticated:
            kwargs['created_by'] = self.request.user
        serializer.save(**kwargs)

    @action(detail=True, methods=['post'])
    def generate(self, request: Request, pk: str = None) -> Response:
        report = self.get_object()
        pdf_bytes = generator.generate_report_pdf(report.pk)
        from django.core.files.base import ContentFile
        report.pdf_file.save(
            f'{report.report_no}.pdf',
            ContentFile(pdf_bytes),
            save=True,
        )
        report.qr_code = generator.generate_qr_verification(report.pk)
        report.save(update_fields=['qr_code', 'updated_at'])
        return Response({
            'code': 200,
            'message': 'PDF已生成',
            'data': ReportDetailSerializer(report).data,
        })

    @action(detail=True, methods=['post'])
    def submit_audit(self, request: Request, pk: str = None) -> Response:
        report = workflow.submit_for_audit(int(pk), request.user)
        return Response({
            'code': 200,
            'message': '已提交审核',
            'data': ReportDetailSerializer(report).data,
        })

    @action(detail=True, methods=['post'])
    def audit(self, request: Request, pk: str = None) -> Response:
        approved = request.data.get('approved', True)
        comment = request.data.get('comment', '')
        signature = request.FILES.get('signature')
        report = workflow.audit_report(
            int(pk), request.user, approved, comment, signature,
        )
        return Response({
            'code': 200,
            'message': '审核完成',
            'data': ReportDetailSerializer(report).data,
        })

    @action(detail=True, methods=['post'])
    def approve(self, request: Request, pk: str = None) -> Response:
        approved = request.data.get('approved', True)
        comment = request.data.get('comment', '')
        signature = request.FILES.get('signature')
        report = workflow.approve_report(
            int(pk), request.user, approved, comment, signature,
        )
        return Response({
            'code': 200,
            'message': '批准完成',
            'data': ReportDetailSerializer(report).data,
        })

    @action(detail=True, methods=['post'])
    def issue(self, request: Request, pk: str = None) -> Response:
        report = workflow.issue_report(int(pk), request.user)
        return Response({
            'code': 200,
            'message': '报告已发放',
            'data': ReportDetailSerializer(report).data,
        })

    @action(detail=True, methods=['post'])
    def void(self, request: Request, pk: str = None) -> Response:
        reason = request.data.get('reason', '')
        report = workflow.void_report(int(pk), request.user, reason)
        return Response({
            'code': 200,
            'message': '报告已作废',
            'data': ReportDetailSerializer(report).data,
        })

    @action(detail=True, methods=['get'])
    def preview(self, request: Request, pk: str = None) -> HttpResponse:
        report = self.get_object()
        pdf_bytes = generator.generate_report_pdf(report.pk)
        return HttpResponse(pdf_bytes, content_type='application/pdf')

    @action(detail=True, methods=['get'])
    def download(self, request: Request, pk: str = None) -> FileResponse:
        report = self.get_object()
        if report.pdf_file:
            response = FileResponse(
                report.pdf_file.open('rb'),
                content_type='application/pdf',
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{report.report_no}.pdf"'
            )
            return response
        pdf_bytes = generator.generate_report_pdf(report.pk)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{report.report_no}.pdf"'
        )
        return response

    @action(detail=True, methods=['post'])
    def distribute(self, request: Request, pk: str = None) -> Response:
        report = self.get_object()
        serializer = ReportDistributionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report, created_by=request.user)
        return Response({
            'code': 201,
            'message': '发放记录已创建',
            'data': serializer.data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='verify')
    def verify(self, request: Request, pk: str = None) -> Response:
        report = self.get_object()
        return Response({
            'code': 200,
            'data': {
                'report_no': report.report_no,
                'status': report.status,
                'status_display': report.get_status_display(),
                'compile_date': report.compile_date,
                'issue_date': report.issue_date,
                'has_cma': report.has_cma,
            },
        })


class ReportDistributionViewSet(BaseModelViewSet):
    serializer_class = ReportDistributionSerializer
    lims_module = 'report'

    def get_queryset(self):
        return ReportDistribution.objects.filter(
            report_id=self.kwargs['report_pk'],
        )

    def perform_create(self, serializer) -> None:
        report = Report.objects.get(pk=self.kwargs['report_pk'])
        if self.request.user.is_authenticated:
            serializer.save(
                report=report, created_by=self.request.user,
            )
        else:
            serializer.save(report=report)


class ReportTemplateViewSet(BaseModelViewSet):
    queryset = ReportTemplate.objects.select_related(
        'test_method', 'test_parameter', 'created_by',
    )
    serializer_class = ReportTemplateSerializer
    lims_module = 'report'
    search_fields = ['name', 'code', 'report_type']
    filterset_fields = ['is_active', 'report_type', 'test_method', 'test_parameter']
