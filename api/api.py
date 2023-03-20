from flask import Blueprint

from api.v1 import v1
from api.v2 import v2

records_api = Blueprint("api", __name__, url_prefix="/api")


@records_api.route("/health")
def health() -> dict[str, bool]:
    """Return ok response."""
    return {"ok": True}


records_api.register_blueprint(v1)
records_api.register_blueprint(v2)
