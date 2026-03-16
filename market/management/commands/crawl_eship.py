import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from market.models import CrawledShip
from datetime import datetime, timedelta
import time
import re

class Command(BaseCommand):
    help = 'Crawl eshiptrading.com for deck barges'

    def handle(self, *args, **options):
        self.stdout.write('Starting crawl of eshiptrading.com...')
        
        base_url = "https://m.eshiptrading.com"
        start_url = "https://m.eshiptrading.com/shipcs/shipboc.aspx?BtTypesID=63"
        ajax_url = "https://m.eshiptrading.com/AjaxFile/Bt_ShipsHandler.aspx"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Calculate cut-off date (3 months ago)
        # Assuming "3 months" = 90 days
        cutoff_date = datetime.now().date() - timedelta(days=90)
        self.stdout.write(f"Filtering ships released after {cutoff_date}")
        
        count = 0
        max_count = 100
        ship_num = 0
        
        # Session to maintain cookies
        session = requests.Session()
        session.headers.update(headers)
        
        # Step 1: Load initial page to get initial list and ShipNum
        try:
            response = session.get(start_url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract initial ShipNum
            ship_num_input = soup.find('input', {'id': 'ShipNum'})
            if ship_num_input:
                ship_num = int(ship_num_input.get('value', 6))
            else:
                ship_num = 6
                
            # Process initial items
            items = soup.find_all('a', class_='list-item')
            self.stdout.write(f"Found {len(items)} items on initial page")
            
            for item in items:
                if count >= max_count:
                    break
                
                detail_url = item.get('href')
                if not detail_url:
                    continue
                    
                full_detail_url = base_url + detail_url
                saved, should_stop = self.process_ship(session, full_detail_url, cutoff_date)
                if saved:
                    count += 1
                if should_stop:
                    self.stdout.write("Stopping crawl as per stop signal (old data encountered).")
                    finished = True # Ensure outer loop stops too if we move this
                    break # Break inner loop
            
            # Step 2: AJAX Pagination
            finished = False
            while not finished and count < max_count:
                self.stdout.write(f"Fetching more... ShipNum: {ship_num}")
                
                data = {
                    'CallMethod': 'GetShipCSList()',
                    'ShipNum': str(ship_num),
                    'BtTypesID': '63'
                }
                
                try:
                    # The AJAX endpoint returns "isScro|&|&html_content"
                    # But based on eship_full.html, it's a POST request
                    ajax_response = session.post(ajax_url, data=data)
                    ajax_response.encoding = 'utf-8'
                    
                    if ajax_response.status_code != 200:
                        self.stdout.write(self.style.ERROR(f"AJAX request failed: {ajax_response.status_code}"))
                        break
                        
                    parts = ajax_response.text.split('|&|&')
                    if len(items) < 2:
                        # Should have isScro and content
                        if len(parts) > 0:
                             # Maybe just content? Or different format?
                             # inspect_eship_detail showed: var arr = data.split('|&|&'); isScro = arr[0]; result = arr[1];
                             pass
                    
                    if len(parts) >= 2:
                        is_scro = parts[0]
                        html_content = parts[1]
                        
                        if is_scro == '0':
                            finished = True
                        
                        soup_ajax = BeautifulSoup(html_content, 'html.parser')
                        new_items = soup_ajax.find_all('a', class_='list-item')
                        
                        if not new_items:
                            self.stdout.write("No more items found in AJAX response")
                            break
                            
                        self.stdout.write(f"Found {len(new_items)} new items")
                        
                        for item in new_items:
                            if count >= max_count:
                                break
                            
                            detail_url = item.get('href')
                            if not detail_url:
                                continue
                                
                            full_detail_url = base_url + detail_url
                            saved, should_stop = self.process_ship(session, full_detail_url, cutoff_date)
                            if saved:
                                count += 1
                            if should_stop:
                                self.stdout.write("Stopping crawl as per stop signal (old data encountered).")
                                finished = True
                                break
                        
                        ship_num += 6
                        time.sleep(1) # Be polite
                    else:
                        self.stdout.write("Unexpected AJAX response format")
                        break
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error during AJAX: {e}"))
                    break
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical error: {e}"))
            
        self.stdout.write(self.style.SUCCESS(f"Crawl completed. Saved {count} ships."))

    def process_ship(self, session, url, cutoff_date):
        """
        Returns: (saved, should_stop)
        saved: bool - whether the ship was saved/updated
        should_stop: bool - whether the crawl should stop (e.g. found old data)
        """
        try:
            # Check if already crawled
            # Extract source_id from URL (e.g. /SS102726.html -> SS102726)
            match = re.search(r'/(SS\d+)\.html', url)
            if not match:
                return False, False
            
            source_id = match.group(1)
            
            if CrawledShip.objects.filter(source_id=source_id, source='eship').exists():
                self.stdout.write(f"Skipping {source_id} (already exists)")
                return False, False
            
            # Fetch detail
            try:
                resp = session.get(url, timeout=10)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Extract Release Date
                # Look for "Release Date:"
                release_date_str = None
                
                # Search in .table-item
                items = soup.find_all('div', class_='table-item')
                for item in items:
                    bt = item.find('div', class_='bt')
                    if bt and 'Release Date' in bt.get_text():
                        bc = item.find('div', class_='bc')
                        if bc:
                            release_date_str = bc.get_text().strip()
                            break
                
                if not release_date_str:
                    # Fallback: check "Update" field
                    for div in soup.find_all('div', class_='text-view-num'):
                        bt = div.find('div', class_='bt')
                        if bt and 'Update' in bt.get_text():
                            num = div.find('div', class_='num')
                            if num:
                                update_text = num.get_text().strip()
                                release_date_str = self.parse_relative_date(update_text)
                                # If it returns a date object, convert back to str or handle logic
                                if isinstance(release_date_str, datetime) or hasattr(release_date_str, 'day'):
                                    final_date = release_date_str
                                    release_date_str = "parsed_object" # flag
                                break
                
                final_date = None
                if release_date_str == "parsed_object":
                    # final_date is already set above
                    pass
                elif release_date_str:
                    try:
                        # Try parsing YYYY-MM-DD
                        if re.match(r'\d{4}-\d{2}-\d{2}', release_date_str):
                            final_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                        # Try parsing relative
                        elif 'ago' in release_date_str or 'day' in release_date_str or 'hour' in release_date_str:
                             final_date = self.parse_relative_date(release_date_str)
                    except:
                        pass
                
                if final_date:
                    if final_date < cutoff_date:
                        self.stdout.write(f"Skipping {source_id}: Date {final_date} is too old")
                        return False, True # Stop signal!
                else:
                    self.stdout.write(f"Warning: Could not determine date for {source_id}, but saving anyway.")
                    # Do NOT return False here. Proceed to save.
                
                # Extract other fields
                dwt = self.get_text_by_label(soup, 'DWT')
                build_year_str = self.get_text_by_label(soup, 'Built Date') # 2021.10
                build_year = None
                if build_year_str:
                    try:
                        build_year = int(build_year_str.split('.')[0])
                    except:
                        pass
                
                width = self.get_text_by_label(soup, 'Breadth')
                length = self.get_text_by_label(soup, 'Loa')
                depth = self.get_text_by_label(soup, 'Depth')
                
                full_desc = soup.find('div', class_='shipremark')
                full_desc_text = full_desc.get_text().strip() if full_desc else ""
                
                # Save
                CrawledShip.objects.update_or_create(
                    source_id=source_id,
                    source='eship',
                    defaults={
                        'source_url': url,
                        'ship_category': 'Deck Barge',
                        'dwt': dwt or '',
                        'build_year': build_year,
                        'width': width or '',
                        'length': length or '',
                        'depth': depth or '',
                        'full_description': f"{full_desc_text}\n\nPublished: {final_date if final_date else 'Unknown'}"
                    }
                )
                self.stdout.write(f"Saved {source_id} ({final_date if final_date else 'No Date'})")
                return True, False
                
            except Exception as e:
                self.stdout.write(f"Error processing {url}: {e}")
                return False, False
                
        except Exception as e:
             self.stdout.write(f"Error in process_ship: {e}")
             return False, False

    def get_text_by_label(self, soup, label):
        items = soup.find_all('div', class_='table-item')
        for item in items:
            bt = item.find('div', class_='bt')
            if bt and label in bt.get_text():
                bc = item.find('div', class_='bc')
                if bc:
                    return bc.get_text().strip()
        return None

    def parse_relative_date(self, text):
        today = datetime.now().date()
        text = text.lower()
        try:
            if 'day' in text:
                days = int(re.search(r'(\d+)', text).group(1))
                return today - timedelta(days=days)
            if 'hour' in text:
                return today
            if 'min' in text:
                return today
            # Try absolute
            return datetime.strptime(text, '%Y-%m-%d').date()
        except:
            return None
