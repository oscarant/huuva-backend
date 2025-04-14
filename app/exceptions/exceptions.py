class NotFoundError(Exception):
    """Exception raised when an entity is not found."""

    def __init__(self, entity_name: str, identifier: str):
        self.entity_name = entity_name
        self.identifier = identifier
        super().__init__(f"{entity_name} not found with identifier: {identifier}")


class ConflictError(Exception):
    """Exception raised when there is a conflict, such as a duplicate entry."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
