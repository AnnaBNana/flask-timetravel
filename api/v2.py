import jsonpickle
from flask import Blueprint, request

from api.records_api import API
from service.record import RecordRevisionHistoryService


v2 = Blueprint("v2", __name__, url_prefix="/v2")
service = RecordRevisionHistoryService()
api = API(service)


@v2.route("/records/<id>/<version>", methods=["GET"])
def get_record(id: str, version: str) -> str:
    record = api.get_records(id, version=version)
    return jsonpickle.encode(record)


@v2.route("/records/<id>/<version>", methods=["POST"])
def post_record(id: str, version: str) -> tuple[str, int]:
    data = request.json
    api.post_records(id, data, version=version)
    return ("", 204)


@v2.route("/records/<id>/versions", methods=["GET"])
def get_versions(id: str) -> list[str]:
    versions = api.get_versions(id)
    return jsonpickle.encode({"versions": versions}, 200)
