from dataclasses import asdict, dataclass
from uuid import uuid4

from inventrack.domain.product import utc_now


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    actor: str
    action: str
    details: str
    timestamp: str

    @classmethod
    def create(cls, actor: str, action: str, details: str) -> "AuditEvent":
        return cls(uuid4().hex, actor, action, details, utc_now())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEvent":
        return cls(**data)
