import jsonpickle
from typing import Any

from flask import Blueprint, request

from api.records_api import API
from service.record import SqliteRecordService


v1 = Blueprint("v1", __name__, url_prefix="/v1")
api = API(SqliteRecordService())


@v1.route("/records/<id>", methods=["GET"])
def get_record(id: str) -> str:
    record = api.get_records(id)
    return jsonpickle.encode(record)


@v1.route("/records/<id>", methods=["POST"])
def post_record(id: str) -> tuple[str, int]:
    data = request.json
    api.post_records(id, data)
    return ("", 204)
