import requests
from bs4 import BeautifulSoup

url = "https://horizonship.com/ship-category/barges-for-sale/self-propelled-barges-for-sale/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    with open('horizon_full.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Saved horizon_full.html")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Try to find list items
    # Based on user snippet, it seems to be a table or div structure
    # Let's print some classes
    for tag in soup.find_all(['div', 'tr'], class_=True):
         pass # just to trigger soup parsing if needed
         
except Exception as e:
    print(f"Error: {e}")
