from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity.record import Record


class RecordError(Exception):
    """Raised when there us an error during record transaction"""


class RecordDoesNotExistError(LookupError, Exception):
    """Raised when record lookup fails."""


class RecordService:
    def get_record(self, id: int) -> "Record":
        raise NotImplementedError

    def create_record(self, record: "Record") -> None:
        raise NotImplementedError

    def update_record(self, id: int) -> "Record":
        raise NotImplementedError


class InMemoryRecordService(RecordService):
    def __init__(self) -> None:
        self.data: dict[int, "Record"] = {}

    def get_record(self, id: int) -> "Record":
        try:
            record = self.data[id]
        except KeyError as e:
            raise RecordDoesNotExistError from e

        return record

    def create_record(self, record: "Record") -> None:
        return super().create_record(record)

    def update_record(self, id: int) -> "Record":
        return super().update_record(id)
