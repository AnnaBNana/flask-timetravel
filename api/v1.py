import jsonpickle
from flask import Blueprint, request

from api.records import API
from service.record.v1 import SqliteRecordService

v1 = Blueprint("v1", __name__, url_prefix="/v1")
api = API(SqliteRecordService())


@v1.route("/records/<id>", methods=["GET"])
def get_record(id: str) -> str:
    """Get record by id, return record or 404."""
    record = api.get_records(id)
    return jsonpickle.encode(record)


@v1.route("/records/<id>", methods=["POST"])
def post_record(id: str) -> tuple[str, int]:
    """Create record, returns empty response in success case."""
    data = request.json
    api.post_records(id, data)
    return ("", 204)
