class BaseAPIException(Exception):
    """Base exception for all API errors"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(BaseAPIException):
    def __init__(self, entity_name: str, identifier: str):
        message = f"{entity_name} not found with identifier: {identifier}"
        super().__init__(message)


class ConflictError(BaseAPIException):
    pass
