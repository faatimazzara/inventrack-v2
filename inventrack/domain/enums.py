from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    MANAGER = "manager"
    DEVELOPER = "developer"


class StockMovementType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"
