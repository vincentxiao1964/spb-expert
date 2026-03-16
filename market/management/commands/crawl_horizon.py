import time
import requests
import json
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from market.models import CrawledShip

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Crawl Horizon Ship Brokers for Self Propelled Barges (Last 3 months)'

    def handle(self, *args, **options):
        self.stdout.write("Starting Horizon Ship Brokers crawl...")
        
        base_url = "https://horizonship.com/ship-category/barges-for-sale/self-propelled-barges-for-sale/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36 Edg/144.0.0.0'
        }
        
        # Calculate cut-off date (3 months ago)
        cutoff_date = timezone.now() - timedelta(days=90)
        self.stdout.write(f"Cut-off date: {cutoff_date.strftime('%Y-%m-%d')}")
        
        session = requests.Session()
        session.headers.update(headers)
        
        count = 0
        max_count = 100
        page_size = 50
        start = 0
        finished = False
        
        while not finished and count < max_count:
            url = f"{base_url}?start={start}"
            self.stdout.write(f"Fetching page: {url}")
            
            try:
                response = session.get(url, timeout=30)
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"Failed to fetch page: {response.status_code}"))
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the table rows
                # The table structure seems to be inside a form or just table tags
                # Based on inspection: <tr class="alt"> or just <tr> inside <tbody>
                # We can look for links that contain "/ship/"
                
                rows = soup.find_all('tr')
                found_on_page = 0
                
                for row in rows:
                    if count >= max_count:
                        finished = True
                        break
                        
                    # Check if this row is a ship listing
                    # It should have a link to a ship detail page
                    link_tag = row.find('a', href=True)
                    if not link_tag:
                        continue
                        
                    link = link_tag['href']
                    if '/ship/' not in link:
                        continue
                    
                    # Extract Ref ID (usually in the first cell)
                    cols = row.find_all('td')
                    if not cols:
                        continue
                        
                    try:
                        source_id = cols[0].get_text(strip=True)
                        # If ID is not numeric, it might be the wrong row (header or mobile view)
                        if not source_id.isdigit():
                            continue
                            
                        # Extract basic info from row
                        title = link_tag.get_text(strip=True)
                        # Length is usually in col 3 (index 3) based on inspection, but let's be safe and just get it from detail or assume column order
                        # Col 0: Ref
                        # Col 2: Title (Col 1 is empty or image?)
                        # Col 3: Length
                        # Col 4: Beam (Width)
                        # Col 5: Draft (Depth)
                        # Col 6: Year
                        # Col 8: DWT
                        
                        length_val = cols[3].get_text(strip=True) if len(cols) > 3 else ""
                        width_val = cols[4].get_text(strip=True) if len(cols) > 4 else ""
                        depth_val = cols[5].get_text(strip=True) if len(cols) > 5 else ""
                        build_year_val = cols[6].get_text(strip=True) if len(cols) > 6 else ""
                        dwt_val = cols[8].get_text(strip=True) if len(cols) > 8 else ""
                        
                    except Exception as e:
                        self.stdout.write(f"Error parsing row: {e}")
                        continue
                        
                    found_on_page += 1
                    
                    # Check if already exists
                    if CrawledShip.objects.filter(source_id=source_id, source='horizon').exists():
                        self.stdout.write(f"Skipping {source_id} (already exists)")
                        continue
                    
                    # Fetch detail to check date
                    self.stdout.write(f"Checking details for {source_id}...")
                    try:
                        time.sleep(1) # Be polite
                        detail_resp = session.get(link, timeout=30)
                        detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                        
                        # Find JSON-LD for datePublished
                        scripts = detail_soup.find_all('script', type='application/ld+json')
                        pub_date = None
                        
                        for i, script in enumerate(scripts):
                            try:
                                script_content = script.string or script.text
                                if not script_content:
                                    continue
                                    
                                data = json.loads(script_content)
                                # self.stdout.write(f"Debug: script {i} keys: {list(data.keys())}")
                                if '@graph' in data:
                                    # self.stdout.write(f"Debug: @graph found with {len(data['@graph'])} items")
                                    for item in data['@graph']:
                                        if 'datePublished' in item:
                                            pub_date = item['datePublished']
                                            break
                                elif 'datePublished' in data:
                                     pub_date = data['datePublished']
                                     
                                if pub_date: break
                            except Exception as e:
                                self.stdout.write(f"Debug: Error parsing script {i}: {e}")
                                continue
                        
                        if not pub_date:
                            self.stdout.write(f"  No date found for {source_id}, but saving anyway.")
                            dt = None
                        else:
                            # Parse date (ISO 8601) e.g., 2025-11-26T20:18:57+00:00
                            # Python 3.7+ supports fromisoformat, but handle potential 'Z' or offset
                            try:
                                dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                            except ValueError:
                                 # Fallback manual parsing if needed
                                 try:
                                     dt = datetime.strptime(pub_date.split('T')[0], '%Y-%m-%d')
                                     dt = timezone.make_aware(dt)
                                 except Exception as e:
                                     self.stdout.write(f"  Error parsing date {pub_date}: {e}. Treating as no date.")
                                     dt = None
                        
                        if dt and dt < cutoff_date:
                            self.stdout.write(f"  Date {dt.date()} is too old. Stopping crawl.")
                            finished = True
                            break
                            
                        # Valid! Save it.
                        CrawledShip.objects.create(
                            source_id=source_id,
                            source='horizon',
                            source_url=link,
                            ship_category='Self Propelled Barge',
                            dwt=dwt_val,
                            build_year=int(build_year_val) if build_year_val and build_year_val.isdigit() else None,
                            width=width_val,
                            length=length_val,
                            depth=depth_val,
                            full_description=f"{title}\n\nPublished: {pub_date if pub_date else 'Unknown'}"
                        )
                        self.stdout.write(self.style.SUCCESS(f"  Saved {source_id} ({dt.date() if dt else 'No Date'})"))
                        count += 1
                        
                        if count >= 100:
                            self.stdout.write("  Reached 100 items limit. Stopping crawl.")
                            finished = True
                            break
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Error processing detail {link}: {e}"))
                
                if found_on_page == 0:
                    finished = True
                else:
                    start += page_size
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Critical error: {e}"))
                break
                
        self.stdout.write(self.style.SUCCESS(f"Crawl completed. Saved {count} ships."))
