from __future__ import annotations

from decimal import Decimal
from typing import Any

from .models import JudgmentRule, TestResult


def judge_result(test_result: TestResult) -> str:
    if test_result.rounded_value is None:
        return 'na'

    rules = JudgmentRule.objects.filter(
        test_parameter=test_result.parameter,
    )

    task = test_result.task
    grade = getattr(task.sample, 'grade', '')
    if grade:
        rules = rules.filter(grade=grade)

    rule = rules.first()
    if not rule:
        return 'na'

    value = test_result.rounded_value
    if rule.min_value is not None and value < rule.min_value:
        return 'unqualified'
    if rule.max_value is not None and value > rule.max_value:
        return 'unqualified'
    return 'qualified'


def evaluate_concrete_strength(
    results: list[Decimal],
    grade: str,
) -> dict[str, Any]:
    """GB/T 50107 混凝土强度统计评定。"""
    n = len(results)
    if n == 0:
        return {'qualified': False, 'method': None, 'reason': '无检测数据'}

    fcu_k = _parse_grade_value(grade)
    if fcu_k is None:
        return {'qualified': False, 'method': None, 'reason': '无法解析强度等级'}

    mean_val = sum(results) / n
    min_val = min(results)

    if n >= 10:
        return _statistical_evaluation(results, n, mean_val, min_val, fcu_k)
    return _non_statistical_evaluation(mean_val, min_val, fcu_k)


def _statistical_evaluation(
    results: list[Decimal],
    n: int,
    mean_val: Decimal,
    min_val: Decimal,
    fcu_k: Decimal,
) -> dict[str, Any]:
    # GB/T 50107-2010 §4.1 统计方法
    variance = sum((x - mean_val) ** 2 for x in results) / (n - 1)
    s = variance ** Decimal('0.5')
    lambda_1 = Decimal('1.15') if n < 25 else Decimal('1.0')

    cond1 = mean_val >= fcu_k + lambda_1 * s
    cond2 = min_val >= fcu_k - Decimal('0.06') * fcu_k
    return {
        'qualified': bool(cond1 and cond2),
        'method': 'statistical',
        'mean': float(mean_val),
        'std_dev': float(s),
        'min': float(min_val),
        'fcu_k': float(fcu_k),
    }


def _non_statistical_evaluation(
    mean_val: Decimal,
    min_val: Decimal,
    fcu_k: Decimal,
) -> dict[str, Any]:
    # GB/T 50107-2010 §4.2 非统计方法
    cond1 = mean_val >= Decimal('1.15') * fcu_k
    cond2 = min_val >= Decimal('0.95') * fcu_k
    return {
        'qualified': bool(cond1 and cond2),
        'method': 'non_statistical',
        'mean': float(mean_val),
        'min': float(min_val),
        'fcu_k': float(fcu_k),
    }


def _parse_grade_value(grade: str) -> Decimal | None:
    """Extract numeric MPa value from grade string like 'C30'."""
    cleaned = grade.upper().lstrip('C')
    try:
        return Decimal(cleaned)
    except Exception:
        return None


def evaluate_rebar_mechanics(
    results: dict[str, Decimal],
    spec: dict[str, Decimal],
) -> dict[str, Any]:
    """GB 1499.2 钢筋力学性能评定。"""
    checks = {}

    if 'yield_strength' in results and 'yield_min' in spec:
        checks['yield'] = results['yield_strength'] >= spec['yield_min']

    if 'tensile_strength' in results and 'tensile_min' in spec:
        checks['tensile'] = results['tensile_strength'] >= spec['tensile_min']

    if 'elongation' in results and 'elongation_min' in spec:
        checks['elongation'] = results['elongation'] >= spec['elongation_min']

    # GB 1499.2: 强屈比 ≥ 1.25
    if 'yield_strength' in results and 'tensile_strength' in results:
        ratio = results['tensile_strength'] / results['yield_strength']
        checks['strength_ratio'] = ratio >= Decimal('1.25')

    return {
        'qualified': all(checks.values()) if checks else False,
        'checks': {k: bool(v) for k, v in checks.items()},
    }
