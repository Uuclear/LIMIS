from __future__ import annotations


def calc_compressive_strength(
    load_kn: float,
    area_mm2: float,
    correction_factor: float = 1.0,
) -> float:
    # GB/T 50081-2019 §6.0.4: f = F / A × δ
    if area_mm2 <= 0:
        raise ValueError('area_mm2 must be positive')
    return load_kn * 1000 / area_mm2 * correction_factor


def calc_flexural_strength(
    load_kn: float,
    span_mm: float,
    width_mm: float,
    height_mm: float,
) -> float:
    # GB/T 50081-2019 §7.0.4: f = F·L / (b·h²)
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError('width_mm and height_mm must be positive')
    force_n = load_kn * 1000
    return force_n * span_mm / (width_mm * height_mm ** 2)


def calc_average_strength(
    values: list[float],
    allow_discard: bool = True,
) -> float:
    """GB/T 50081-2019 取平均值，支持异常值剔除。

    三个试件取平均: 若最大值或最小值与中间值之差超过中间值的15%，
    则剔除该值；若两者均超过15%，则该组试验无效。
    """
    if not values:
        raise ValueError('values must not be empty')

    if len(values) != 3 or not allow_discard:
        return sum(values) / len(values)

    sorted_vals = sorted(values)
    low, mid, high = sorted_vals

    if mid == 0:
        return sum(values) / len(values)

    low_dev = abs(mid - low) / mid
    high_dev = abs(high - mid) / mid

    if low_dev > 0.15 and high_dev > 0.15:
        raise ValueError('最大值与最小值均超过中间值15%，该组试验无效')

    if low_dev > 0.15:
        return (mid + high) / 2
    if high_dev > 0.15:
        return (low + mid) / 2

    return sum(values) / len(values)
