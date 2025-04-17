class BaseAPIError(Exception):
    """Base exception for all API errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(BaseAPIError):
    def __init__(self, entity_name: str, identifier: str) -> None:
        message = f"{entity_name} not found with identifier: {identifier}"
        super().__init__(message)


class ConflictError(BaseAPIError):
    def __init__(self, entity_name: str, identifier: str) -> None:
        message = f"Conflict with {entity_name} with identifier: {identifier}"
        super().__init__(message)
