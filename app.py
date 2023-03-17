from flask import Flask

from api.api import records_api

import db

app = Flask(__name__)

print("Starting up!")

app.register_blueprint(records_api)

print("Initializing DB!")
db.initialize_db()
