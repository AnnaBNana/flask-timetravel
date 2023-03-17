import jsonpickle
from flask import Blueprint, request

from api.get_records import get_records
from api.post_records import post_records


v1 = Blueprint("v1", __name__, url_prefix="/v1")


@v1.route("/records/<id>", methods=["GET"])
def get_record(id: str) -> str:
    record = get_records(id)
    return jsonpickle.encode(record)


@v1.route("/records/<id>", methods=["POST"])
def post_record(id: str) -> str:
    data = request.json
    record = post_records(id, data)
    return jsonpickle.encode(record)
