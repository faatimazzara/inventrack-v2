class InventoryError(Exception):
    """Business error that can be displayed safely to a CLI user."""


class ValidationError(InventoryError):
    pass


class DuplicateProductError(InventoryError):
    pass


class ProductNotFoundError(InventoryError):
    pass


class InsufficientStockError(InventoryError):
    pass


class AuthenticationError(InventoryError):
    pass


class AuthorizationError(InventoryError):
    pass


class StorageError(InventoryError):
    pass
