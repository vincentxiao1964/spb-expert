
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from collections import defaultdict
from django.core.management.base import BaseCommand
from market.models import CrawledShip

# User = get_user_model() # Not needed for CrawledShip

class Command(BaseCommand):
    help = 'Crawl deck barges from sp.sol.com.cn and generate width statistics (Max 20 pages)'

    def handle(self, *args, **options):
        # user = User.objects.filter(is_superuser=True).first()
        # if not user:
        #     self.stdout.write(self.style.ERROR('No superuser found. Cannot assign listings.'))
        #     return

        base_url = 'https://sp.sol.com.cn/'
        list_url = 'https://sp.sol.com.cn/sell.asp'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        print("Crawling sp.sol.com.cn for Deck Barges (Max 100 items)...")
        
        count = 0
        max_count = 100
        stats = {'28': 0, '32': 0, '36': 0}
        width_distribution = defaultdict(int)
        
        # Pre-encode search term
        shiptype_gb = '甲板驳船'.encode('gb2312')
        shiptype_encoded = urllib.parse.quote(shiptype_gb)

        for pageno in range(1, 21): # Keep page loop but break on count
            if count >= max_count:
                print(f"Reached limit of {max_count} items. Stopping.")
                break
                
            print(f"Fetching page {pageno}...")
            
            # Use GET with params for all pages
            url = f"{list_url}?pageno={pageno}&shiptype={shiptype_encoded}&sotype=sell"
            
            try:
                response = requests.get(url, headers=headers)
                response.encoding = 'gb18030'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                tables = soup.find_all('table')
                if len(tables) <= 3:
                    print(f"No results table found on page {pageno}. Stopping.")
                    break

                result_table = tables[3]
                rows = result_table.find_all('tr')
                
                if len(rows) == 0:
                    print(f"No rows in table on page {pageno}. Stopping.")
                    break
                
                # Verify if we have listings or just header
                # Sometimes table 3 is just layout. Check for "DWT" or similar in header?
                # The previous run showed 22 items on page 1, so it works.
                
                page_processed_count = 0
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 10:
                        continue
                    
                    try:
                        id_link = cols[1].find('a')
                        if not id_link: continue
                        
                        external_id = id_link.get_text(strip=True)
                        detail_url = base_url + id_link['href']
                        
                        dwt_text = cols[3].get_text(strip=True).replace('DWT', '').strip()
                        year_text = cols[4].get_text(strip=True)
                        status_text = cols[9].get_text(strip=True) # Col 9 is Status
                        
                        if '有效' not in status_text:
                            # print(f"Skipping {external_id}: Status is {status_text}")
                            continue
                            
                        # print(f"Processing {external_id} ({dwt_text} DWT)...")
                        
                        # Fetch Detail
                        detail_resp = requests.get(detail_url, headers=headers)
                        detail_resp.encoding = 'gb18030'
                        detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                        
                        # --- New Parsing Logic ---
                        
                        # 1. REMARK (Often contains contact info)
                        remark_text = ""
                        remark_label = detail_soup.find(string=lambda t: t and '备' in t and '注' in t)
                        if remark_label:
                            remark_row = remark_label.find_parent('tr')
                            if remark_row:
                                # Clean up text
                                remark_text = remark_row.get_text(separator=' ', strip=True)

                        # 2. IMAGES
                        img_urls = []
                        img_label = detail_soup.find(string=lambda t: t and '船舶照片' in t)
                        if img_label:
                            # Use next sibling logic as found in inspection
                            parent = img_label.parent # span
                            grandparent = parent.parent # div class="buysellCont_title"
                            
                            if grandparent:
                                next_sib = grandparent.find_next_sibling()
                                if next_sib:
                                    for img in next_sib.find_all('img'):
                                        src = img.get('src')
                                        if src:
                                            # Check if there is a parent anchor with high-res link
                                            parent_a = img.find_parent('a')
                                            if parent_a and parent_a.get('href') and parent_a['href'].lower().endswith('.jpg'):
                                                src = parent_a['href']
                                                
                                            if not src.startswith('http'):
                                                full_src = base_url + src.lstrip('/')
                                            else:
                                                full_src = src
                                                
                                            if full_src not in img_urls:
                                                img_urls.append(full_src)

                        # 3. CONTACT
                        # First try the separate section (usually paywalled but check anyway)
                        contact_text = ""
                        contact_label = detail_soup.find(string=lambda t: t and '联系方式' in t)
                        if contact_label:
                             # Check if it's the paywall text
                             parent = contact_label.parent
                             if parent and "付费" in parent.get_text():
                                 pass # Paywalled
                             else:
                                 # Try to find content if not paywalled
                                 pass 
                        
                        # Fallback: Extract contact from Remark
                        # Pattern: Matches mobile numbers, names, companies
                        extracted_contacts = []
                        seen_values = set()
                        
                        # 1. Mobile numbers (11 digits starting with 1)
                        mobiles = re.findall(r'(?:[^0-9]|^)(1[3-9]\d{9})(?:[^0-9]|$)', remark_text)
                        for m in mobiles:
                            if m not in seen_values:
                                extracted_contacts.append(f"Mobile: {m}")
                                seen_values.add(m)

                        # 2. Name extraction
                        # Pattern A: Prefix based (联系人: 张三 / Cherry)
                        # Match non-digit, non-punctuation chars after label
                        name_pattern1 = r'(?:联系人|姓名|联系)[:：]\s*([a-zA-Z\u4e00-\u9fa5]{2,10}(?:先生|女士|小姐|经理|总)?)'
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
                            
                        if extracted_contacts:
                            contact_text = "\n".join(extracted_contacts)

                        # 4. Construct Clean Description (Simplified)
                        desc_lines = []
                        desc_lines.append(f"Original ID: {external_id}")
                        desc_lines.append(f"Source: {detail_url}")
                        desc_lines.append("")
                        desc_lines.append("--- Ship Specifications ---")
                        desc_lines.append(f"DWT: {dwt_text}")
                        desc_lines.append(f"Year: {year_text}")
                        desc_lines.append(f"Status: {status_text}")
                        
                        full_text = detail_soup.get_text() # For dimension regex only
                        
                        width = ''
                        length = ''
                        depth = ''
                        
                        # Regex for dimensions (keep existing logic)
                        width_match = re.search(r'(?:宽|B|Breadth|Width)[\s:]*(\d+(\.\d+)?)', full_text, re.IGNORECASE)
                        if width_match:
                            width = width_match.group(1)
                        
                        length_match = re.search(r'(?:长|L|Length|LOA)[\s:]*(\d+(\.\d+)?)', full_text, re.IGNORECASE)
                        if length_match:
                            length = length_match.group(1)
                            
                        depth_match = re.search(r'(?:深|D|Depth)[\s:]*(\d+(\.\d+)?)', full_text, re.IGNORECASE)
                        if depth_match:
                            depth = depth_match.group(1)
                            
                        if width: desc_lines.append(f"Width: {width}")
                        if length: desc_lines.append(f"Length: {length}")
                        if depth: desc_lines.append(f"Depth: {depth}")
                        
                        # Removed "Remarks" and "Contact" and "Images" from full_description 
                        # because they are now in structured fields and user requested deduplication.
                        
                        final_description = "\n".join(desc_lines)

                        if width:
                            w_float = float(width)
                            width_distribution[w_float] += 1
                            if 27.5 <= w_float <= 28.5:
                                stats['28'] += 1
                            elif 31.5 <= w_float <= 32.5:
                                stats['32'] += 1
                            elif 35.5 <= w_float <= 36.5:
                                stats['36'] += 1
                        else:
                            width_distribution['Unknown'] += 1
                        
                        # Save to DB
                        ship_category_val = 'NON_SELF_PROPELLED'
                        if re.search(r'(主机|Engine)[\s:]*[^\s0-9]*\d+', full_text, re.IGNORECASE):
                            ship_category_val = 'SELF_PROPELLED'
                            
                        CrawledShip.objects.update_or_create(
                            source_id=external_id,
                            defaults={
                                'source': 'sol',
                                'source_url': detail_url,
                                'ship_category': ship_category_val,
                                'dwt': dwt_text,
                                'build_year': int(year_text) if year_text.isdigit() else None,
                                'width': width,
                                'length': length,
                                'depth': depth,
                                'full_description': final_description,
                                'remark': remark_text,
                                'contact_info': contact_text,
                                'images': img_urls
                            }
                        )
                        
                        count += 1
                        page_processed_count += 1
                        
                    except Exception as e:
                        print(f"Error processing row: {e}")
                        continue
                
                if page_processed_count == 0:
                     # Check if we should stop. 
                     # If the table exists but no valid items found (e.g. all invalid status), 
                     # we should probably check if it's the last page.
                     # Usually the last page has fewer items. If 0 items, likely end of list.
                     # But we check for empty rows earlier.
                     # If we found rows but filtered them all out, we might still want to check next page.
                     # But if there are NO rows, we break.
                     pass

            except Exception as e:
                print(f"Page {pageno} Error: {e}")
                # Don't break immediately on network error, try next? Or break?
                # Break to be safe.
                break

        print("\n" + "="*30)
        print("航运在线在售甲板表")
        print("="*30)
        print(f"28米宽：{stats['28']}")
        print(f"32米宽：{stats['32']}")
        print(f"36米宽：{stats['36']}")
        print("-" * 20)
        print("详细分布:")
        sorted_widths = sorted([w for w in width_distribution.keys() if isinstance(w, float)])
        for w in sorted_widths:
            print(f"{w}m: {width_distribution[w]}")
        if width_distribution['Unknown'] > 0:
            print(f"Unknown: {width_distribution['Unknown']}")
        print("="*30)
        print(f"Total Crawled: {count}")
