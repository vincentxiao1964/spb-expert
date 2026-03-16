import os
import django
import sys

# Add project root and apps to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'apps'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spb_expert.settings')
django.setup()

from market.models import MarketNews

exists = MarketNews.objects.filter(title__icontains='ZPMC').exists()
print(f"ZPMC News Exists: {exists}")
if exists:
    news = MarketNews.objects.get(title__icontains='ZPMC')
    print(f"ID: {news.id}, Title: {news.title}, User: {news.user.username}")
