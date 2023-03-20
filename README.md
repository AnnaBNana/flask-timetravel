# Time travel

A v1 and v2 API for record storage with simple structure.

A record consists of a simple identifier and a data object in JSON form.

Run in local:

* Python 3.11.0b5
* Create a virtualenv: `python -m venv /path/to/new/virtual/environment`
* Activate virtualenv: `source /path/to/new/virtual/environment`
* Pip install requirements `pip install -r requirements.txt`
* Run application on `http://127.0.0.1:5000`: `flask run` or `flask run --debug` to run in watch mode.
* Run tests: `pytest`

Making requests:

GET
``` bash
# get a record V1
> http GET http://127.0.0.1:5000/api/v1/records/20

# get record v2
> http GET http://127.0.0.1:5000/api/v2/records/5/latest

# get versions by slug
> GET http://127.0.0.1:5000/api/v2/records/5/versions
```

POST
``` bash
# create a record v1
> POST http://127.0.0.1:5000/api/v1/records/20 '{"hello": "world"}'

# create a record v2
> POST http://127.0.0.1:5000/api/v2/records/5/latest

```
