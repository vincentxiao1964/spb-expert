import requests
from bs4 import BeautifulSoup
import re

url = "https://m.eshiptrading.com/shipcs/shipboc.aspx?BtTypesID=63"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Fetching {url}...")
response = requests.get(url, headers=headers)

with open('eship_full.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"Saved to eship_full.html ({len(response.text)} bytes)")

soup = BeautifulSoup(response.text, 'html.parser')

# Look for scripts
scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    if script.string:
        content = script.string
        if 'ajax' in content.lower() or 'load' in content.lower() or 'post' in content.lower():
            print(f"--- Script {i} ---")
            print(content[:500])
            print("...")

# Look for external scripts that might handle logic
for script in scripts:
    if script.get('src'):
        print(f"External script: {script['src']}")
