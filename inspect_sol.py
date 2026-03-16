import requests
from bs4 import BeautifulSoup
import urllib.parse
import sys

# '甲板驳船' in GB2312/GBK
shiptype_gbk = '甲板驳船'.encode('gb2312')

url = 'https://sp.sol.com.cn/sell.asp'
# Try without params first to see if we get *any* listings
# Then try with params
print("--- Fetching Default Page ---")
try:
    response = requests.get(url)
    response.encoding = 'gb18030'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print visible text to see if there are listings
    text = soup.get_text()
    # Remove empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    print("\n".join(lines[:200])) # Print first 200 lines of text

    # Check for specific links again
    print("\n--- Checking for detail links ---")
    links = soup.find_all('a')
    count = 0
    for link in links:
        href = link.get('href')
        if href and ('detail' in href or 'show' in href):
            print(f"Link: {href} -> {link.text.strip()}")
            count += 1
            if count > 20: break
    if count == 0:
        print("No detail links found.")

except Exception as e:
    print(f"Error: {e}")
