from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from market.models import CrawledShip, MarketNews, DailyBriefing
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generates a daily market briefing from crawled data'

    def handle(self, *args, **options):
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        
        # 1. Fetch new ships from last 24h
        new_ships = CrawledShip.objects.filter(crawled_at__gte=yesterday).order_by('source', '-crawled_at')
        
        # 2. Fetch new market news
        new_news = MarketNews.objects.filter(created_at__gte=yesterday).order_by('-created_at')
        
        # Generate Report Text
        report_lines = []
        # No header in DB content to keep it clean, or keep it? Let's keep it simple.
        # But for display, maybe we want HTML? For now, text is fine.
        
        report_lines.append(f"🚢 每日船舶市场简报 / Daily Ship Market Briefing")
        report_lines.append(f"📅 {now.strftime('%Y-%m-%d %H:%M')}")
        report_lines.append("=" * 40)
        report_lines.append("")
        
        # --- Ships Section ---
        if new_ships.exists():
            report_lines.append(f"🔥 新增船舶信息 ({new_ships.count()} 条)")
            
            # Group by source
            ships_by_source = {}
            for ship in new_ships:
                if ship.source not in ships_by_source:
                    ships_by_source[ship.source] = []
                ships_by_source[ship.source].append(ship)
                
            for source, ships in ships_by_source.items():
                source_name = source.upper()
                report_lines.append(f"\n[{source_name}]")
                for i, ship in enumerate(ships, 1):
                    # Try to format details: DWT, Year, Location
                    details = []
                    if ship.dwt: details.append(f"{ship.dwt} DWT")
                    if ship.build_year: details.append(f"Built {ship.build_year}")
                    if ship.ship_category: details.append(ship.ship_category)
                    
                    details_str = ", ".join(details)
                    report_lines.append(f"{i}. {details_str}")
                    report_lines.append(f"   🔗 {ship.source_url}")
                    if ship.full_description:
                        # Truncate description for brevity
                        desc_preview = ship.full_description.split('\n')[0][:50]
                        if desc_preview:
                            report_lines.append(f"   ℹ️ {desc_preview}...")
        else:
            report_lines.append("ℹ️ 过去24小时无新增船舶信息。")
            
        report_lines.append("")
        
        # --- News Section ---
        if new_news.exists():
            report_lines.append(f"📰 市场新闻 ({new_news.count()} 条)")
            for i, news in enumerate(new_news, 1):
                report_lines.append(f"{i}. {news.title}")
                if news.source_url:
                    report_lines.append(f"   🔗 {news.source_url}")
        else:
            report_lines.append("ℹ️ 过去24小时无新增市场新闻。")
            
        report_lines.append("")
        report_lines.append("=" * 40)
        report_lines.append("🤖 生成自 SPB Expert 智能助手")
        
        full_report = "\n".join(report_lines)
        
        # Output to stdout (logs)
        self.stdout.write(full_report)
        
        # Save to DB
        try:
            DailyBriefing.objects.create(
                content=full_report,
                status=DailyBriefing.Status.DRAFT # Default to Draft for review
            )
            self.stdout.write(self.style.SUCCESS(f"\nBriefing saved to Database (Status: Draft)"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not save briefing to DB: {e}"))

        # Optional: Save to a log file specifically for briefings
        try:
            log_dir = settings.BASE_DIR / 'logs' / 'briefings'
            log_dir.mkdir(parents=True, exist_ok=True)
            filename = f"briefing_{now.strftime('%Y%m%d')}.txt"
            with open(log_dir / filename, 'w', encoding='utf-8') as f:
                f.write(full_report)
            self.stdout.write(self.style.SUCCESS(f"\nBriefing saved to {log_dir / filename}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not save briefing to file: {e}"))

