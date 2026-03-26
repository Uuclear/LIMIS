from __future__ import annotations


def calc_mortar_flexural(load_kn: float, span_mm: float = 100.0) -> float:
    # GB/T 17671 §9.3: Rf = 1.5·F·L / b³  (b = 40mm)
    b = 40.0
    return 1.5 * load_kn * 1000 * span_mm / (b ** 3)


def calc_mortar_compressive(load_kn: float, area_mm2: float = 1600.0) -> float:
    # GB/T 17671 §9.4: Rc = F / A  (A = 40×40 = 1600mm²)
    if area_mm2 <= 0:
        raise ValueError('area_mm2 must be positive')
    return load_kn * 1000 / area_mm2


def calc_cement_strength(
    flexural_values: list[float],
    compressive_values: list[float],
) -> dict:
    """GB/T 17671 水泥强度计算。

    抗折: 3个试件取平均，若一个偏差>±10%则剔除取二均值，
    若两个均超差则无效。
    抗压: 6个试件去掉最大最小值取四均值。
    """
    flexural = _calc_flexural_average(flexural_values)
    compressive = _calc_compressive_average(compressive_values)
    return {
        'flexural_strength': flexural,
        'compressive_strength': compressive,
    }


def _calc_flexural_average(values: list[float]) -> float:
    if len(values) != 3:
        return sum(values) / len(values) if values else 0.0

    mean = sum(values) / 3
    if mean == 0:
        return 0.0

    outliers = [v for v in values if abs(v - mean) / mean > 0.10]
    if len(outliers) >= 2:
        raise ValueError('两个以上抗折值偏差超过10%，该组无效')
    if len(outliers) == 1:
        remaining = [v for v in values if v not in outliers]
        return sum(remaining) / len(remaining)
    return mean


def _calc_compressive_average(values: list[float]) -> float:
    """6个值去掉最大最小取四均值。"""
    if len(values) < 3:
        return sum(values) / len(values) if values else 0.0
    if len(values) == 6:
        sorted_v = sorted(values)
        return sum(sorted_v[1:5]) / 4
    return sum(values) / len(values)
