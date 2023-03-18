from werkzeug.exceptions import HTTPException


class ResourceNotFound(HTTPException):
    """Raised when resource not found."""

    code = 404


class ResourceKeyInvalidError(HTTPException):
    """Raised for invalid record key."""

    code = 400
