"""Derived academic figures (GPA, credits, per-term grouping, schedule clashes).

These are computed in the web layer from the enrollment records the API
already returns (``EnrollmentWithOffering``: each carries its offering, course,
and term). They are *presentation* aggregations — a production system would
likely expose a ``/students/{id}/academic-summary`` endpoint so this domain
logic lives in the API service; kept here to leave the API untouched.

The grade scale is 0-10 (matches the seed data); GPA is credit-weighted.
Enrollment records are plain dicts (parsed JSON), so we index by key.
"""

from datetime import time
from typing import Any

Enrollment = dict[str, Any]
Offering = dict[str, Any]


def _credits(enr: Enrollment) -> int:
    return int(enr["offering"]["course"]["credits"])


def cumulative_gpa(enrollments: list[Enrollment]) -> float | None:
    """Credit-weighted average grade over COMPLETED, graded enrollments."""
    graded = [e for e in enrollments if e["status"] == "COMPLETED" and e["grade"] is not None]
    total_credits = sum(_credits(e) for e in graded)
    if not total_credits:
        return None
    weighted = sum(float(e["grade"]) * _credits(e) for e in graded)
    return round(weighted / total_credits, 2)


def credits_earned(enrollments: list[Enrollment]) -> int:
    return sum(_credits(e) for e in enrollments if e["status"] == "COMPLETED")


def credits_in_progress(enrollments: list[Enrollment]) -> int:
    return sum(_credits(e) for e in enrollments if e["status"] == "REGISTERED")


def completed_by_term(enrollments: list[Enrollment]) -> list[dict[str, Any]]:
    """Group COMPLETED enrollments by term (newest first), with per-term GPA."""
    groups: dict[str, dict[str, Any]] = {}
    for enr in enrollments:
        if enr["status"] != "COMPLETED":
            continue
        term = enr["offering"]["term"]
        bucket = groups.setdefault(term["code"], {"term": term, "rows": []})
        bucket["rows"].append(enr)

    result: list[dict[str, Any]] = []
    for bucket in groups.values():
        rows = bucket["rows"]
        result.append(
            {
                "term": bucket["term"],
                "rows": rows,
                "credits": sum(_credits(r) for r in rows),
                "gpa": cumulative_gpa(rows),
            }
        )
    result.sort(key=lambda g: g["term"]["code"], reverse=True)
    return result


def _as_time(value: str) -> time:
    return time.fromisoformat(value)


def _overlaps(a_start: time, a_end: time, b_start: time, b_end: time) -> bool:
    return a_start < b_end and b_start < a_end


def find_clash(offering: Offering, registered: list[Offering]) -> Offering | None:
    """Return a registered offering that clashes (same day, overlapping time)
    with ``offering``, or None. Mirrors the server-side check so the UI can warn
    before the API rejects the registration with a 409."""
    for other in registered:
        if other["id"] == offering["id"]:
            continue
        if other["day_of_week"] == offering["day_of_week"] and _overlaps(
            _as_time(offering["start_time"]),
            _as_time(offering["end_time"]),
            _as_time(other["start_time"]),
            _as_time(other["end_time"]),
        ):
            return other
    return None
