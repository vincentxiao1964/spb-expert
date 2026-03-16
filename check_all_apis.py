import requests

endpoints = [
    'http://127.0.0.1:8000/api/v1/store/home/',
    'http://127.0.0.1:8000/api/v1/logistics/shipments/',
    'http://127.0.0.1:8000/api/v1/procurement/requests/'
]

for url in endpoints:
    try:
        response = requests.get(url)
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        # print(f"Preview: {str(response.json())[:100]}")
        print("-" * 20)
    except Exception as e:
        print(f"Failed {url}: {e}")
