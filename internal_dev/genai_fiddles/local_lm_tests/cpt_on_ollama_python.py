# this is ChatGPT's suggestion on how to run ollama/python
# 
import requests
import json

url = 'http://localhost:11434/api/generate'
headers = {'Content-Type': 'application/json'}
data = {
    'model': 'llama3.2',
    'prompt': 'Why is the sky blue?',
    'format': 'json',
    'stream': False
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print(result['response'])
else:
    print('Error:', response.status_code, response.text)