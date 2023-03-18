import jsonpickle
from flask import Blueprint, request

from api.get_records import get_records_v2
from api.post_records import post_records_v2


v2 = Blueprint("v2", __name__, url_prefix="/v2")


@v2.route("/records/<id>/<version>", methods=["GET"])
def get_record(id: str, version: str) -> str:
    record = get_records_v2(id, version)
    return jsonpickle.encode(record)


@v2.route("/records/<id>/<version>", methods=["POST"])
def post_record(id: str, version: str) -> tuple[str, ...]:
    data = request.json
    post_records_v2(id, data, version)
    return ("", 204)
