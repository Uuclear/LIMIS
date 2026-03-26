"""
Rounding utilities per GB/T 8170 — 数值修约规则与极限数值的表示和判定.
Implements the "四舍六入五成双" (round-half-to-even) rule.
"""
from __future__ import annotations

import math
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from typing import Union

Numeric = Union[int, float, str, Decimal]


def round_half_even(value: Numeric | None, precision: int = 0) -> Decimal | None:
    if value is None:
        return None

    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None

    if d.is_nan() or d.is_infinite():
        return None

    quant = Decimal(10) ** -precision
    return d.quantize(quant, rounding=ROUND_HALF_EVEN)


def round_to_digits(value: Numeric | None, significant_digits: int) -> Decimal | None:
    if value is None or significant_digits < 1:
        return None

    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None

    if d.is_nan() or d.is_infinite() or d == 0:
        return Decimal(0) if d == 0 else None

    exponent = d.adjusted()
    precision = significant_digits - 1 - exponent

    return round_half_even(d, precision)
