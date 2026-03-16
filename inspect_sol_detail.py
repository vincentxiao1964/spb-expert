import requests
from bs4 import BeautifulSoup
import sys
import re

url = 'https://sp.sol.com.cn/sell_msg.asp?solid=lhhdhi'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

try:
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    response.encoding = 'gb18030' # The site uses GB18030/GB2312
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Main Ship Info Table
    print("\n--- Main Ship Info ---")
    # It seems to be in a table. Let's look for '出售2011年造550吨沿海甲板货船'
    title = soup.find(string=lambda t: t and '出售2011年造550吨沿海甲板货船' in t)
    if title:
        print(f"Found Title: {title.strip()}")
        # Traverse up to find the container
        container = title.find_parent('table')
        if container:
            print("Found Main Table.")
            # Print rows text
            for tr in container.find_all('tr'):
                print(f"Row: {tr.get_text(strip=True)}")
    else:
        print("Title not found in text.")

    # 2. Remark Section (备注)
    print("\n--- Remark Section ---")
    remark_label = soup.find(string=lambda t: t and '备' in t and '注' in t)
    if remark_label:
        print("Found Remark Label.")
        remark_row = remark_label.find_parent('tr')
        if remark_row:
            remark_text = remark_row.get_text(separator=' ', strip=True)
            print(f"Remark Content: {remark_text}")
            
            # --- Test Extraction Logic ---
            print("\nTesting Extraction Logic on Remark...")
            extracted_contacts = []
            seen_values = set()
            
            # 1. Mobile numbers (11 digits starting with 1)
            mobiles = re.findall(r'(?:[^0-9]|^)(1[3-9]\d{9})(?:[^0-9]|$)', remark_text)
            for m in mobiles:
                if m not in seen_values:
                    extracted_contacts.append(f"Mobile: {m}")
                    seen_values.add(m)

            # 2. Name extraction
            # Pattern A: Prefix based (联系人: 张三)
            name_pattern1 = r'(?:联系人|姓名|联系)[:：]\s*([\u4e00-\u9fa5]{1,4}(?:先生|女士|小姐|经理|总)?)'
            names = re.findall(name_pattern1, remark_text)
            for n in names:
                if n not in ['方式'] and n not in seen_values:
                    extracted_contacts.append(f"Name: {n}")
                    seen_values.add(n)
            
            # Pattern B: Context based (e.g. 请联系王经理)
            name_pattern2 = r'联系\s*([\u4e00-\u9fa5]{1,3}(?:经理|总|先生|女士))'
            names2 = re.findall(name_pattern2, remark_text)
            for n in names2:
                if n not in seen_values:
                    extracted_contacts.append(f"Name: {n}")
                    seen_values.add(n)

            # 3. Company extraction
            # Pattern A: Prefix based (公司: XXX)
            company_pattern1 = r'(?:公司|公司名|单位)[:：]\s*([^\s,，;；]+)'
            companies = re.findall(company_pattern1, remark_text)
            for c in companies:
                if c not in seen_values:
                    extracted_contacts.append(f"Company: {c}")
                    seen_values.add(c)
                    
            # Pattern B: Suffix based (XXX公司)
            # Exclude colons to avoid capturing "公司：XXX"
            company_pattern2 = r'([^\s,，;；。:：]{2,20}公司)'
            companies2 = re.findall(company_pattern2, remark_text)
            for c in companies2:
                if c in ['本公司', '我公司', '贵公司']:
                    continue
                if c not in seen_values:
                    extracted_contacts.append(f"Company: {c}")
                    seen_values.add(c)
            
            print("Extracted Results:")
            for item in extracted_contacts:
                print(f"  - {item}")

    else:
        print("Remark label not found.")

    # 3. Images
    print("\n--- Images Debug ---")
    img_label = soup.find(string=lambda t: t and '船舶照片' in t)
    if img_label:
        print("Found Image Label.")
        parent = img_label.parent
        grandparent = parent.parent
        
        # Check next sibling of grandparent (the Title DIV)
        if grandparent:
            next_sib = grandparent.find_next_sibling()
            if next_sib:
                print(f"Next Sibling of Image Title DIV is {next_sib.name}")
                # print(next_sib.prettify()[:500])
                
                imgs = next_sib.find_all('img')
                print(f"Images in Next Sibling: {len(imgs)}")
                for img in imgs:
                    print(f"Img src: {img.get('src')}")
            else:
                print("No Next Sibling for Image Title DIV.")
                
            # Also check next next sibling just in case
            if next_sib:
                next_next = next_sib.find_next_sibling()
                if next_next:
                    print(f"Next Next Sibling is {next_next.name}")
                    imgs = next_next.find_all('img')
                    print(f"Images in Next Next Sibling: {len(imgs)}")

    # 4. Contact Info
    print("\n--- Contact Info Debug ---")
    contact_label = soup.find(string=lambda t: t and '联系方式' in t)
    if contact_label:
        print("Found Contact Label.")
        parent = contact_label.parent
        print(f"Parent ({parent.name}) content snippet:")
        print(parent.prettify()[:500])
        
        grandparent = parent.parent
        if grandparent:
             print(f"Grandparent ({grandparent.name}) content snippet:")
             # print(grandparent.prettify()[:500])
             pass

except Exception as e:
    print(f"Error: {e}")
