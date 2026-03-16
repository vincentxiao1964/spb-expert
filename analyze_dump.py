
import os
from bs4 import BeautifulSoup

file_path = 'sol_dump.html'
with open(file_path, 'rb') as f:
    content = f.read()
    soup = BeautifulSoup(content, 'html.parser', from_encoding='gb18030')
    
    tables = soup.find_all('table')
    if len(tables) > 3:
        table = tables[3]
        print("--- Inspecting Table 3 ---")
        rows = table.find_all('tr')
        for i, row in enumerate(rows[:5]):
            print(f"\nRow {i}:")
            # Print HTML to see structure
            print(row.prettify()[:500])
            
            # Check for links
            links = row.find_all('a')
            for link in links:
                print(f"  LINK: href={link.get('href')}, text={link.get_text(strip=True)}")
                
            # Check for onclick in tds
            cols = row.find_all('td')
            for col in cols:
                if col.has_attr('onclick'):
                    print(f"  ONCLICK: {col['onclick']}")
                # Check child elements for onclick
                for child in col.find_all(True):
                     if child.has_attr('onclick'):
                        print(f"  CHILD ONCLICK: {child['onclick']}")
