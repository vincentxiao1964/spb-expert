from django.core.management.base import BaseCommand
from tools.models import Port, BunkerPrice
from django.utils import timezone
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Initialize bunker ports and generate dummy price data for testing'

    def handle(self, *args, **options):
        # Port List (Name EN, Name ZH, Country EN, Country ZH)
        # Coordinates are approximate placeholders for initialization
        ports_data = [
            # Domestic (China)
            ("Dalian", "大连", "China", "中国", 38.9, 121.6),
            ("Qinhuangdao", "秦皇岛", "China", "中国", 39.9, 119.6),
            ("Tangshan", "唐山", "China", "中国", 39.2, 118.5),
            ("Tianjin", "天津", "China", "中国", 39.0, 117.7),
            ("Qingdao", "青岛", "China", "中国", 36.1, 120.3),
            ("Yantai", "烟台", "China", "中国", 37.5, 121.4),
            ("Lianyungang", "连云港", "China", "中国", 34.7, 119.4),
            ("Nantong", "南通", "China", "中国", 32.0, 120.8),
            ("Shanghai", "上海", "China", "中国", 31.2, 121.5),
            ("Zhoushan", "舟山", "China", "中国", 30.0, 122.2),
            ("Fuzhou", "福州", "China", "中国", 26.0, 119.5),
            ("Xiamen", "厦门", "China", "中国", 24.5, 118.1),
            ("Guangzhou", "广州", "China", "中国", 23.1, 113.3),
            ("Shenzhen", "深圳", "China", "中国", 22.5, 114.1),
            ("Haikou", "海口", "China", "中国", 20.0, 110.3),
            ("Sanya", "三亚", "China", "中国", 18.2, 109.5),
            ("Beihai", "北海", "China", "中国", 21.5, 109.1),
            ("Fangcheng", "防城", "China", "中国", 21.6, 108.3),
            ("Qinzhou", "钦州", "China", "中国", 21.9, 108.6),
            ("Nanjing", "南京", "China", "中国", 32.0, 118.8),
            ("Jiangyin", "江阴", "China", "中国", 31.9, 120.3),
            ("Zhangjiagang", "张家港", "China", "中国", 31.8, 120.5),
            
            # International
            ("Singapore", "新加坡", "Singapore", "新加坡", 1.3, 103.8),
            ("Dubai", "迪拜", "UAE", "阿联酋", 25.2, 55.3),
            ("Mumbai", "孟买", "India", "印度", 18.9, 72.8),
            ("Chittagong", "吉大港", "Bangladesh", "孟加拉国", 22.3, 91.8),
            ("Ho Chi Minh", "胡志明", "Vietnam", "越南", 10.8, 106.6),
            ("London", "伦敦", "UK", "英国", 51.5, 0.0),
            ("Rotterdam", "鹿特丹", "Netherlands", "荷兰", 51.9, 4.5),
            ("Hamburg", "汉堡", "Germany", "德国", 53.5, 10.0),
            ("Los Angeles", "洛杉矶", "USA", "美国", 33.7, -118.2),
            ("New York", "纽约", "USA", "美国", 40.7, -74.0),
        ]

        created_count = 0
        for p_en, p_zh, c_en, c_zh, lat, lon in ports_data:
            port, created = Port.objects.get_or_create(
                name_en=p_en,
                defaults={
                    'name_zh': p_zh,
                    'country_en': c_en,
                    'country_zh': c_zh,
                    'latitude': lat,
                    'longitude': lon
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created port: {p_en}"))
            else:
                # Update Chinese name if missing
                if not port.name_zh:
                    port.name_zh = p_zh
                    port.save()

        self.stdout.write(self.style.SUCCESS(f"Total ports created: {created_count}"))

        # Generate dummy prices for today if not exist
        today = timezone.now().date()
        # Optional: Clear today's existing prices to avoid duplicates or mixed types during development
        BunkerPrice.objects.filter(date=today).delete()
        
        price_count = 0
        
        for p_en, _, c_en, _, _, _ in ports_data:
            port = Port.objects.get(name_en=p_en)
            
            # Decide currency and base price
            is_domestic = (c_en == 'China')
            currency = 'CNY' if is_domestic else 'USD'
            
            if is_domestic:
                # Domestic: RME180 and DIESEL0 (0# Diesel)
                # RME180 ~4100 CNY, 0# Diesel ~7200 CNY
                base_heavy = Decimal(4100)
                base_light = Decimal(7200)
                type_heavy = 'RME180'
                type_light = 'DIESEL0'
            else:
                # International: VLSFO and MGO
                # VLSFO ~620 USD, MGO ~780 USD
                base_heavy = Decimal(620)
                base_light = Decimal(780)
                type_heavy = 'VLSFO'
                type_light = 'MGO'
            
            # Random variation
            price_heavy = base_heavy + Decimal(random.uniform(-50, 50))
            price_light = base_light + Decimal(random.uniform(-50, 50))
            
            # Heavy Fuel (VLSFO or RME180)
            _, created = BunkerPrice.objects.get_or_create(
                port=port,
                date=today,
                fuel_type=type_heavy,
                defaults={
                    'price': round(price_heavy, 2),
                    'currency': currency,
                    'change': round(Decimal(random.uniform(-10, 10)), 2),
                    'source': 'Estimated'
                }
            )
            if created: price_count += 1

            # Light Fuel (MGO or Diesel0)
            _, created = BunkerPrice.objects.get_or_create(
                port=port,
                date=today,
                fuel_type=type_light,
                defaults={
                    'price': round(price_light, 2),
                    'currency': currency,
                    'change': round(Decimal(random.uniform(-10, 10)), 2),
                    'source': 'Estimated'
                }
            )
            if created: price_count += 1

        self.stdout.write(self.style.SUCCESS(f"Generated {price_count} dummy price records for {today}"))
