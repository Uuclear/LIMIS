"""
原始记录模板引擎

提供原始记录模板的渲染和生成功能：
- 根据模板schema生成表单
- 支持动态计算字段
- 支持条件显示/隐藏
- 支持数据校验规则
"""

import json
from typing import Any, Optional
from decimal import Decimal

from django.core.exceptions import ValidationError


class TemplateEngine:
    """模板引擎基类"""
    
    def __init__(self, schema: dict):
        """
        初始化模板引擎
        
        :param schema: 模板schema定义
        """
        self.schema = schema
        self.fields = schema.get('fields', [])
        self.sections = schema.get('sections', [])
        self.rules = schema.get('rules', [])
        self.calculations = schema.get('calculations', [])
    
    def render(self, data: dict = None) -> dict:
        """
        渲染模板
        
        :param data: 已有数据（用于填充表单）
        :return: 渲染后的表单结构
        """
        rendered = {
            'sections': [],
            'fields': [],
        }
        
        # 渲染分区
        for section in self.sections:
            rendered_section = self._render_section(section, data)
            rendered['sections'].append(rendered_section)
        
        # 渲染字段
        for field in self.fields:
            rendered_field = self._render_field(field, data)
            rendered['fields'].append(rendered_field)
        
        return rendered
    
    def _render_section(self, section: dict, data: dict = None) -> dict:
        """渲染分区"""
        rendered = {
            'id': section.get('id'),
            'title': section.get('title'),
            'description': section.get('description'),
            'fields': [],
            'visible': self._evaluate_visibility(section, data),
        }
        
        for field in section.get('fields', []):
            rendered_field = self._render_field(field, data)
            rendered['fields'].append(rendered_field)
        
        return rendered
    
    def _render_field(self, field: dict, data: dict = None) -> dict:
        """渲染字段"""
        field_id = field.get('id')
        
        rendered = {
            'id': field_id,
            'label': field.get('label'),
            'type': field.get('type'),
            'required': field.get('required', False),
            'visible': self._evaluate_visibility(field, data),
            'disabled': field.get('disabled', False),
            'default': field.get('default'),
            'placeholder': field.get('placeholder'),
            'unit': field.get('unit'),
            'precision': field.get('precision'),
            'min': field.get('min'),
            'max': field.get('max'),
            'options': field.get('options'),
            'validation': field.get('validation'),
            'value': data.get(field_id) if data else field.get('default'),
        }
        
        return rendered
    
    def _evaluate_visibility(self, item: dict, data: dict = None) -> bool:
        """评估可见性条件"""
        visibility = item.get('visibility')
        
        if not visibility:
            return True
        
        # 简单条件评估
        if isinstance(visibility, dict):
            condition_type = visibility.get('type')
            
            if condition_type == 'field_value':
                field_id = visibility.get('field')
                expected_value = visibility.get('value')
                actual_value = data.get(field_id) if data else None
                return actual_value == expected_value
            
            if condition_type == 'expression':
                expression = visibility.get('expression')
                return self._evaluate_expression(expression, data)
        
        return True
    
    def _evaluate_expression(self, expression: str, data: dict = None) -> bool:
        """评估表达式"""
        # 简单表达式评估（仅支持基本比较）
        # 实际应用中可以使用更复杂的表达式引擎
        try:
            # 替换变量
            if data:
                for key, value in data.items():
                    expression = expression.replace(f'${key}', str(value))
            
            # 安全评估（仅支持基本比较操作）
            # 注意：实际应用中应该使用更安全的表达式评估方法
            return bool(eval(expression))
        except Exception:
            return True
    
    def validate_data(self, data: dict) -> list[str]:
        """
        验证数据
        
        :param data: 待验证数据
        :return: 错误消息列表
        """
        errors = []
        
        for field in self.fields:
            field_id = field.get('id')
            value = data.get(field_id)
            
            # 必填校验
            if field.get('required') and value is None:
                errors.append(f'{field.get("label")} 为必填项')
            
            # 类型校验
            if value is not None:
                field_type = field.get('type')
                type_error = self._validate_type(field, value)
                if type_error:
                    errors.append(type_error)
            
            # 自定义校验规则
            validation = field.get('validation')
            if validation and value is not None:
                validation_error = self._validate_custom(field, value, validation)
                if validation_error:
                    errors.append(validation_error)
        
        return errors
    
    def _validate_type(self, field: dict, value: Any) -> Optional[str]:
        """类型校验"""
        field_type = field.get('type')
        label = field.get('label')
        
        try:
            if field_type == 'number':
                if not isinstance(value, (int, float, Decimal, str)):
                    return f'{label} 必须为数字'
                float(value)
            
            elif field_type == 'integer':
                if not isinstance(value, (int, str)):
                    return f'{label} 必须为整数'
                int(value)
            
            elif field_type == 'text':
                if not isinstance(value, str):
                    return f'{label} 必须为文本'
            
            elif field_type == 'date':
                # 日期格式校验
                pass
            
            elif field_type == 'select':
                options = field.get('options', [])
                if value not in [opt.get('value') for opt in options]:
                    return f'{label} 的值不在有效选项范围内'
            
            # 范围校验
            if field_type in ('number', 'integer'):
                min_val = field.get('min')
                max_val = field.get('max')
                num_value = float(value)
                
                if min_val is not None and num_value < min_val:
                    return f'{label} 不能小于 {min_val}'
                if max_val is not None and num_value > max_val:
                    return f'{label} 不能大于 {max_val}'
        
        except (ValueError, TypeError) as e:
            return f'{label} 格式不正确'
        
        return None
    
    def _validate_custom(self, field: dict, value: Any, validation: dict) -> Optional[str]:
        """自定义校验"""
        rule_type = validation.get('type')
        label = field.get('label')
        
        if rule_type == 'regex':
            import re
            pattern = validation.get('pattern')
            if pattern and not re.match(pattern, str(value)):
                return validation.get('message', f'{label} 格式不正确')
        
        elif rule_type == 'expression':
            expression = validation.get('expression')
            if expression and not self._evaluate_expression(expression, {'value': value}):
                return validation.get('message', f'{label} 校验失败')
        
        return None
    
    def calculate(self, data: dict) -> dict:
        """
        执行计算
        
        :param data: 输入数据
        :return: 计算后的数据（包含计算字段）
        """
        result = data.copy()
        
        for calc in self.calculations:
            target_field = calc.get('target')
            formula = calc.get('formula')
            
            if target_field and formula:
                try:
                    calculated_value = self._execute_formula(formula, data)
                    result[target_field] = calculated_value
                except Exception:
                    pass
        
        return result
    
    def _execute_formula(self, formula: str, data: dict) -> Any:
        """执行公式计算"""
        # 替换变量
        for key, value in data.items():
            formula = formula.replace(f'${key}', str(value) if value else '0')
        
        # 安全执行（仅支持数学运算）
        try:
            return eval(formula)
        except Exception:
            return None


class RecordTemplateEngine(TemplateEngine):
    """
    原始记录模板引擎
    
    专门用于原始记录的模板渲染，支持：
    - 检测参数自动填充
    - 设备信息自动填充
    - 环境条件记录
    - 结果计算
    """
    
    def render_for_task(self, task, data: dict = None) -> dict:
        """
        为检测任务渲染模板
        
        :param task: 检测任务对象
        :param data: 已有数据
        :return: 渲染后的表单结构
        """
        # 获取任务相关信息
        task_data = {
            'task_no': task.task_no,
            'sample_no': task.sample.blind_no or task.sample.sample_no,
            'sample_name': task.sample.name,
            'test_method': str(task.test_method),
            'test_parameter': str(task.test_parameter) if task.test_parameter else '',
            'equipment_name': str(task.equipment) if task.equipment else '',
            'equipment_no': task.equipment.equipment_no if task.equipment else '',
        }
        
        # 合并数据
        merged_data = {**task_data, **(data or {})}
        
        return self.render(merged_data)
    
    def calculate_results(self, data: dict) -> dict:
        """
        计算检测结果
        
        :param data: 输入数据
        :return: 包含计算结果的数据
        """
        result = self.calculate(data)
        
        # 执行结果判定
        for rule in self.rules:
            if rule.get('type') == 'result_judgment':
                judgment = self._judge_result(data, rule)
                result['result_judgment'] = judgment
        
        return result
    
    def _judge_result(self, data: dict, rule: dict) -> str:
        """判定结果"""
        criteria = rule.get('criteria', [])
        
        for criterion in criteria:
            field_id = criterion.get('field')
            operator = criterion.get('operator')
            threshold = criterion.get('threshold')
            result_text = criterion.get('result')
            
            value = data.get(field_id)
            if value is None:
                continue
            
            try:
                value = float(value)
                threshold = float(threshold)
                
                if operator == 'gte' and value >= threshold:
                    return result_text
                elif operator == 'lte' and value <= threshold:
                    return result_text
                elif operator == 'gt' and value > threshold:
                    return result_text
                elif operator == 'lt' and value < threshold:
                    return result_text
                elif operator == 'eq' and value == threshold:
                    return result_text
            except (ValueError, TypeError):
                continue
        
        return '待判定'


# 预定义的模板schema示例
TEMPLATE_EXAMPLES = {
    'concrete_compressive': {
        'name': '混凝土抗压强度检测记录',
        'sections': [
            {
                'id': 'basic_info',
                'title': '基本信息',
                'fields': [
                    {'id': 'task_no', 'label': '任务编号', 'type': 'text', 'disabled': True},
                    {'id': 'sample_no', 'label': '样品编号', 'type': 'text', 'disabled': True},
                    {'id': 'sample_name', 'label': '样品名称', 'type': 'text', 'disabled': True},
                    {'id': 'design_strength', 'label': '设计强度等级', 'type': 'text', 'required': True},
                    {'id': 'age_days', 'label': '龄期(天)', 'type': 'integer', 'required': True, 'min': 1, 'max': 365},
                ],
            },
            {
                'id': 'environment',
                'title': '环境条件',
                'fields': [
                    {'id': 'temperature', 'label': '温度', 'type': 'number', 'unit': '°C', 'required': True, 'precision': 1, 'min': 15, 'max': 25},
                    {'id': 'humidity', 'label': '相对湿度', 'type': 'number', 'unit': '%', 'required': True, 'precision': 1, 'min': 50, 'max': 70},
                ],
            },
            {
                'id': 'equipment',
                'title': '设备信息',
                'fields': [
                    {'id': 'equipment_name', 'label': '设备名称', 'type': 'text', 'disabled': True},
                    {'id': 'equipment_no', 'label': '设备编号', 'type': 'text', 'disabled': True},
                    {'id': 'calibration_date', 'label': '校准日期', 'type': 'date', 'disabled': True},
                ],
            },
            {
                'id': 'test_data',
                'title': '检测数据',
                'fields': [
                    {'id': 'specimen_size', 'label': '试件尺寸', 'type': 'text', 'required': True, 'placeholder': '如: 150×150×150mm'},
                    {'id': 'load_value', 'label': '破坏荷载', 'type': 'number', 'unit': 'kN', 'required': True, 'precision': 1},
                    {'id': 'area', 'label': '受压面积', 'type': 'number', 'unit': 'mm²', 'required': True, 'precision': 0},
                ],
            },
        ],
        'calculations': [
            {
                'target': 'compressive_strength',
                'formula': '$load_value * 1000 / $area',
                'description': '抗压强度 = 荷载 / 面积',
            },
        ],
        'rules': [
            {
                'type': 'result_judgment',
                'criteria': [
                    {'field': 'compressive_strength', 'operator': 'gte', 'threshold': '${design_strength}', 'result': '合格'},
                    {'field': 'compressive_strength', 'operator': 'lt', 'threshold': '${design_strength}', 'result': '不合格'},
                ],
            },
        ],
    },
    
    'steel_tensile': {
        'name': '钢筋拉伸试验记录',
        'sections': [
            {
                'id': 'basic_info',
                'title': '基本信息',
                'fields': [
                    {'id': 'task_no', 'label': '任务编号', 'type': 'text', 'disabled': True},
                    {'id': 'sample_no', 'label': '样品编号', 'type': 'text', 'disabled': True},
                    {'id': 'steel_grade', 'label': '钢筋牌号', 'type': 'select', 'required': True, 'options': [
                        {'value': 'HRB400', 'label': 'HRB400'},
                        {'value': 'HRB500', 'label': 'HRB500'},
                        {'value': 'HPB300', 'label': 'HPB300'},
                    ]},
                    {'id': 'diameter', 'label': '公称直径', 'type': 'number', 'unit': 'mm', 'required': True},
                ],
            },
            {
                'id': 'test_data',
                'title': '检测数据',
                'fields': [
                    {'id': 'original_area', 'label': '原始面积', 'type': 'number', 'unit': 'mm²', 'required': True},
                    {'id': 'yield_load', 'label': '屈服荷载', 'type': 'number', 'unit': 'kN', 'required': True},
                    {'id': 'max_load', 'label': '最大荷载', 'type': 'number', 'unit': 'kN', 'required': True},
                    {'id': 'elongation', 'label': '断后伸长率', 'type': 'number', 'unit': '%', 'required': True},
                ],
            },
        ],
        'calculations': [
            {
                'target': 'yield_strength',
                'formula': '$yield_load * 1000 / $original_area',
                'description': '屈服强度 = 屈服荷载 / 面积',
            },
            {
                'target': 'tensile_strength',
                'formula': '$max_load * 1000 / $original_area',
                'description': '抗拉强度 = 最大荷载 / 面积',
            },
        ],
    },
}