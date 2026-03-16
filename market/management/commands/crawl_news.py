import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from market.models import MarketNews
from django.contrib.auth import get_user_model
import random
import datetime
from django.utils import timezone
import time
import os
from serpapi import GoogleSearch
import dateparser
try:
    from volcenginesdkarkruntime import Ark
    HAS_ARK = True
except Exception:
    HAS_ARK = False

User = get_user_model()

class Command(BaseCommand):
    help = 'Crawls specific market news (Self-Propelled Barges) from simulated external sources or SerpApi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with simulated data',
        )

    def summarize_text(self, text):
        """
        Summarize text using Doubao Ark if available and ENDPOINT_ID provided.
        Fallback to original text snippet on failure.
        """
        endpoint_id = os.getenv('ENDPOINT_ID', '').strip()
        api_key = os.getenv('ARK_API_KEY', '').strip()
        if not text:
            return ''
        if endpoint_id and api_key and HAS_ARK:
            try:
                client = Ark(api_key=api_key)
                prompt = (
                    "请用中文和英文各约60字对下面内容做资讯摘要，突出与自航驳船/甲板船相关要点：\n\n"
                    f"{text}"
                )
                result = client.run(endpoint_id=endpoint_id, input=prompt)
                # result 可能是 dict 或字符串，这里统一取文本
                if isinstance(result, dict):
                    out = result.get('output_text') or result.get('output') or ''
                else:
                    out = str(result)
                if out.strip():
                    return out.strip()
            except Exception:
                pass
        # Try HTTP OpenAI-compatible API
        if endpoint_id and api_key:
            try:
                url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
                prompt = (
                    "请用中文和英文各约60字对下面内容做资讯摘要，突出与自航驳船/甲板船相关要点：\n\n"
                    f"{text}"
                )
                payload = {
                    "model": endpoint_id,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices") or []
                    if choices:
                        msg = choices[0].get("message") or {}
                        content = msg.get("content") or ""
                        if isinstance(content, str) and content.strip():
                            return content.strip()
                # If non-200 or empty, fall through
            except Exception:
                pass
        return text

    def handle(self, *args, **options):
        self.stdout.write('Starting specialized news crawler for "Self-Propelled Barges"...')
        
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR('No superuser found. Please create one first.'))
            return

        if options['demo']:
            self.crawl_simulated_search(user)
        else:
            # Check for SerpApi Key
            serpapi_key = os.getenv('SERPAPI_KEY')
            if serpapi_key:
                self.crawl_serpapi(user, serpapi_key)
            else:
                self.stdout.write(self.style.WARNING('SERPAPI_KEY not found in .env. Running advanced simulation...'))
                self.crawl_simulated_search(user)

    def crawl_serpapi(self, user, api_key):
        """
        Uses SerpApi to search Google (International) and Baidu (Domestic).
        """
        self.stdout.write('Connecting to SerpApi (Google & Baidu)...')
        
        # Define search configurations
        searches = [
            {
                'engine': 'google',
                'q': 'Self-Propelled Barge',
                'location': 'United States', # or global
                'hl': 'en',
                'gl': 'us',
                'tbm': 'nws', # News tab
                'label': 'International (Google)'
            },
            {
                'engine': 'baidu',
                'q': '自航驳船',
                'rn': 10, # Number of results
                'ct': 1, # News
                'label': 'Domestic (Baidu)'
            }
        ]
        
        count = 0
        three_days_ago = timezone.now() - datetime.timedelta(days=3)

        for search_config in searches:
            self.stdout.write(f"Searching: {search_config['label']} for '{search_config['q']}'")
            
            try:
                params = search_config.copy()
                del params['label'] # Remove internal label
                params['api_key'] = api_key
                
                search = GoogleSearch(params)
                results = search.get_dict()
                
                news_results = []
                
                # Handle Google News Results
                if search_config['engine'] == 'google' and 'news_results' in results:
                    news_results = results['news_results']
                # Handle Baidu Results (structure differs)
                elif search_config['engine'] == 'baidu' and 'organic_results' in results:
                    news_results = results['organic_results']
                
                if not news_results:
                    self.stdout.write(self.style.WARNING(f"No results found for {search_config['label']}"))
                    continue

                for item in news_results:
                    # Extract fields based on engine
                    if search_config['engine'] == 'google':
                        title = item.get('title')
                        link = item.get('link')
                        snippet = item.get('snippet', 'No summary available.')
                        
                        source_obj = item.get('source', {})
                        if isinstance(source_obj, dict):
                            source = source_obj.get('title', 'Google News')
                        else:
                            source = str(source_obj)

                        date_str = item.get('date', '') # e.g. "1 day ago", "Feb 5, 2026"
                        
                        if date_str:
                            pub_date = dateparser.parse(date_str)
                            if not pub_date:
                                # Fallback if parsing fails
                                pub_date = timezone.now()
                            elif timezone.is_naive(pub_date):
                                pub_date = timezone.make_aware(pub_date)
                        else:
                            # If no date string provided by API, we can't strictly filter
                            # But since we requested news, it's likely recent.
                            # We'll default to now() but maybe log a warning.
                            pub_date = timezone.now()
                        
                    elif search_config['engine'] == 'baidu':
                        title = item.get('title')
                        link = item.get('link')
                        snippet = item.get('snippet', 'No summary available.')
                        source = 'Baidu Search' # Baidu JSON often doesn't isolate source name easily in all result types
                        
                        # Baidu results might not have a clean 'date' field in the same way
                        # We try to find it, but if not, we default to now()
                        date_str = item.get('date', '')
                        if date_str:
                            pub_date = dateparser.parse(date_str)
                            if not pub_date:
                                pub_date = timezone.now()
                            elif timezone.is_naive(pub_date):
                                pub_date = timezone.make_aware(pub_date)
                        else:
                            pub_date = timezone.now() # Placeholder

                    # Basic validation
                    if not title or not link:
                        continue
                    
                    # 1. Date Filter (Last 3 days)
                    # Note: three_days_ago is aware datetime
                    if pub_date < three_days_ago:
                        self.stdout.write(self.style.NOTICE(f"Skipping old article: {title} ({pub_date.date()})"))
                        continue

                    # 2. Duplicate Check
                    if MarketNews.objects.filter(title=title).exists():
                        self.stdout.write(f"Skipping duplicate: {title}")
                        continue
                    
                    # 2. Summarization (Upgraded to Full Content)
                    self.stdout.write(f"  Fetching full content from: {link[:50]}...")
                    full_text = self.fetch_real_content(link)
                    
                    # Use full text if available and long enough, otherwise fallback to snippet
                    # Truncate to avoid context limit if very large (Doubao has limit)
                    if full_text and len(full_text) > 100:
                        text_to_summarize = full_text[:10000] 
                    else:
                        text_to_summarize = snippet
                        
                    summary = self.summarize_text(text_to_summarize)
                    
                    final_content = (
                        f"【摘要/Summary】\n{summary}\n\n"
                        f"【原文链接/Source Link】\n{link}\n\n"
                        f"【来源/Source】\n{source}\n"
                        f"【抓取时间/Crawled Time】\n{timezone.now().strftime('%Y-%m-%d %H:%M')}"
                    )
                    
                    # 3. Save
                    MarketNews.objects.create(
                        user=user,
                        title=title,
                        content=final_content,
                        source_url=link,
                        original_source=source,
                        status=MarketNews.Status.PENDING
                    )
                    self.stdout.write(self.style.SUCCESS(f"Fetched: {title}"))
                    count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error searching {search_config['label']}: {e}"))

        self.stdout.write(self.style.SUCCESS(f'--------------------------------------------------'))
        self.stdout.write(self.style.SUCCESS(f'Task Completed: Added {count} new articles via SerpApi.'))

    def crawl_simulated_search(self, user):
        """
        Simulates the result of searching for 'Self-Propelled Barge' and '自航驳船' 
        over the last 3 days.
        """
        self.stdout.write('Searching for "Self-Propelled Barge" (International) & "自航驳船" (Domestic)...')
        self.stdout.write('Filtering results: Last 3 days only...')
        
        # Simulated "Fresh" Results (Last 3 Days)
        # In a real scenario, these would come from parsing search result pages or API responses
        fresh_results = [
            {
                'title': 'Europe Inland Shipping: New Hybrid Self-Propelled Barges Launching in Rotterdam',
                'summary': 'A consortium of Dutch shipbuilders has announced the launch of 5 new hybrid self-propelled barges designed for the Rhine corridor. These vessels promise 30% fuel reduction.',
                'link': 'https://www.inland-navigation-news-example.com/2026/02/04/new-hybrid-barges',
                'source': 'Inland Nav News',
                'lang': 'en',
                'date': timezone.now() - datetime.timedelta(days=1)
            },
            {
                'title': '长江中游自航驳船运输效率提升方案发布',
                'summary': '交通运输部发布最新指导意见，旨在提升长江中游自航驳船的周转效率。新方案强调了数字化调度系统的应用，预计将平均航次时间缩短15%。',
                'link': 'https://www.shipping-cn-example.com/news/20260205/changjiang-barge',
                'source': '中国航运网',
                'lang': 'zh',
                'date': timezone.now() - datetime.timedelta(hours=5)
            },
            {
                'title': 'Market Report: US Jones Act Self-Propelled Barge Fleet Analysis 2026',
                'summary': 'The latest market analysis shows a tightening supply of Jones Act compliant self-propelled deck barges. Charter rates have increased by 8% Q-o-Q.',
                'link': 'https://www.us-maritime-insight-example.com/reports/jones-act-barges-2026',
                'source': 'Maritime Insight',
                'lang': 'en',
                'date': timezone.now() - datetime.timedelta(days=2)
            }
        ]

        # Simulated "Old" Results (Older than 3 Days) - Should be filtered out
        old_results = [
            {
                'title': '2025 Review of Asian Self-Propelled Barge Market',
                'summary': 'A look back at the trends that defined the barge market in 2025.',
                'link': 'https://www.asia-barge-example.com/2025-review',
                'source': 'Asia Barge News',
                'lang': 'en',
                'date': timezone.now() - datetime.timedelta(days=10)
            }
        ]

        all_candidates = fresh_results + old_results
        
        count = 0
        three_days_ago = timezone.now() - datetime.timedelta(days=3)

        for item in all_candidates:
            # 1. Date Filter
            if item['date'] < three_days_ago:
                self.stdout.write(self.style.NOTICE(f"Skipping old article: {item['title']} ({item['date'].date()})"))
                continue

            # 2. Duplicate Check
            if MarketNews.objects.filter(title=item['title']).exists():
                self.stdout.write(f"Skipping duplicate: {item['title']}")
                continue

            # 3. Summarization (Simulated)
            # In real life, we would pass 'content' to an LLM here to get a summary.
            # Here we use the simulated 'summary' field directly.
            summary = self.summarize_text(item['summary'])
            final_content = (
                f"【摘要/Summary】\n{summary}\n\n"
                f"【原文链接/Source Link】\n{item['link']}\n\n"
                f"【来源/Source】\n{item['source']}\n"
                f"【发布日期/Date】\n{item['date'].strftime('%Y-%m-%d')}"
            )

            # 4. Save to Database (Status=PENDING)
            MarketNews.objects.create(
                user=user,
                title=item['title'],
                content=final_content,
                # Save structured fields
                source_url=item['link'],
                original_source=item['source'],
                status=MarketNews.Status.PENDING # Requires Admin Approval
            )
            self.stdout.write(self.style.SUCCESS(f"Fetched & Summarized: {item['title']}"))
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'--------------------------------------------------'))
        self.stdout.write(self.style.SUCCESS(f'Task Completed: Added {count} new articles to Pending Review.'))
        self.stdout.write(self.style.SUCCESS(f'Please visit Admin Panel to review and publish.'))

    def fetch_real_content(self, url):
        """
        Helper to fetch real page content if we were doing live scraping.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
                    script.extract()
                    
                # Get text
                text = soup.get_text()
                
                # Break into lines and remove leading and trailing space on each
                lines = (line.strip() for line in text.splitlines())
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # Drop blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
            return ""
        except Exception:
            return ""
