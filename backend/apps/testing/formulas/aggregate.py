from __future__ import annotations


def calc_fineness_modulus(sieve_residues_pct: list[float]) -> float:
    """JGJ 52 §7.3 砂的细度模数计算。

    sieve_residues_pct: 各筛累计筛余百分比, 依次为
    4.75mm, 2.36mm, 1.18mm, 0.60mm, 0.30mm, 0.15mm
    Mx = (A2+A3+A4+A5+A6 - 5*A1) / (100 - A1)
    """
    if len(sieve_residues_pct) != 6:
        raise ValueError('需要6个筛档的累计筛余百分比')

    a1, a2, a3, a4, a5, a6 = sieve_residues_pct
    denominator = 100 - a1
    if denominator == 0:
        raise ValueError('4.75mm筛累计筛余不能为100%')
    return (a2 + a3 + a4 + a5 + a6 - 5 * a1) / denominator


def calc_mud_content(
    dry_weight_before: float,
    dry_weight_after: float,
) -> float:
    # JGJ 52 §7.7: 含泥量 = (烘干前 - 烘干后) / 烘干前 × 100%
    if dry_weight_before <= 0:
        raise ValueError('dry_weight_before must be positive')
    return (dry_weight_before - dry_weight_after) / dry_weight_before * 100


def calc_crushing_value(
    load_kn: float,
    sample_weight: float,
    residue_weight: float,
) -> float:
    # JGJ 52 §7.13: 压碎指标 = (装入量 - 筛余量) / 装入量 × 100%
    if sample_weight <= 0:
        raise ValueError('sample_weight must be positive')
    _ = load_kn  # recorded for traceability, not used in formula
    return (sample_weight - residue_weight) / sample_weight * 100
