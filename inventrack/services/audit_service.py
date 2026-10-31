from inventrack.auth.access_control import AccessControl
from inventrack.domain.audit_event import AuditEvent
from inventrack.domain.enums import Role
from inventrack.domain.user import User


class AuditService:
    def __init__(self, access: AccessControl) -> None:
        self.access = access
        self._events: list[AuditEvent] = []

    def record(self, actor: User, action: str, details: str) -> None:
        self._events.append(AuditEvent.create(actor.username, action, details))

    def list_events(self, actor: User, limit: int = 100) -> list[AuditEvent]:
        self.access.require(actor, Role.ADMIN, Role.MANAGER)
        return list(reversed(self._events[-limit:]))

    def all_for_storage(self) -> list[dict]:
        return [event.to_dict() for event in self._events]

    def load(self, data: list[dict]) -> None:
        self._events = [AuditEvent.from_dict(item) for item in data]
