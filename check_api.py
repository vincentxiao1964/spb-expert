
import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/api/v1/listings/')
    if response.status_code == 200:
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            print("First item keys:", data[0].keys())
            print("First item unique_id:", data[0].get('unique_id'))
        else:
            print("No data or empty list returned")
            print(data)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception: {e}")
