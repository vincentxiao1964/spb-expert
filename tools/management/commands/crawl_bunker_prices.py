import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from tools.models import Port, BunkerPrice
from django.utils import timezone
from decimal import Decimal
import re
import time
import traceback

class Command(BaseCommand):
    help = 'Crawl daily bunker prices from Ship & Bunker and 100ppi'

    def add_arguments(self, parser):
        parser.add_argument('--domestic-url', type=str, help='URL for 100ppi domestic prices')

    def crawl_100ppi(self, url):
        self.stdout.write(f"Crawling domestic prices from {url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            # Handle JS protection
            if 'document.cookie' in response.text and 'HW_CHECK' in response.text:
                self.stdout.write("Detected JS protection. Handling...")
                match = re.search(r'var _0x2 = "([a-f0-9]+)";', response.text)
                if match:
                    cookie_val = match.group(1)
                    cookies = {'HW_CHECK': cookie_val}
                    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
                else:
                    self.stdout.write(self.style.ERROR("Failed to bypass JS protection."))
                    return

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch {url}: {response.status_code}"))
                return
                
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse content
            content_div = soup.find('div', class_='nd-c') or soup.find('div', class_='news-detail')
            if not content_div:
                content_div = soup
            
            lines = [line.strip() for line in content_div.get_text(separator='\n').split('\n') if line.strip()]
            
            # Find start
            start_index = 0
            for i, line in enumerate(lines):
                if "最新报价" in line:
                    start_index = i + 1
                    break
            
            if start_index == 0:
                self.stdout.write(self.style.WARNING("Could not find data start marker '最新报价'."))
                return

            current_fuel = None
            port_map = {
                '上海': 'Shanghai',
                '舟山': 'Zhoushan',
                '青岛': 'Qingdao',
                '广州': 'Guangzhou',
                '大连': 'Dalian',
                '天津': 'Tianjin',
                '宁波': 'Ningbo',
                '秦皇岛': 'Qinhuangdao',
                '珠海': 'Zhuhai',
                '湛江': 'Zhanjiang',
                '唐山': 'Tangshan',
                '厦门': 'Xiamen'
            }
            
            today = timezone.now().date()
            count = 0
            
            i = start_index
            while i < len(lines):
                line = lines[i]
                
                if "公式定价原理" in line or "版权声明" in line or "相关商品" in line:
                    break
                
                # Check fuel
                if "燃料油" in line and "CST" in line:
                    if "180CST" in line:
                        current_fuel = "RME180"
                    elif "120CST" in line:
                        current_fuel = "RME180" # Map 120CST to RME180 for now as it's similar domestic grade? Or keep separate if DB supports.
                        # DB has RME180. 120CST is close. Let's map to RME180 but maybe log it?
                        # Actually user said "RME180". 120CST is slightly different.
                        # Let's check if model supports others.
                        # Model: RME180, DIESEL0.
                        # If I map 120CST to RME180, it might overwrite 180CST if same port.
                        # The list has Shanghai 180CST and Shanghai 120CST.
                        # If I save both as RME180, one will overwrite.
                        # I'll prioritize 180CST. If current_fuel is 120CST, maybe skip or map to IFO380?
                        # Let's skip 120CST for now to be safe, or only use it if 180 missing.
                        pass
                    elif "0#" in line:
                        current_fuel = "DIESEL0"
                    
                    if "120CST" in line:
                         current_fuel = "120CST" # Mark it to handle logic below

                    i += 1
                    continue
                
                if "元/吨" in line:
                    if i >= 3:
                        price_line = line
                        location = lines[i-1]
                        # brand = lines[i-2]
                        # company = lines[i-3]
                        
                        if current_fuel == "120CST":
                            # Skip 120CST for now as we focus on RME180
                            i += 1
                            continue
                            
                        if not current_fuel:
                            i += 1
                            continue

                        # Extract price
                        price_match = re.search(r'(\d+)', price_line)
                        if not price_match:
                            i += 1
                            continue
                        price = Decimal(price_match.group(1))
                        
                        # Map Port
                        port_en = None
                        for cn, en in port_map.items():
                            if cn in location:
                                port_en = en
                                break
                        
                        if port_en:
                            try:
                                port = Port.objects.get(name_en=port_en)
                                BunkerPrice.objects.update_or_create(
                                    port=port,
                                    date=today,
                                    fuel_type=current_fuel,
                                    defaults={
                                        'price': price,
                                        'currency': 'CNY',
                                        'change': 0,
                                        'source': '100ppi'
                                    }
                                )
                                self.stdout.write(f"  Saved {current_fuel} for {port_en}: {price} CNY")
                                count += 1
                            except Port.DoesNotExist:
                                pass # self.stdout.write(self.style.WARNING(f"Port {port_en} not in DB"))
                
                i += 1
            
            self.stdout.write(self.style.SUCCESS(f"100ppi crawl finished. Saved {count} records."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error crawling 100ppi: {e}"))
            traceback.print_exc()

    def crawl_100ppi_diesel(self):
        url = "https://diesel.100ppi.com/"
        self.stdout.write(f"Crawling diesel prices from {url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            # Handle JS protection
            if 'document.cookie' in response.text and 'HW_CHECK' in response.text:
                self.stdout.write("Detected JS protection on Diesel page. Handling...")
                match = re.search(r'var _0x2 = "([a-f0-9]+)";', response.text)
                if match:
                    cookie_val = match.group(1)
                    cookies = {'HW_CHECK': cookie_val}
                    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
                else:
                    self.stdout.write(self.style.ERROR("Failed to bypass JS protection on Diesel page."))
                    return

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch {url}: {response.status_code}"))
                return

            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.content, 'html.parser')
            
            tables = soup.find_all('table')
            if not tables:
                self.stdout.write(self.style.WARNING("No tables found on Diesel page."))
                return

            # Assume first table is the main price table
            table = tables[0]
            rows = table.find_all('tr')
            
            today_str = timezone.now().strftime('%Y-%m-%d')
            prices = []
            
            for row in rows:
                cols = row.find_all('td')
                if not cols or len(cols) < 7:
                    continue
                
                # Column mapping based on inspection:
                # 0: Product (牌号:0#...)
                # 1: Short Name
                # 3: Price String (5730元/吨)
                # 4: Price Value (5730)
                # 6: Date (2026-02-06)
                
                product = cols[0].get_text(strip=True)
                price_val_str = cols[4].get_text(strip=True)
                date_str = cols[6].get_text(strip=True)
                
                if "0#" in product and date_str == today_str:
                    try:
                        price = Decimal(price_val_str)
                        if price > 0:
                            prices.append(price)
                    except:
                        pass
            
            if prices:
                avg_price = sum(prices) / len(prices)
                self.stdout.write(f"Found {len(prices)} diesel prices for today. Average: {avg_price:.2f} CNY")
                
                # Save for Qingdao (Proxy for Shandong)
                try:
                    port = Port.objects.get(name_en='Qingdao')
                    BunkerPrice.objects.update_or_create(
                        port=port,
                        date=timezone.now().date(),
                        fuel_type='DIESEL0',
                        defaults={
                            'price': avg_price,
                            'currency': 'CNY',
                            'change': 0,
                            'source': '100ppi (Shandong Avg)'
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f"Saved DIESEL0 for Qingdao: {avg_price:.2f} CNY"))
                except Port.DoesNotExist:
                    self.stdout.write(self.style.WARNING("Port Qingdao not found"))
            else:
                self.stdout.write(self.style.WARNING(f"No diesel prices found for today ({today_str})."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error crawling 100ppi Diesel: {e}"))
            traceback.print_exc()

    def crawl_100ppi_fueloil(self):
        url = "https://fueloil.100ppi.com/"
        self.stdout.write(f"Crawling fuel oil prices from {url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if 'document.cookie' in response.text and 'HW_CHECK' in response.text:
                self.stdout.write("Detected JS protection on Fuel Oil page. Handling...")
                match = re.search(r'var _0x2 = "([a-f0-9]+)";', response.text)
                if match:
                    cookie_val = match.group(1)
                    cookies = {'HW_CHECK': cookie_val}
                    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
                else:
                    self.stdout.write(self.style.ERROR("Failed to bypass JS protection on Fuel Oil page."))
                    return

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch {url}: {response.status_code}"))
                return
                
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.content, 'html.parser')
            
            tables = soup.find_all('table')
            if not tables:
                self.stdout.write(self.style.WARNING("No tables found on Fuel Oil page."))
                return
                
            # Table 0 is usually the spot price table
            table = tables[0]
            rows = table.find_all('tr')
            
            today = timezone.now().date()
            count = 0
            
            # Location Mapping
            loc_map = {
                '舟山': 'Zhoushan',
                '上海': 'Shanghai',
                '大': 'Dalian', # 中国船舶燃料大 -> Dalian
                '广': 'Guangzhou', # 中国船舶燃料广 -> Guangzhou
                '湛': 'Zhanjiang', # 中国船舶燃料湛 -> Zhanjiang
                '唐山': 'Tangshan',
                '曹妃甸': 'Tangshan',
                '宁波': 'Ningbo',
                '青岛': 'Qingdao',
                '天津': 'Tianjin',
                '秦皇岛': 'Qinhuangdao',
                '厦门': 'Xiamen'
            }

            for row in rows:
                cols = row.find_all('td')
                if not cols or len(cols) < 7:
                    continue
                
                product = cols[0].get_text(strip=True)
                location = cols[2].get_text(strip=True)
                price_str = cols[3].get_text(strip=True)
                
                if "180CST" in product:
                    fuel_type = "RME180"
                else:
                    continue
                
                currency = 'CNY'
                if '美元' in price_str:
                    currency = 'USD'
                
                price_match = re.search(r'(\d+)', price_str)
                if not price_match:
                    continue
                price = Decimal(price_match.group(1))
                
                port_en = None
                for k, v in loc_map.items():
                    if k in location:
                        port_en = v
                        break
                
                if port_en:
                    try:
                        port = Port.objects.get(name_en=port_en)
                        BunkerPrice.objects.update_or_create(
                            port=port,
                            date=today,
                            fuel_type=fuel_type,
                            defaults={
                                'price': price,
                                'currency': currency,
                                'change': 0,
                                'source': '100ppi (FuelOil)'
                            }
                        )
                        self.stdout.write(f"  Saved {fuel_type} for {port_en}: {price} {currency}")
                        count += 1
                    except Port.DoesNotExist:
                        pass
            
            self.stdout.write(self.style.SUCCESS(f"100ppi FuelOil crawl finished. Saved {count} records."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error crawling 100ppi FuelOil: {e}"))
            traceback.print_exc()

    def handle(self, *args, **options):
        # Always run diesel crawl
        self.crawl_100ppi_diesel()
        # Always run fuel oil crawl
        self.crawl_100ppi_fueloil()

        domestic_url = options.get('domestic_url')
        if domestic_url:
            self.crawl_100ppi(domestic_url)

        base_url = "https://shipandbunker.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Port Name (DB) -> URL Path
        port_urls = {
            # International
            "Singapore": "/prices/apac/sea/sg-sin-singapore",
            "Rotterdam": "/prices/emea/nwe/nl-rtm-rotterdam",
            "Hong Kong": "/prices/apac/ea/cn-hok-hong-kong",
            "New York": "/prices/am/namatl/us-nyc-new-york",
            "Los Angeles": "/prices/am/nampac/us-lax-la-long-beach",
            "Ho Chi Minh": "/prices/apac/sea/vn-sgn-ho-chi-minh-city",
            "Dubai": "/prices/emea/me/ae-fjr-fujairah", # Mapping Dubai to Fujairah
            "Fujairah": "/prices/emea/me/ae-fjr-fujairah", # Explicit Fujairah
            "Mumbai": "/prices/apac/isc/in-bom-mumbai",
            "Chittagong": "/prices/apac/isc/bd-cgp-chittagong",
            "Hamburg": "/prices/emea/nwe/de-ham-hamburg",
            
            # E-Ports Additions
            "Piraeus": "/prices/emea/med/gr-pir-piraeus",
            "St. Petersburg": "/prices/emea/nwe/ru-led-st-petersburg",
            "Istanbul": "/prices/emea/med/tr-ist-istanbul",
            "Houston": "/prices/am/gulf/us-hou-houston",
            "Antwerp": "/prices/emea/nwe/be-ant-antwerp",
            "Balboa": "/prices/am/panama/pa-pba-balboa",
            "Santos": "/prices/am/samerica/br-ssz-santos",
            "Gibraltar": "/prices/emea/med/gi-gib-gibraltar",
            "Suez": "/prices/emea/me/eg-suz-suez",
            "Durban": "/prices/emea/afr/za-dur-durban",
            "Tokyo": "/prices/apac/ea/jp-tyo-tokyo",
            "Osaka": "/prices/apac/ea/jp-osa-osaka",
            "Busan": "/prices/apac/ea/kr-pus-busan",
            "Kaohsiung": "/prices/apac/ea/tw-khh-kaohsiung",
            
            # Domestic (Major ones found on S&B)
            "Shanghai": "/prices/apac/ea/cn-sha-shanghai",
            "Zhoushan": "/prices/apac/ea/cn-zos-zhoushan",
            "Dalian": "/prices/apac/ea/cn-dlc-dalian",
            "Qingdao": "/prices/apac/ea/cn-tao-qingdao",
            "Tianjin": "/prices/apac/ea/cn-tsn-tianjin",
            "Guangzhou": "/prices/apac/ea/cn-can-guangzhou",
            "Xiamen": "/prices/apac/ea/cn-xmn-xiamen",
        }

        # Exchange rate (USD -> CNY)
        # In a real app, fetch this dynamically. For now, use a realistic estimate.
        USD_TO_CNY = Decimal('7.25')

        today = timezone.now().date()
        self.stdout.write(f"Starting crawl for {today}...")

        for port_name, path in port_urls.items():
            url = base_url + path
            self.stdout.write(f"Fetching {port_name} from {url}...")
            
            try:
                # Find port in DB
                try:
                    port = Port.objects.get(name_en=port_name)
                except Port.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Port {port_name} not found in DB. Skipping."))
                    continue

                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"Failed to fetch {url}: {response.status_code}"))
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Strategy: Look for tables with class 'price-table' and fuel type class
                # 'VLSFO', 'MGO', 'LSMGO'
                
                fuels_to_find = ['VLSFO', 'MGO', 'LSMGO']
                found_fuels = set()
                
                tables = soup.find_all('table')
                
                for table in tables:
                    classes = table.get('class', [])
                    if not classes: continue
                    
                    fuel_type = None
                    if 'VLSFO' in classes:
                        fuel_type = 'VLSFO'
                    elif 'MGO' in classes or 'LSMGO' in classes:
                        fuel_type = 'MGO'
                    
                    if not fuel_type: continue
                    if fuel_type in found_fuels: continue # Already found this fuel (e.g. MGO vs LSMGO preference)

                    # Parse the first data row (assuming historical table sorted by date descending)
                    rows = table.find_all('tr')
                    if len(rows) < 2: continue # Header + at least 1 data row
                    
                    # Row 0 is header usually, Row 1 is latest data
                    # Verify header to be sure? 
                    # Usually headers are: Date, Price $/mt, Change, High, Low, Spread
                    
                    data_row = rows[1]
                    cols = data_row.find_all(['td', 'th'])
                    data = [c.get_text(strip=True) for c in cols]
                    
                    if len(data) < 3: continue
                    
                    # Date is col 0, Price is col 1, Change is col 2
                    price_raw = data[1]
                    change_raw = data[2]
                    
                    try:
                        # Remove '$', commas, spaces
                        price_clean = re.sub(r'[^\d.]', '', price_raw)
                        if not price_clean: continue
                        price = Decimal(price_clean)
                        
                        # Parse Change
                        change_clean = re.sub(r'[^\d.-]', '', change_raw)
                        if not change_clean or change_clean == '-' or change_clean == '':
                            change = Decimal(0)
                        else:
                            change = Decimal(change_clean)
                            
                        # Handle Currency conversion for Domestic ports
                        currency = 'USD'
                        # Assume Chinese ports in S&B are USD bonded prices, but user wants Domestic CNY?
                        # If we convert USD -> CNY, it's an estimate.
                        # User asked for "Domestic ports" and "International ports".
                        # For now, let's keep it as USD for International, and Convert for Domestic.
                        if port.country_en == 'China':
                             price = price * USD_TO_CNY
                             change = change * USD_TO_CNY
                             currency = 'CNY'
                        
                        # Save to DB
                        BunkerPrice.objects.update_or_create(
                            port=port,
                            date=today,
                            fuel_type=fuel_type,
                            defaults={
                                'price': round(price, 2),
                                'currency': currency,
                                'change': round(change, 2),
                                'source': 'Ship & Bunker'
                            }
                        )
                        self.stdout.write(f"  Saved {fuel_type}: {price} {currency} ({change})")
                        found_fuels.add(fuel_type)

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Error parsing {fuel_type} data {data}: {e}"))
                
                if not found_fuels:
                     self.stdout.write(self.style.WARNING(f"No fuel data found for {port_name}."))

                time.sleep(1) # Be polite

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {port_name}: {e}"))
                traceback.print_exc()

        self.stdout.write(self.style.SUCCESS("Crawl completed."))
