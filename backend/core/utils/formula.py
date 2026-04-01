"""
自动计算公式库

提供检测实验室常用的计算公式：
- 混凝土强度计算
- 钢筋力学性能计算
- 沥青性能计算
- 土工试验计算
- 通用数学函数
"""

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional, Union
from dataclasses import dataclass


Number = Union[int, float, Decimal, str]


@dataclass
class CalculationResult:
    """计算结果"""
    value: Decimal
    unit: str
    precision: int = 2
    formula: str = ''
    description: str = ''
    
    def __str__(self) -> str:
        return f'{self.value:.{self.precision}f} {self.unit}'
    
    def to_dict(self) -> dict:
        return {
            'value': float(self.value),
            'display': str(self),
            'unit': self.unit,
            'precision': self.precision,
            'formula': self.formula,
            'description': self.description,
        }


def to_decimal(value: Number) -> Decimal:
    """转换为Decimal"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, str):
        return Decimal(value)
    return Decimal(str(value))


def round_decimal(value: Decimal, precision: int = 2) -> Decimal:
    """四舍五入"""
    return value.quantize(Decimal(f'0.{"0" * precision}'), rounding=ROUND_HALF_UP)


class FormulaLibrary:
    """公式库基类"""
    
    @staticmethod
    def safe_divide(a: Number, b: Number, precision: int = 2) -> Decimal:
        """安全除法（避免除零错误）"""
        a_dec = to_decimal(a)
        b_dec = to_decimal(b)
        
        if b_dec == 0:
            return Decimal('0')
        
        result = a_dec / b_dec
        return round_decimal(result, precision)
    
    @staticmethod
    def percentage(value: Number, total: Number, precision: int = 2) -> Decimal:
        """计算百分比"""
        return FormulaLibrary.safe_divide(value, total, precision) * 100
    
    @staticmethod
    def average(values: list[Number], precision: int = 2) -> Decimal:
        """计算平均值"""
        if not values:
            return Decimal('0')
        
        total = sum(to_decimal(v) for v in values)
        return FormulaLibrary.safe_divide(total, len(values), precision)
    
    @staticmethod
    def standard_deviation(values: list[Number], precision: int = 2) -> Decimal:
        """计算标准差"""
        if len(values) < 2:
            return Decimal('0')
        
        avg = FormulaLibrary.average(values, precision=10)
        variance = sum((to_decimal(v) - avg) ** 2 for v in values) / len(values)
        std = Decimal(str(math.sqrt(float(variance))))
        return round_decimal(std, precision)
    
    @staticmethod
    def max_value(values: list[Number]) -> Decimal:
        """最大值"""
        if not values:
            return Decimal('0')
        return max(to_decimal(v) for v in values)
    
    @staticmethod
    def min_value(values: list[Number]) -> Decimal:
        """最小值"""
        if not values:
            return Decimal('0')
        return min(to_decimal(v) for v in values)
    
    @staticmethod
    def range_value(values: list[Number], precision: int = 2) -> Decimal:
        """极差"""
        return round_decimal(FormulaLibrary.max_value(values) - FormulaLibrary.min_value(values), precision)


class ConcreteFormula(FormulaLibrary):
    """混凝土检测计算公式"""
    
    @staticmethod
    def compressive_strength(load: Number, area: Number, precision: int = 1) -> CalculationResult:
        """
        抗压强度计算
        
        公式: fc = F / A
        fc: 抗压强度 (MPa)
        F: 破坏荷载 (kN)
        A: 受压面积 (mm²)
        
        :param load: 破坏荷载 (kN)
        :param area: 受压面积 (mm²)
        :param precision: 结果精度
        :return: 抗压强度结果
        """
        load_dec = to_decimal(load)
        area_dec = to_decimal(area)
        
        # 荷载转换为N，面积转换为mm²，结果为MPa
        strength = FormulaLibrary.safe_divide(load_dec * 1000, area_dec, precision)
        
        return CalculationResult(
            value=strength,
            unit='MPa',
            precision=precision,
            formula='fc = F × 1000 / A',
            description=f'抗压强度 = {load}kN × 1000 / {area}mm²',
        )
    
    @staticmethod
    def strength_correction(size: str, strength: Number, precision: int = 1) -> CalculationResult:
        """
        强度尺寸修正
        
        非标准尺寸试件强度修正系数：
        - 100×100×100mm: 0.95
        - 150×150×150mm: 1.00 (标准)
        - 200×200×200mm: 1.05
        
        :param size: 试件尺寸
        :param strength: 实测强度
        :param precision: 结果精度
        :return: 修正后强度
        """
        correction_factors = {
            '100': Decimal('0.95'),
            '150': Decimal('1.00'),
            '200': Decimal('1.05'),
        }
        
        # 提取尺寸
        size_key = size.split('×')[0] if '×' in size else size[:3]
        factor = correction_factors.get(size_key, Decimal('1.00'))
        
        corrected = to_decimal(strength) * factor
        corrected = round_decimal(corrected, precision)
        
        return CalculationResult(
            value=corrected,
            unit='MPa',
            precision=precision,
            formula='fc = fc实测 × η',
            description=f'修正强度 = {strength}MPa × {factor}',
        )
    
    @staticmethod
    def flexural_strength(load: Number, span: Number, width: Number, height: Number, precision: int = 1) -> CalculationResult:
        """
        抗折强度计算
        
        公式: ff = F × L / (b × h²)
        ff: 抗折强度 (MPa)
        F: 破坏荷载 (N)
        L: 支座间距 (mm)
        b: 试件宽度 (mm)
        h: 试件高度 (mm)
        
        :param load: 破坏荷载 (kN)
        :param span: 支座间距 (mm)
        :param width: 试件宽度 (mm)
        :param height: 试件高度 (mm)
        :param precision: 结果精度
        :return: 抗折强度结果
        """
        load_n = to_decimal(load) * 1000  # kN转N
        span_dec = to_decimal(span)
        width_dec = to_decimal(width)
        height_dec = to_decimal(height)
        
        strength = FormulaLibrary.safe_divide(
            load_n * span_dec,
            width_dec * height_dec ** 2,
            precision
        )
        
        return CalculationResult(
            value=strength,
            unit='MPa',
            precision=precision,
            formula='ff = F × L / (b × h²)',
            description=f'抗折强度 = {load}kN × {span}mm / ({width}mm × {height}mm²)',
        )


class SteelFormula(FormulaLibrary):
    """钢筋检测计算公式"""
    
    @staticmethod
    def yield_strength(yield_load: Number, area: Number, precision: int = 0) -> CalculationResult:
        """
        屈服强度计算
        
        公式: ReL = Fy / S0
        ReL: 屈服强度 (MPa)
        Fy: 屈服荷载 (N)
        S0: 原始横截面积 (mm²)
        
        :param yield_load: 屈服荷载 (kN)
        :param area: 横截面积 (mm²)
        :param precision: 结果精度
        :return: 屈服强度结果
        """
        load_n = to_decimal(yield_load) * 1000  # kN转N
        area_dec = to_decimal(area)
        
        strength = FormulaLibrary.safe_divide(load_n, area_dec, precision)
        
        return CalculationResult(
            value=strength,
            unit='MPa',
            precision=precision,
            formula='ReL = Fy × 1000 / S0',
            description=f'屈服强度 = {yield_load}kN × 1000 / {area}mm²',
        )
    
    @staticmethod
    def tensile_strength(max_load: Number, area: Number, precision: int = 0) -> CalculationResult:
        """
        抗拉强度计算
        
        公式: Rm = Fm / S0
        Rm: 抗拉强度 (MPa)
        Fm: 最大荷载 (N)
        S0: 原始横截面积 (mm²)
        
        :param max_load: 最大荷载 (kN)
        :param area: 横截面积 (mm²)
        :param precision: 结果精度
        :return: 抗拉强度结果
        """
        load_n = to_decimal(max_load) * 1000  # kN转N
        area_dec = to_decimal(area)
        
        strength = FormulaLibrary.safe_divide(load_n, area_dec, precision)
        
        return CalculationResult(
            value=strength,
            unit='MPa',
            precision=precision,
            formula='Rm = Fm × 1000 / S0',
            description=f'抗拉强度 = {max_load}kN × 1000 / {area}mm²',
        )
    
    @staticmethod
    def elongation(original_length: Number, final_length: Number, precision: int = 1) -> CalculationResult:
        """
        断后伸长率计算
        
        公式: A = (Lu - L0) / L0 × 100
        A: 断后伸长率 (%)
        Lu: 断后标距 (mm)
        L0: 原始标距 (mm)
        
        :param original_length: 原始标距 (mm)
        :param final_length: 断后标距 (mm)
        :param precision: 结果精度
        :return: 伸长率结果
        """
        l0 = to_decimal(original_length)
        lu = to_decimal(final_length)
        
        elongation = FormulaLibrary.percentage(lu - l0, l0, precision)
        
        return CalculationResult(
            value=elongation,
            unit='%',
            precision=precision,
            formula='A = (Lu - L0) / L0 × 100',
            description=f'伸长率 = ({final_length} - {original_length}) / {original_length} × 100',
        )
    
    @staticmethod
    def cross_section_area(diameter: Number, precision: int = 1) -> CalculationResult:
        """
        圆形钢筋横截面积
        
        公式: S = π × d² / 4
        
        :param diameter: 直径 (mm)
        :param precision: 结果精度
        :return: 横截面积结果
        """
        d = to_decimal(diameter)
        area = Decimal(str(math.pi)) * d ** 2 / 4
        area = round_decimal(area, precision)
        
        return CalculationResult(
            value=area,
            unit='mm²',
            precision=precision,
            formula='S = π × d² / 4',
            description=f'横截面积 = π × {diameter}² / 4',
        )
    
    @staticmethod
    def strength_ratio(yield_strength: Number, tensile_strength: Number, precision: int = 2) -> CalculationResult:
        """
        强屈比计算
        
        公式: R = Rm / ReL
        要求: R ≥ 1.25 (抗震要求)
        
        :param yield_strength: 屈服强度 (MPa)
        :param tensile_strength: 抗拉强度 (MPa)
        :param precision: 结果精度
        :return: 强屈比结果
        """
        ratio = FormulaLibrary.safe_divide(tensile_strength, yield_strength, precision)
        
        return CalculationResult(
            value=ratio,
            unit='',
            precision=precision,
            formula='R = Rm / ReL',
            description=f'强屈比 = {tensile_strength}MPa / {yield_strength}MPa',
        )


class AsphaltFormula(FormulaLibrary):
    """沥青检测计算公式"""
    
    @staticmethod
    def density(mass: Number, volume: Number, precision: int = 3) -> CalculationResult:
        """
        密度计算
        
        公式: ρ = m / V
        
        :param mass: 质量 (g)
        :param volume: 体积 (cm³)
        :param precision: 结果精度
        :return: 密度结果
        """
        density = FormulaLibrary.safe_divide(mass, volume, precision)
        
        return CalculationResult(
            value=density,
            unit='g/cm³',
            precision=precision,
            formula='ρ = m / V',
            description=f'密度 = {mass}g / {volume}cm³',
        )
    
    @staticmethod
    def penetration(value: Number, precision: int = 1) -> CalculationResult:
        """
        针入度（直接测量值）
        
        :param value: 针入度值 (0.1mm)
        :param precision: 结果精度
        :return: 针入度结果
        """
        pen = round_decimal(to_decimal(value), precision)
        
        return CalculationResult(
            value=pen,
            unit='0.1mm',
            precision=precision,
            formula='直接测量',
            description='针入度标准条件: 25°C, 5s, 100g',
        )
    
    @staticmethod
    def softening_point(value: Number, precision: int = 1) -> CalculationResult:
        """
        软化点（直接测量值）
        
        :param value: 软化点值 (°C)
        :param precision: 结果精度
        :return: 软化点结果
        """
        sp = round_decimal(to_decimal(value), precision)
        
        return CalculationResult(
            value=sp,
            unit='°C',
            precision=precision,
            formula='直接测量',
            description='环球法软化点',
        )
    
    @staticmethod
    def ductility(value: Number, precision: int = 0) -> CalculationResult:
        """
        延度（直接测量值）
        
        :param value: 延度值 (cm)
        :param precision: 结果精度
        :return: 延度结果
        """
        duct = round_decimal(to_decimal(value), precision)
        
        return CalculationResult(
            value=duct,
            unit='cm',
            precision=precision,
            formula='直接测量',
            description='延度标准条件: 25°C, 5cm/min',
        )


class SoilFormula(FormulaLibrary):
    """土工试验计算公式"""
    
    @staticmethod
    def water_content(wet_mass: Number, dry_mass: Number, precision: int = 1) -> CalculationResult:
        """
        含水率计算
        
        公式: w = (m - md) / md × 100
        w: 含水率 (%)
        m: 湿土质量 (g)
        md: 干土质量 (g)
        
        :param wet_mass: 湿土质量 (g)
        :param dry_mass: 干土质量 (g)
        :param precision: 结果精度
        :return: 含水率结果
        """
        wet = to_decimal(wet_mass)
        dry = to_decimal(dry_mass)
        
        water_content = FormulaLibrary.percentage(wet - dry, dry, precision)
        
        return CalculationResult(
            value=water_content,
            unit='%',
            precision=precision,
            formula='w = (m - md) / md × 100',
            description=f'含水率 = ({wet_mass} - {dry_mass}) / {dry_mass} × 100',
        )
    
    @staticmethod
    def density(mass: Number, volume: Number, precision: int = 2) -> CalculationResult:
        """
        密度计算
        
        公式: ρ = m / V
        
        :param mass: 质量 (g)
        :param volume: 体积 (cm³)
        :param precision: 结果精度
        :return: 密度结果
        """
        density = FormulaLibrary.safe_divide(mass, volume, precision)
        
        return CalculationResult(
            value=density,
            unit='g/cm³',
            precision=precision,
            formula='ρ = m / V',
            description=f'密度 = {mass}g / {volume}cm³',
        )
    
    @staticmethod
    def dry_density(density: Number, water_content: Number, precision: int = 2) -> CalculationResult:
        """
        干密度计算
        
        公式: ρd = ρ / (1 + w)
        ρd: 干密度 (g/cm³)
        ρ: 密度 (g/cm³)
        w: 含水率
        
        :param density: 密度 (g/cm³)
        :param water_content: 含水率 (%)
        :param precision: 结果精度
        :return: 干密度结果
        """
        rho = to_decimal(density)
        w = to_decimal(water_content) / 100
        
        dry_density = FormulaLibrary.safe_divide(rho, 1 + w, precision)
        
        return CalculationResult(
            value=dry_density,
            unit='g/cm³',
            precision=precision,
            formula='ρd = ρ / (1 + w)',
            description=f'干密度 = {density}g/cm³ / (1 + {water_content}%)',
        )
    
    @staticmethod
    def compaction_degree(dry_density: Number, max_dry_density: Number, precision: int = 1) -> CalculationResult:
        """
        压实度计算
        
        公式: K = ρd / ρd,max × 100
        K: 压实度 (%)
        ρd: 干密度 (g/cm³)
        ρd,max: 最大干密度 (g/cm³)
        
        :param dry_density: 干密度 (g/cm³)
        :param max_dry_density: 最大干密度 (g/cm³)
        :param precision: 结果精度
        :return: 压实度结果
        """
        degree = FormulaLibrary.percentage(dry_density, max_dry_density, precision)
        
        return CalculationResult(
            value=degree,
            unit='%',
            precision=precision,
            formula='K = ρd / ρd,max × 100',
            description=f'压实度 = {dry_density}g/cm³ / {max_dry_density}g/cm³ × 100',
        )


class FormulaRegistry:
    """公式注册表"""
    
    _formulas = {
        # 混凝土公式
        'concrete_compressive': ConcreteFormula.compressive_strength,
        'concrete_strength_correction': ConcreteFormula.strength_correction,
        'concrete_flexural': ConcreteFormula.flexural_strength,
        
        # 钢筋公式
        'steel_yield': SteelFormula.yield_strength,
        'steel_tensile': SteelFormula.tensile_strength,
        'steel_elongation': SteelFormula.elongation,
        'steel_area': SteelFormula.cross_section_area,
        'steel_ratio': SteelFormula.strength_ratio,
        
        # 沥青公式
        'asphalt_density': AsphaltFormula.density,
        'asphalt_penetration': AsphaltFormula.penetration,
        'asphalt_softening': AsphaltFormula.softening_point,
        'asphalt_ductility': AsphaltFormula.ductility,
        
        # 土工公式
        'soil_water_content': SoilFormula.water_content,
        'soil_density': SoilFormula.density,
        'soil_dry_density': SoilFormula.dry_density,
        'soil_compaction': SoilFormula.compaction_degree,
        
        # 通用公式
        'average': FormulaLibrary.average,
        'std_dev': FormulaLibrary.standard_deviation,
        'max': FormulaLibrary.max_value,
        'min': FormulaLibrary.min_value,
        'range': FormulaLibrary.range_value,
        'percentage': FormulaLibrary.percentage,
        'safe_divide': FormulaLibrary.safe_divide,
    }
    
    @classmethod
    def get_formula(cls, name: str):
        """获取公式"""
        return cls._formulas.get(name)
    
    @classmethod
    def execute(cls, name: str, **kwargs) -> Optional[CalculationResult]:
        """执行公式"""
        formula = cls.get_formula(name)
        if formula:
            return formula(**kwargs)
        return None
    
    @classmethod
    def list_formulas(cls) -> dict:
        """列出所有公式"""
        return {
            'concrete': [
                {'name': 'concrete_compressive', 'description': '抗压强度计算', 'params': ['load', 'area']},
                {'name': 'concrete_strength_correction', 'description': '强度尺寸修正', 'params': ['size', 'strength']},
                {'name': 'concrete_flexural', 'description': '抗折强度计算', 'params': ['load', 'span', 'width', 'height']},
            ],
            'steel': [
                {'name': 'steel_yield', 'description': '屈服强度计算', 'params': ['yield_load', 'area']},
                {'name': 'steel_tensile', 'description': '抗拉强度计算', 'params': ['max_load', 'area']},
                {'name': 'steel_elongation', 'description': '断后伸长率计算', 'params': ['original_length', 'final_length']},
                {'name': 'steel_area', 'description': '横截面积计算', 'params': ['diameter']},
                {'name': 'steel_ratio', 'description': '强屈比计算', 'params': ['yield_strength', 'tensile_strength']},
            ],
            'asphalt': [
                {'name': 'asphalt_density', 'description': '密度计算', 'params': ['mass', 'volume']},
                {'name': 'asphalt_penetration', 'description': '针入度', 'params': ['value']},
                {'name': 'asphalt_softening', 'description': '软化点', 'params': ['value']},
                {'name': 'asphalt_ductility', 'description': '延度', 'params': ['value']},
            ],
            'soil': [
                {'name': 'soil_water_content', 'description': '含水率计算', 'params': ['wet_mass', 'dry_mass']},
                {'name': 'soil_density', 'description': '密度计算', 'params': ['mass', 'volume']},
                {'name': 'soil_dry_density', 'description': '干密度计算', 'params': ['density', 'water_content']},
                {'name': 'soil_compaction', 'description': '压实度计算', 'params': ['dry_density', 'max_dry_density']},
            ],
            'general': [
                {'name': 'average', 'description': '平均值', 'params': ['values']},
                {'name': 'std_dev', 'description': '标准差', 'params': ['values']},
                {'name': 'max', 'description': '最大值', 'params': ['values']},
                {'name': 'min', 'description': '最小值', 'params': ['values']},
                {'name': 'range', 'description': '极差', 'params': ['values']},
                {'name': 'percentage', 'description': '百分比', 'params': ['value', 'total']},
            ],
        }