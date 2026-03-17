import requests
import json

url = 'http://10.15.0.17:8000/temperature'
data = {'temperature': 23.5}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(data), headers=headers)

print('Status code:', response.status_code)
print('Response:', response.json())
