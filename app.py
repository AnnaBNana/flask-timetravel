from flask import Flask

from api.api import new_api

app = Flask(__name__)


@new_api.route("/health")
def health():
    return {"ok": True}


app.register_blueprint(new_api)
