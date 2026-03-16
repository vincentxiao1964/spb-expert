import requests

url = "https://m.eshiptrading.com/SS102726.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    with open('eship_detail.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Saved eship_detail.html")
except Exception as e:
    print(f"Error: {e}")
