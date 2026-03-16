import requests
import os

print("Starting dump...")
url = 'https://sp.sol.com.cn/sell.asp'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
data = {'shiptype': '甲板驳船'.encode('gb2312'), 'sotype': 'sell'} 

try:
    print(f"Posting to {url}...")
    response = requests.post(url, data=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.content)}")
    
    # Save as bytes to avoid encoding issues
    path = os.path.abspath('sol_dump.html')
    with open(path, 'wb') as f:
        f.write(response.content)
    print(f"Dumped to {path}")
except Exception as e:
    print(f"Error: {e}")
