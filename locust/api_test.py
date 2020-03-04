import requests
import datetime
import json

data = {
  'config': 'Sample Configuration',
  'start': datetime.datetime.now().isoformat(),
  'end': datetime.datetime.now().isoformat(),
  'workers': 3}

print("DATA: " + str(data))
endpoint='http://localhost:5000/api/v1/tests'
request = requests.post(endpoint, json=data)
print(request.text)
