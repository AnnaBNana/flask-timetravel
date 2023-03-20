from datetime import datetime


class Record:
    def __init__(self, slug: str, data: dict[str, str], **kwargs) -> None:
        self.slug = slug
        self.data = data
        self.version = kwargs.get("version")
        self.timestamp = kwargs.get("timestamp", datetime.now())
