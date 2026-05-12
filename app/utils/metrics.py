import math


def format_count(value: int | float | None) -> str:
    if value is None:
        return "Not available"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "Not available"


def format_percent(value: int | float | None) -> str:
    if value is None:
        return "Not available"
    try:
        if math.isnan(float(value)):
            return "Not available"
        return f"{float(value):.1%}"
    except (TypeError, ValueError):
        return "Not available"


def format_number(value: int | float | None) -> str:
    if value is None:
        return "Not available"
    try:
        return f"{float(value):,.3f}"
    except (TypeError, ValueError):
        return "Not available"
