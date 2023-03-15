from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity.record import Record


class RecordError(Exception):
    """Raised when there us an error during record transaction"""


class RecordDoesNotExistError(LookupError, RecordError):
    """Raised when record lookup fails."""


class RecordAlreadyExistsError(RecordError):
    """Raised when record exists."""


class RecordService:
    def get_record(self, id: int) -> "Record":
        raise NotImplementedError

    def create_record(self, record: "Record") -> None:
        raise NotImplementedError

    def update_record(self, id: int, data: dict[str, str]) -> "Record":
        raise NotImplementedError


class InMemoryRecordService(RecordService):
    data: dict[int, "Record"] = {}

    @classmethod
    def get_record(cls, id: int) -> "Record":
        print(cls.data)
        try:
            record = cls.data[id]
        except KeyError as e:
            raise RecordDoesNotExistError from e

        return record

    @classmethod
    def create_record(cls, record: "Record") -> None:
        if record.id in cls.data:
            raise RecordAlreadyExistsError
        else:
            cls.data[record.id] = record
        
        print(cls.data)

    @classmethod
    def update_record(cls, id: int, data: dict[str, str]) -> "Record":
        entry = cls.data[id]

        for key, value in data.items():
            if value:
                entry.data[key] = value
            else:
                entry.data.pop(key, None)

        return entry