"""Shared Jinja2 environment + small presentation filters."""

from datetime import date, datetime
from pathlib import Path

from fastapi.templating import Jinja2Templates

_TEMPLATE_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))


def _hhmm(value: str) -> str:
    """'08:00:00' -> '08:00'."""
    return value[:5] if isinstance(value, str) else value


def _day(value: str) -> str:
    names = {
        "MON": "Monday",
        "TUE": "Tuesday",
        "WED": "Wednesday",
        "THU": "Thursday",
        "FRI": "Friday",
        "SAT": "Saturday",
        "SUN": "Sunday",
    }
    return names.get(value, value)


def _nice_date(value: str) -> str:
    """ISO date/datetime string -> 'Sep 01, 2025'."""
    if not isinstance(value, str):
        return str(value)
    try:
        parsed: date = datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            parsed = date.fromisoformat(value[:10])
        except ValueError:
            return value
    return parsed.strftime("%b %d, %Y")


templates.env.filters["hhmm"] = _hhmm
templates.env.filters["day"] = _day
templates.env.filters["nice_date"] = _nice_date
