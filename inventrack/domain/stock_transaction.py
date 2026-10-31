from dataclasses import asdict, dataclass
from uuid import uuid4

from inventrack.domain.enums import StockMovementType
from inventrack.domain.product import utc_now


@dataclass(frozen=True, slots=True)
class StockTransaction:
    transaction_id: str
    product_id: str
    movement_type: StockMovementType
    before: int
    after: int
    quantity: int
    reason: str
    actor: str
    timestamp: str

    @classmethod
    def create(cls, product_id: str, movement_type: StockMovementType,
               before: int, after: int, reason: str, actor: str) -> "StockTransaction":
        return cls(uuid4().hex, product_id, movement_type, before, after,
                   abs(after - before), reason, actor, utc_now())

    def to_dict(self) -> dict:
        return {**asdict(self), "movement_type": self.movement_type.value}

    @classmethod
    def from_dict(cls, data: dict) -> "StockTransaction":
        return cls(**{**data, "movement_type": StockMovementType(data["movement_type"])})
