import jsonpickle
from flask import Blueprint, request

from api.get_records import get_records
from api.post_records import post_records


new_api = Blueprint("api", __name__, url_prefix="/api/v1")


@new_api.route("/records/<id>", methods=["GET"])
def get_record(id: str) -> str:
    record = get_records(id)
    return jsonpickle.encode(record)


@new_api.route("/records/<id>", methods=["POST"])
def post_record(id: str) -> str:
    data = request.json
    record = post_records(id, data)
    return jsonpickle.encode(record)
