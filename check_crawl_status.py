
import os
import django
import sys

# Add project root to path
sys.path.append('d:\\spb-expert9')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spb_expert.settings')
django.setup()

from market.models import MarketNews, CrawledShip
from django.utils import timezone

print("--- MarketNews Status ---")
recent_news = MarketNews.objects.order_by('-created_at')[:5]
if recent_news:
    for news in recent_news:
        print(f"[{news.created_at.strftime('%Y-%m-%d %H:%M')}] {news.title} (Status: {news.status})")
else:
    print("No MarketNews found.")

print("\n--- CrawledShip Status ---")
recent_ships = CrawledShip.objects.order_by('-created_at')[:5]
if recent_ships:
    for ship in recent_ships:
        print(f"[{ship.created_at.strftime('%Y-%m-%d %H:%M')}] {ship.source} - {ship.source_id} (DWT: {ship.dwt})")
else:
    print("No CrawledShip found.")
