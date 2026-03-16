
import requests
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spb_expert.settings")
django.setup()

from django.conf import settings

# Assuming server is running on localhost:8000
url = "http://localhost:8000/api/listings/?page=1"
response = requests.get(url)

print(f"Status Code: {response.status_code}")
try:
    data = response.json()
    count = data.get('count', 0)
    print(f"Count: {count}")
    print(f"Results length: {len(data.get('results', []))}")
except Exception as e:
    print(f"Error parsing JSON: {e}")
    print(response.text)
