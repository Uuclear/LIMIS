"""
盲样管理服务

盲样管理是实验室质量保证的重要功能：
- 检测人员看到的样品编号不包含委托方信息
- 通过盲样编号与实际编号的映射表实现
- 映射表仅样品管理员和技术负责人可查看
"""

import random
import string
from datetime import datetime
from typing import Optional

from django.db import transaction
from django.core.exceptions import ValidationError

from apps.samples.models import Sample


class BlindSampleService:
    """盲样管理服务"""
    
    # 盲样编号前缀
    BLIND_PREFIX = 'BL'
    
    @classmethod
    def generate_blind_no(cls, sample: Sample) -> str:
        """
        生成盲样编号
        
        格式: BL + 年月 + 随机6位字符
        例如: BL202603-ABC123
        """
        date_part = datetime.now().strftime('%Y%m')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        blind_no = f'{cls.BLIND_PREFIX}{date_part}-{random_part}'
        
        # 确保唯一性
        while Sample.objects.filter(blind_no=blind_no).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            blind_no = f'{cls.BLIND_PREFIX}{date_part}-{random_part}'
        
        return blind_no
    
    @classmethod
    def assign_blind_no(cls, sample: Sample, save: bool = True) -> str:
        """
        为样品分配盲样编号
        
        :param sample: 样品对象
        :param save: 是否保存到数据库
        :return: 盲样编号
        """
        if sample.blind_no:
            return sample.blind_no
        
        blind_no = cls.generate_blind_no(sample)
        sample.blind_no = blind_no
        
        if save:
            sample.save(update_fields=['blind_no', 'updated_at'])
        
        return blind_no
    
    @classmethod
    def batch_assign_blind_no(cls, samples: list[Sample]) -> dict:
        """
        批量分配盲样编号
        
        :param samples: 样品列表
        :return: 映射字典 {sample_no: blind_no}
        """
        mapping = {}
        
        with transaction.atomic():
            for sample in samples:
                if not sample.blind_no:
                    blind_no = cls.assign_blind_no(sample, save=True)
                    mapping[sample.sample_no] = blind_no
                else:
                    mapping[sample.sample_no] = sample.blind_no
        
        return mapping
    
    @classmethod
    def get_real_sample_no(cls, blind_no: str) -> Optional[str]:
        """
        根据盲样编号获取真实样品编号
        
        :param blind_no: 盲样编号
        :return: 真实样品编号
        """
        try:
            sample = Sample.objects.get(blind_no=blind_no)
            return sample.sample_no
        except Sample.DoesNotExist:
            return None
    
    @classmethod
    def get_sample_by_blind_no(cls, blind_no: str) -> Optional[Sample]:
        """
        根据盲样编号获取样品对象
        
        :param blind_no: 盲样编号
        :return: 样品对象
        """
        try:
            return Sample.objects.get(blind_no=blind_no)
        except Sample.DoesNotExist:
            return None
    
    @classmethod
    def get_blind_mapping(cls, commission_id: int = None, project_id: int = None) -> list[dict]:
        """
        获取盲样映射表
        
        :param commission_id: 委托单ID（可选）
        :param project_id: 项目ID（可选）
        :return: 映射列表
        """
        queryset = Sample.objects.filter(blind_no__isnull=False).select_related('commission')
        
        if commission_id:
            queryset = queryset.filter(commission_id=commission_id)
        if project_id:
            queryset = queryset.filter(commission__project_id=project_id)
        
        return [
            {
                'sample_no': sample.sample_no,
                'blind_no': sample.blind_no,
                'sample_name': sample.name,
                'commission_no': sample.commission.commission_no,
                'status': sample.status,
            }
            for sample in queryset
        ]
    
    @classmethod
    def can_view_mapping(cls, user) -> bool:
        """
        检查用户是否有权限查看盲样映射表
        
        只有以下角色可以查看：
        - 系统管理员
        - 技术负责人
        - 样品管理员
        - 质量负责人
        """
        if user.is_superuser:
            return True
        
        if hasattr(user, 'roles'):
            role_codes = user.roles.values_list('code', flat=True)
            allowed_roles = ['admin', 'tech_director', 'sample_clerk', 'quality_director']
            return any(role in allowed_roles for role in role_codes)
        
        return False
    
    @classmethod
    def remove_blind_no(cls, sample: Sample, save: bool = True) -> None:
        """
        移除盲样编号（解除盲样状态）
        
        :param sample: 样品对象
        :param save: 是否保存到数据库
        """
        sample.blind_no = None
        
        if save:
            sample.save(update_fields=['blind_no', 'updated_at'])


class BlindSampleMixin:
    """
    盲样混入类
    可用于视图类，提供盲样相关功能
    """
    
    def get_sample_display_no(self, sample: Sample, user) -> str:
        """
        获取样品的显示编号
        
        如果用户可以查看映射表，返回真实编号
        否则返回盲样编号（如果有）
        """
        if BlindSampleService.can_view_mapping(user):
            return sample.sample_no
        return sample.blind_no or sample.sample_no
    
    def get_sample_display_info(self, sample: Sample, user) -> dict:
        """
        获取样品的显示信息
        
        根据用户权限决定返回哪些信息
        """
        can_view_mapping = BlindSampleService.can_view_mapping(user)
        
        info = {
            'id': sample.id,
            'display_no': self.get_sample_display_no(sample, user),
            'name': sample.name,
            'status': sample.status,
            'status_display': sample.get_status_display(),
        }
        
        # 只有有权限的用户才能看到委托信息
        if can_view_mapping:
            info['sample_no'] = sample.sample_no
            info['blind_no'] = sample.blind_no
            info['commission_no'] = sample.commission.commission_no if sample.commission else None
            info['project_name'] = str(sample.commission.project) if sample.commission and sample.commission.project else None
        
        return info