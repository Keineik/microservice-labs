from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict, computed_field


def _as_aware(dt: datetime) -> datetime:
    """Treat naive datetimes (e.g. from SQLite) as UTC so comparisons are safe."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


class TermOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    starts_on: date
    ends_on: date
    registration_starts_at: datetime
    registration_ends_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_registration_open(self) -> bool:
        now = datetime.now(UTC)
        return _as_aware(self.registration_starts_at) <= now <= _as_aware(self.registration_ends_at)
