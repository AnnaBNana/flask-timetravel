import jsonpickle
from flask import Blueprint

from api.get_records import get_records


new_api = Blueprint("api", __name__, url_prefix="/api/v1")


@new_api.route("/records/<id>", methods=["GET"])
def get_record(id: int) -> str:
    record = get_records(id)
    return jsonpickle.encode(record)
