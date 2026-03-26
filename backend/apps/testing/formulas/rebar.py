from __future__ import annotations


def calc_yield_strength(force_kn: float, area_mm2: float) -> float:
    # GB 1499.2: ReL = F / A
    if area_mm2 <= 0:
        raise ValueError('area_mm2 must be positive')
    return force_kn * 1000 / area_mm2


def calc_tensile_strength(force_kn: float, area_mm2: float) -> float:
    # GB 1499.2: Rm = F / A
    if area_mm2 <= 0:
        raise ValueError('area_mm2 must be positive')
    return force_kn * 1000 / area_mm2


def calc_elongation(original_length: float, final_length: float) -> float:
    # GB/T 228.1: A = (Lu - Lo) / Lo × 100%
    if original_length <= 0:
        raise ValueError('original_length must be positive')
    return (final_length - original_length) / original_length * 100


def calc_weight_deviation(
    actual_weight: float,
    nominal_weight: float,
) -> float:
    # GB 1499.2 §7.4: 偏差 = (实际 - 公称) / 公称 × 100%
    if nominal_weight <= 0:
        raise ValueError('nominal_weight must be positive')
    return (actual_weight - nominal_weight) / nominal_weight * 100
