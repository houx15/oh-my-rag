"""Typed, local arithmetic utilities; not yet a natural-language answer route.

Independent engineering implementation, not attributed to a paper. A derived
number is never an exact source quotation or verification of its premise.
"""
from decimal import Decimal, localcontext
import re

# Dimension, multiplier to its base unit. No currency exchange or world data.
UNITS = {
    "元": ("CNY", Decimal("1")), "万元": ("CNY", Decimal("10000")),
    "亿元": ("CNY", Decimal("100000000")),
    "平方米": ("area", Decimal("1")), "万平方米": ("area", Decimal("10000")),
    "克": ("mass", Decimal("1")), "毫克": ("mass", Decimal("0.001")),
    "千克": ("mass", Decimal("1000")),
}


def _quantity(value, unit, provenance, scope):
    if not isinstance(value, str) or len(value) > 80 or not re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        raise ValueError("supply one explicit decimal string, without ambiguous separators")
    if unit not in UNITS:
        raise ValueError("unsupported unit")
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError("operand provenance required")
    if scope not in ("user_premise", "document_statement"):
        raise ValueError("explicit premise scope required")
    return Decimal(value)


def convert(value, source_unit, target_unit, *, provenance, scope):
    number = _quantity(value, source_unit, provenance, scope)
    if target_unit not in UNITS or UNITS[source_unit][0] != UNITS[target_unit][0]:
        raise ValueError("incompatible or unknown units")
    with localcontext() as ctx:
        ctx.prec = 100
        result = number * UNITS[source_unit][1] / UNITS[target_unit][1]
    return {"operation": "unit_conversion", "value": format(result, "f"), "unit": target_unit,
            "operand": {"value": value, "unit": source_unit, "provenance": provenance},
            "scope": scope, "derived": True, "premise_verified": False}


def compare(left, right):
    """Compare explicit operands only when entity, period and measure match.

    Each operand supplies value/unit/provenance/scope/entity/period/measure.
    This deliberately rejects cross-entity or underspecified comparisons; it is
    a narrow diagnostic utility, not an automatic table aggregation system.
    """
    for field in ("entity", "period", "measure", "scope"):
        if not isinstance(left.get(field), str) or not left[field] or left[field] != right.get(field):
            raise ValueError("comparison scopes must be explicit and identical")
    l = _quantity(left["value"], left["unit"], left["provenance"], left["scope"])
    converted = convert(right["value"], right["unit"], left["unit"],
                        provenance=right["provenance"], scope=right["scope"])
    r = Decimal(converted["value"])
    return {"operation": "comparison", "relation": "equal" if l == r else ("less" if l < r else "greater"),
            "operands": [dict(left), dict(right)], "derived": True, "premise_verified": False}
