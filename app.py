from flask import Flask

from api.api import new_api
import db

app = Flask(__name__)


@new_api.route("/health")
def health():
    return {"ok": True}


print("Starting up!")

app.register_blueprint(new_api)

print("Initializing DB!")
db.initialize_db()
