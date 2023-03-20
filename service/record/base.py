from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from entity.record import Record


class RecordError(Exception):
    """Raised when there us an error during record transaction."""


class RecordDoesNotExistError(LookupError, RecordError):
    """Raised when record lookup fails."""


class RecordAlreadyExistsError(RecordError):
    """Raised when record exists."""


class RecordService:
    """A base class for record services."""

    def get_record(self, slug: str, **kwargs: Any) -> "Record":
        """Get record by unique slug."""
        raise NotImplementedError

    def create_record(self, record: "Record", **kwargs: Any) -> None:
        """Create record from record data."""
        raise NotImplementedError

    def update_record(self, slug: str, data: dict[str, Any], **kwargs: Any) -> "Record":
        """Update record data according to data values."""
        raise NotImplementedError

    def get_versions(self, slug: str, **kwargs: Any) -> list[int]:
        """Get versions for slug."""
        raise NotImplementedError
