import requests
from bs4 import BeautifulSoup

print("Running V4 script (Form inspection)...")
url = 'https://sp.sol.com.cn/sell.asp'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://sp.sol.com.cn/sell.asp'
}

try:
    response = requests.get(url, headers=headers)
    response.encoding = 'gb18030'
    soup = BeautifulSoup(response.text, 'html.parser')

    forms = soup.find_all('form')
    for form in forms:
        print(f"\n--- Form: {form.get('name')} (Action: {form.get('action')}) ---")
        inputs = form.find_all('input')
        for inp in inputs:
            print(f"  Input: {inp.get('name')} = {inp.get('value')} (Type: {inp.get('type')})")
        
        selects = form.find_all('select')
        for sel in selects:
             print(f"  Select: {sel.get('name')}")

except Exception as e:
    print(e)
