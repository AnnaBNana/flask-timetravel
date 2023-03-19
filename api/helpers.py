from typing import TYPE_CHECKING, Any

from api.exceptions import ResourceKeyInvalidError

if TYPE_CHECKING:
    from entity.record import Record

def validate_record_id(id: str) -> int:
    try:
        int_id = int(id)
        assert int_id > 0
    except (ValueError, AssertionError) as e:
        raise ResourceKeyInvalidError from e

    return int_id


def update_data(data: dict[str, Any], changes: dict[str, str]) -> None:
    for key, value in changes.items():
        if value:
            data[key] = value
        else:
            data.pop(key, None)
