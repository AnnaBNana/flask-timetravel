from typing import Any


def update_data(data: dict[str, Any], changes: dict[str, str | None]) -> None:
    """Update data dict in place according to changes dict."""
    for key, value in changes.items():
        if value:
            data[key] = value
        else:
            data.pop(key, None)
