from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import ShipListing, MarketNews

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'market:list', 'market:news_list', 'ads:ad_list', 'member_messages']

    def location(self, item):
        return reverse(item)

class ShipListingSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ShipListing.objects.filter(status='APPROVED')

    def lastmod(self, obj):
        return obj.updated_at

class MarketNewsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return MarketNews.objects.filter(status='APPROVED')

    def lastmod(self, obj):
        return obj.updated_at
