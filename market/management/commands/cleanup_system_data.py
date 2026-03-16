import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from market.models import CrawledShip, DailyBriefing, MarketNews
from users.models import VisitorLog

class Command(BaseCommand):
    help = 'Cleans up old system data to free up storage space.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--crawled-ships-days',
            type=int,
            default=90,
            help='Retention days for Crawled Ships (default: 90)'
        )
        parser.add_argument(
            '--briefings-days',
            type=int,
            default=365,
            help='Retention days for Daily Briefings (default: 365)'
        )
        parser.add_argument(
            '--crawled-news-days',
            type=int,
            default=180,
            help='Retention days for Crawled Market News (default: 180)'
        )
        parser.add_argument(
            '--visitor-logs-days',
            type=int,
            default=30,
            help='Retention days for Visitor Logs (default: 30)'
        )

    def handle(self, *args, **options):
        now = timezone.now()
        
        # 1. Cleanup Crawled Ships
        days_ships = options['crawled_ships_days']
        cutoff_ships = now - timedelta(days=days_ships)
        count_ships, _ = CrawledShip.objects.filter(crawled_at__lt=cutoff_ships).delete()
        self.stdout.write(f"Deleted {count_ships} CrawledShip entries older than {days_ships} days.")

        # 2. Cleanup Daily Briefings
        days_briefings = options['briefings_days']
        cutoff_briefings = now - timedelta(days=days_briefings)
        count_briefings, _ = DailyBriefing.objects.filter(created_at__lt=cutoff_briefings).delete()
        self.stdout.write(f"Deleted {count_briefings} DailyBriefing entries older than {days_briefings} days.")

        # 3. Cleanup Crawled Market News
        # Identify crawled news by having a source_url or original_source
        days_news = options['crawled_news_days']
        cutoff_news = now - timedelta(days=days_news)
        count_news, _ = MarketNews.objects.filter(
            created_at__lt=cutoff_news
        ).exclude(original_source='').delete() # Only delete news with an original source (crawled)
        self.stdout.write(f"Deleted {count_news} crawled MarketNews entries older than {days_news} days.")

        # 4. Cleanup Visitor Logs (Consolidated here)
        days_logs = options['visitor_logs_days']
        cutoff_logs = now - timedelta(days=days_logs)
        count_logs, _ = VisitorLog.objects.filter(created_at__lt=cutoff_logs).delete()
        self.stdout.write(f"Deleted {count_logs} VisitorLog entries older than {days_logs} days.")

        self.stdout.write(self.style.SUCCESS("System data cleanup completed."))
