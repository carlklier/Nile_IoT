export FLASK_APP=./webservice.py
source $(pipenv --venv)/bin/activate
flask run -h 0.0.0.0
