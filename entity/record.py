from datetime import datetime
from typing import Any


class Record:
    """Record class models record for storage."""

    def __init__(self, slug: str, data: dict[str, str], **kwargs: Any) -> None:
        """Initialize an object of type record with optional values for v2 versioning."""
        self.slug = slug
        self.data = data
        self.version = kwargs.get("version")
        self.timestamp = kwargs.get("timestamp", datetime.now())
